"""Aula 25: arquitetura integrada do Lakehouse Minishop.

OLTP -> Bronze -> Silver -> Gold analitica -> DuckDB.
                     |
                     +-> ETL -> DW dimensional.

O Lakehouse consulta o proprio Parquet da Gold,
sem criar uma copia exclusiva para o motor SQL.
"""

import json
import os
import shutil
import sqlite3
import tempfile

from contextlib import closing
from pathlib import Path

import duckdb

from src.aula17_data_lake import hash_arquivo
from src.aula20_data_lake_minishop import (
    ler_silver,
    ler_jsonl,
    validar_camada,
)
from src.aula22_arquitetura_lakehouse import executar as executar_aula22


BASE = Path(__file__).resolve().parent.parent
LAKE = BASE / "dados" / "lake"

SCHEMA_VENDAS = [
    ("pedido_id", "BIGINT"),
    ("cliente_id", "BIGINT"),
    ("cliente_nome", "VARCHAR"),
    ("produto_id", "BIGINT"),
    ("produto_nome", "VARCHAR"),
    ("categoria_nome", "VARCHAR"),
    ("data", "VARCHAR"),
    ("quantidade", "BIGINT"),
    ("valor_total_centavos", "BIGINT"),
]

SCHEMA_MENSAL = [
    ("periodo", "VARCHAR"),
    ("pedidos", "BIGINT"),
    ("itens", "BIGINT"),
    ("unidades", "BIGINT"),
    ("faturamento_centavos", "BIGINT"),
]

TABELAS = {
    "vendas_enriquecidas": SCHEMA_VENDAS,
    "indicadores_mensais": SCHEMA_MENSAL,
}


def sql_literal(valor):
    return "'" + str(valor).replace("'", "''") + "'"


def gravar_json(caminho, dados):
    Path(caminho).write_text(
        json.dumps(
            dados, ensure_ascii=False, indent=2, sort_keys=True
        ) + "\n",
        encoding="utf-8",
    )


def ler_json(caminho):
    return json.loads(
        Path(caminho).read_text(encoding="utf-8")
    )


def gerar_vendas_enriquecidas(silver):
    """Enriquece vendas somente com dados existentes na Silver."""
    dados = ler_silver(silver)

    clientes = {
        x["cliente_id"]: x
        for x in dados["clientes"]
    }

    produtos = {
        x["produto_id"]: x
        for x in dados["produtos"]
    }

    vendas = []
    chaves = set()

    for venda in dados["vendas"]:
        cliente = clientes.get(venda["cliente_id"])
        produto = produtos.get(venda["produto_id"])

        if cliente is None or produto is None:
            raise ValueError(
                "Venda sem cliente ou produto cadastrado"
            )

        chave = (
            venda["pedido_id"],
            venda["produto_id"],
        )

        if chave in chaves:
            raise ValueError("Venda duplicada na Silver")

        chaves.add(chave)

        quantidade = venda["quantidade"]
        valor = venda["valor_total_centavos"]
        unitario = venda["preco_unitario_centavos"]

        if (
            quantidade <= 0
            or valor < 0
            or valor != quantidade * unitario
        ):
            raise ValueError("Venda com medidas invalidas")

        vendas.append({
            "pedido_id": venda["pedido_id"],
            "cliente_id": venda["cliente_id"],
            "cliente_nome": cliente["nome"],
            "produto_id": venda["produto_id"],
            "produto_nome": produto["produto_nome"],
            "categoria_nome": produto["categoria_nome"],
            "data": venda["data"],
            "quantidade": quantidade,
            "valor_total_centavos": valor,
        })

    return sorted(
        vendas,
        key=lambda x: (x["pedido_id"], x["produto_id"]),
    )


def criar_parquet(con, caminho, esquema, registros):
    """Materializa uma tabela Gold em Parquet real."""
    definicoes = ", ".join(
        f'"{nome}" {tipo}'
        for nome, tipo in esquema
    )

    con.execute(
        f"CREATE OR REPLACE TABLE staging ({definicoes})"
    )

    if registros:
        colunas = [nome for nome, _ in esquema]

        valores = [
            tuple(registro[coluna] for coluna in colunas)
            for registro in registros
        ]

        placeholders = ",".join("?" for _ in esquema)

        con.executemany(
            f"INSERT INTO staging VALUES ({placeholders})",
            valores,
        )

    con.execute(
        f"COPY staging TO {sql_literal(Path(caminho).as_posix())} "
        "(FORMAT PARQUET, COMPRESSION SNAPPY)"
    )

    with Path(caminho).open("rb") as arquivo:
        if arquivo.read(4) != b"PAR1":
            raise ValueError("Parquet invalido")


def validar_gold_analitica(pasta):
    pasta = Path(pasta)
    catalogo = ler_json(pasta / "catalogo.json")
    manifesto = ler_json(pasta / "manifest.json")

    if (
        catalogo.get("snapshot_id") != pasta.name
        or manifesto.get("snapshot_id") != pasta.name
        or manifesto.get("camada") != "gold_analitica"
    ):
        raise ValueError("Snapshot Gold inconsistente")

    if set(catalogo["tabelas"]) != set(TABELAS):
        raise ValueError("Catalogo incompleto")

    esperados = {
        "catalogo.json",
        *(f"{nome}.parquet" for nome in TABELAS),
    }

    if set(manifesto["arquivos"]) != esperados:
        raise ValueError("Manifesto incompleto")

    for nome, esperado in manifesto["arquivos"].items():
        arquivo = pasta / nome

        if (
            not arquivo.is_file()
            or hash_arquivo(arquivo) != esperado
        ):
            raise ValueError(
                "Integridade comprometida: " + nome
            )

    for nome, esquema in TABELAS.items():
        definicao = catalogo["tabelas"][nome]

        if definicao["arquivo"] != f"{nome}.parquet":
            raise ValueError("Localizacao de tabela incorreta")

        if definicao["colunas"] != [
            {"nome": n, "tipo": t}
            for n, t in esquema
        ]:
            raise ValueError("Esquema incorreto")

    return catalogo


def criar_gold_analitica(silver, gold_original, lake=LAKE):
    """Cria datasets Gold, sem alterar a Gold das aulas anteriores."""
    meta_silver = validar_camada(silver, "silver")
    meta_gold = validar_camada(gold_original, "gold")

    snapshot = meta_silver["snapshot_id"]

    if meta_gold["snapshot_id"] != snapshot:
        raise ValueError("Gold e Silver de snapshots diferentes")

    destino = (
        Path(lake) / "gold_analitica" / "minishop" / snapshot
    )

    destino.parent.mkdir(parents=True, exist_ok=True)

    if destino.exists():
        validar_gold_analitica(destino)
        return destino

    vendas = gerar_vendas_enriquecidas(silver)
    mensal = ler_jsonl(
        Path(gold_original) / "indicadores_mensais.jsonl"
    )

    soma_vendas = sum(
        x["valor_total_centavos"] for x in vendas
    )

    soma_mensal = sum(
        x["faturamento_centavos"] for x in mensal
    )

    if soma_vendas != soma_mensal:
        raise ValueError(
            "Silver enriquecida e Gold mensal divergentes"
        )

    temporaria = Path(tempfile.mkdtemp(
        prefix=".aula25_",
        dir=destino.parent,
    ))

    try:
        con = duckdb.connect(":memory:")

        try:
            criar_parquet(
                con,
                temporaria / "vendas_enriquecidas.parquet",
                SCHEMA_VENDAS,
                vendas,
            )

            criar_parquet(
                con,
                temporaria / "indicadores_mensais.parquet",
                SCHEMA_MENSAL,
                mensal,
            )
        finally:
            con.close()

        catalogo = {
            "snapshot_id": snapshot,
            "formato": "Parquet",
            "origem": "Silver e Gold da Minishop",
            "motor_consulta": "DuckDB",
            "tabelas": {
                nome: {
                    "arquivo": f"{nome}.parquet",
                    "colunas": [
                        {"nome": n, "tipo": t}
                        for n, t in esquema
                    ],
                }
                for nome, esquema in TABELAS.items()
            },
        }

        gravar_json(
            temporaria / "catalogo.json",
            catalogo,
        )

        arquivos = [
            "catalogo.json",
            *(f"{nome}.parquet" for nome in TABELAS),
        ]

        gravar_json(
            temporaria / "manifest.json",
            {
                "camada": "gold_analitica",
                "snapshot_id": snapshot,
                "arquivos": {
                    nome: hash_arquivo(temporaria / nome)
                    for nome in arquivos
                },
            },
        )

        os.rename(temporaria, destino)

    finally:
        if temporaria.exists():
            shutil.rmtree(temporaria)

    validar_gold_analitica(destino)
    return destino


def consultar_lakehouse(pasta, consulta, parametros=()):
    """Executa SELECT sobre os arquivos fisicos da Gold."""
    catalogo = validar_gold_analitica(pasta)

    comando = consulta.strip()

    if not comando or comando.split(None, 1)[0].upper() != "SELECT":
        raise ValueError("Apenas consultas SELECT sao permitidas")

    if ";" in comando.rstrip(";"):
        raise ValueError("Multiplas instrucoes SQL nao permitidas")

    con = duckdb.connect(":memory:")

    try:
        for tabela, definicao in catalogo["tabelas"].items():
            arquivo = (
                Path(pasta) / definicao["arquivo"]
            ).resolve()

            con.execute(
                f"CREATE VIEW {tabela} AS "
                f"SELECT * FROM read_parquet("
                f"{sql_literal(arquivo.as_posix())})"
            )

        resultado = con.execute(
            comando, list(parametros)
        )

        colunas = [
            x[0] for x in resultado.description
        ]

        return [
            dict(zip(colunas, linha))
            for linha in resultado.fetchall()
        ]
    finally:
        con.close()


def indicadores_lakehouse(pasta):
    return consultar_lakehouse(
        pasta,
        """
        SELECT
            COUNT(*) AS linhas_vendas,
            COALESCE(SUM(quantidade), 0) AS unidades,
            COALESCE(SUM(valor_total_centavos), 0)
                AS faturamento_centavos,
            COUNT(DISTINCT pedido_id) AS pedidos
        FROM vendas_enriquecidas
        """,
    )[0]


def vendas_por_categoria(pasta):
    return consultar_lakehouse(
        pasta,
        """
        SELECT categoria_nome,
               SUM(quantidade) AS unidades,
               SUM(valor_total_centavos)
                   AS faturamento_centavos
        FROM vendas_enriquecidas
        GROUP BY categoria_nome
        ORDER BY categoria_nome
        """,
    )


def carregar_dw_dimensional(silver, lake=LAKE):
    """ETL Silver -> DW, sem usar o arquivo Parquet da Gold."""
    meta = validar_camada(silver, "silver")
    snapshot = meta["snapshot_id"]

    destino = (
        Path(lake) / "dw_integrado" / "minishop"
        / snapshot / "dw.sqlite"
    )

    destino.parent.mkdir(parents=True, exist_ok=True)

    if destino.exists():
        return destino

    vendas = gerar_vendas_enriquecidas(silver)

    clientes = sorted({
        (v["cliente_id"], v["cliente_nome"])
        for v in vendas
    })

    produtos = sorted({
        (
            v["produto_id"],
            v["produto_nome"],
            v["categoria_nome"],
        )
        for v in vendas
    })

    mapa_clientes = {
        cid: i
        for i, (cid, _) in enumerate(clientes, 1)
    }

    mapa_produtos = {
        pid: i
        for i, (pid, _, _) in enumerate(produtos, 1)
    }

    temporario = destino.with_suffix(".tmp.sqlite")

    if temporario.exists():
        temporario.unlink()

    try:
        with closing(sqlite3.connect(temporario)) as con:
            con.execute("PRAGMA foreign_keys = ON")

            con.executescript(
                """
                CREATE TABLE dim_cliente (
                    sk_cliente INTEGER PRIMARY KEY,
                    cliente_id INTEGER UNIQUE NOT NULL,
                    nome TEXT NOT NULL
                );

                CREATE TABLE dim_produto (
                    sk_produto INTEGER PRIMARY KEY,
                    produto_id INTEGER UNIQUE NOT NULL,
                    nome TEXT NOT NULL,
                    categoria TEXT NOT NULL
                );

                CREATE TABLE dim_tempo (
                    sk_tempo INTEGER PRIMARY KEY,
                    data TEXT NOT NULL,
                    mes INTEGER NOT NULL,
                    ano INTEGER NOT NULL
                );

                CREATE TABLE fato_vendas (
                    pedido_id INTEGER NOT NULL,
                    sk_cliente INTEGER NOT NULL,
                    sk_produto INTEGER NOT NULL,
                    sk_tempo INTEGER NOT NULL,
                    quantidade INTEGER NOT NULL,
                    valor_total_centavos INTEGER NOT NULL,
                    PRIMARY KEY(pedido_id, sk_produto),
                    FOREIGN KEY(sk_cliente)
                        REFERENCES dim_cliente(sk_cliente),
                    FOREIGN KEY(sk_produto)
                        REFERENCES dim_produto(sk_produto),
                    FOREIGN KEY(sk_tempo)
                        REFERENCES dim_tempo(sk_tempo)
                );
                """
            )

            con.executemany(
                "INSERT INTO dim_cliente VALUES (?,?,?)",
                [
                    (mapa_clientes[cid], cid, nome)
                    for cid, nome in clientes
                ],
            )

            con.executemany(
                "INSERT INTO dim_produto VALUES (?,?,?,?)",
                [
                    (
                        mapa_produtos[pid],
                        pid,
                        nome,
                        categoria,
                    )
                    for pid, nome, categoria in produtos
                ],
            )

            for venda in vendas:
                data = venda["data"]
                sk_tempo = int(data.replace("-", ""))

                con.execute(
                    """
                    INSERT OR IGNORE INTO dim_tempo
                    VALUES (?,?,?,?)
                    """,
                    (
                        sk_tempo,
                        data,
                        int(data[5:7]),
                        int(data[:4]),
                    ),
                )

                con.execute(
                    """
                    INSERT INTO fato_vendas
                    VALUES (?,?,?,?,?,?)
                    """,
                    (
                        venda["pedido_id"],
                        mapa_clientes[venda["cliente_id"]],
                        mapa_produtos[venda["produto_id"]],
                        sk_tempo,
                        venda["quantidade"],
                        venda["valor_total_centavos"],
                    ),
                )

            con.commit()

        os.replace(temporario, destino)

    finally:
        if temporario.exists():
            temporario.unlink()

    return destino


def indicadores_dw(banco):
    banco = Path(banco)

    if not banco.is_file():
        raise FileNotFoundError(banco)

    uri = banco.resolve().as_uri() + "?mode=ro"

    with closing(sqlite3.connect(uri, uri=True)) as con:
        linha = con.execute(
            """
            SELECT COUNT(*),
                   COALESCE(SUM(quantidade), 0),
                   COALESCE(SUM(valor_total_centavos), 0),
                   COUNT(DISTINCT pedido_id)
            FROM fato_vendas
            """
        ).fetchone()

    return dict(zip(
        (
            "linhas_vendas",
            "unidades",
            "faturamento_centavos",
            "pedidos",
        ),
        linha,
    ))


def conferir_integracao(gold_analitica, dw):
    lakehouse = indicadores_lakehouse(
        gold_analitica
    )

    warehouse = indicadores_dw(dw)

    gold_mensal = consultar_lakehouse(
        gold_analitica,
        """
        SELECT
            COALESCE(SUM(faturamento_centavos),0)
                AS faturamento_centavos,
            COALESCE(SUM(unidades),0) AS unidades
        FROM indicadores_mensais
        """,
    )[0]

    consistente = (
        lakehouse == warehouse
        and lakehouse["faturamento_centavos"]
            == gold_mensal["faturamento_centavos"]
        and lakehouse["unidades"]
            == gold_mensal["unidades"]
    )

    return {
        "consistente": consistente,
        "lakehouse": lakehouse,
        "data_warehouse": warehouse,
        "gold": gold_mensal,
    }


def executar(oltp, lake=LAKE):
    """Integra todos os componentes existentes da Minishop."""
    anterior = executar_aula22(oltp, lake)

    silver = Path(anterior["silver"]["pasta"])
    gold_original = Path(anterior["gold"]["pasta"])

    gold_analitica = criar_gold_analitica(
        silver,
        gold_original,
        lake,
    )

    dw = carregar_dw_dimensional(silver, lake)

    conciliacao = conferir_integracao(
        gold_analitica,
        dw,
    )

    if not conciliacao["consistente"]:
        raise ValueError(
            "Gold, Lakehouse e DW divergentes"
        )

    return {
        "snapshot_id": anterior["snapshot"]["snapshot_id"],
        "oltp": str(oltp),
        "bronze": anterior["bronze"]["pasta"],
        "silver": str(silver),
        "gold_original": str(gold_original),
        "gold_analitica": str(gold_analitica),
        "lakehouse_catalogo": str(
            gold_analitica / "catalogo.json"
        ),
        "data_warehouse": str(dw),
        "reconciliacao": conciliacao,
        "categorias": vendas_por_categoria(gold_analitica),
        "lakehouse_usa_arquivos_gold": True,
    }
