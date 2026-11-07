"""Aula 24 - Exemplo OLTP, Bronze, Silver, Gold, Lakehouse e DW.

Dados didaticos fornecidos na transcricao:
FAT001, FAT002, FAT003, CLI10 e CLI20.

Todos os valores financeiros sao guardados em centavos.
Nao sao dados reais do e-commerce Minishop.

Referencia padrao: 2026-01-31.
"""

import hashlib
import json
import os
import sqlite3
from contextlib import closing
from datetime import date
from pathlib import Path

import duckdb


BASE = Path(__file__).resolve().parent.parent
RAIZ = BASE / "dados" / "exemplos" / "aula24"

CLIENTES = [
    (
        "CLI10",
        "Mercado Alpha",
        "Rua F, Belo Horizonte, MG",
    ),
    (
        "CLI20",
        "Loja Beta",
        "Rua X, Campinas, SP",
    ),
]

FATURAS = [
    (
        "FAT001", "CLI10", 100000,
        "2026-01-10", "2026-01-09", 100000,
    ),
    (
        "FAT002", "CLI20", 80000,
        "2026-01-15", None, 0,
    ),
    (
        "FAT003", "CLI10", 50000,
        "2026-01-20", "2026-01-28", 50000,
    ),
]

ESQUEMA_FATURAS = [
    ("id_fatura", "VARCHAR"),
    ("id_cliente", "VARCHAR"),
    ("valor_fatura_centavos", "BIGINT"),
    ("data_vencimento", "VARCHAR"),
    ("data_pagamento", "VARCHAR"),
    ("valor_pago_centavos", "BIGINT"),
]

ESQUEMA_TRATADO = ESQUEMA_FATURAS + [
    ("nome_cliente", "VARCHAR"),
    ("cidade", "VARCHAR"),
    ("estado", "VARCHAR"),
    ("status", "VARCHAR"),
    ("atraso_pagamento_dias", "INTEGER"),
    ("dias_vencido_referencia", "INTEGER"),
    ("saldo_aberto_centavos", "BIGINT"),
]

ESQUEMA_GOLD = ESQUEMA_TRATADO + [
    ("aging", "VARCHAR"),
    ("inadimplente_atual", "BOOLEAN"),
    ("pago_com_atraso", "BOOLEAN"),
]


def arquivo_hash(caminho):
    sha = hashlib.sha256()

    with Path(caminho).open("rb") as entrada:
        for bloco in iter(
            lambda: entrada.read(1024 * 1024), b""
        ):
            sha.update(bloco)

    return sha.hexdigest()


def escrever_json(caminho, objeto):
    Path(caminho).write_text(
        json.dumps(
            objeto,
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        ) + "\n",
        encoding="utf-8",
    )


def ler_json(caminho):
    return json.loads(
        Path(caminho).read_text(encoding="utf-8")
    )


def literal_sql(valor):
    return "'" + str(valor).replace("'", "''") + "'"


def formato_data(texto):
    if not isinstance(texto, str):
        raise ValueError("Data precisa ser texto")

    try:
        resultado = date.fromisoformat(texto)
    except ValueError as erro:
        raise ValueError("Data invalida") from erro

    if resultado.isoformat() != texto:
        raise ValueError("Formato de data nao padronizado")

    return resultado


def gerar_oltp_exemplo(banco):
    """Cria uma fonte didatica separada do OLTP Minishop."""
    banco = Path(banco)
    banco.parent.mkdir(parents=True, exist_ok=True)

    if banco.exists():
        with closing(sqlite3.connect(banco)) as con:
            quantidades = (
                con.execute(
                    "SELECT COUNT(*) FROM clientes"
                ).fetchone()[0],
                con.execute(
                    "SELECT COUNT(*) FROM faturas"
                ).fetchone()[0],
            )

        if quantidades != (2, 3):
            raise ValueError(
                "Fonte didatica existente nao corresponde ao exemplo"
            )

        return banco

    with closing(sqlite3.connect(banco)) as con:
        con.executescript(
            """
            PRAGMA foreign_keys = ON;

            CREATE TABLE clientes (
                id_cliente TEXT PRIMARY KEY,
                nome TEXT NOT NULL,
                endereco TEXT NOT NULL
            );

            CREATE TABLE faturas (
                id_fatura TEXT PRIMARY KEY,
                id_cliente TEXT NOT NULL,
                valor_fatura_centavos INTEGER NOT NULL,
                data_vencimento TEXT NOT NULL,
                data_pagamento TEXT,
                valor_pago_centavos INTEGER NOT NULL,
                FOREIGN KEY (id_cliente)
                    REFERENCES clientes(id_cliente)
            );
            """
        )

        con.executemany(
            "INSERT INTO clientes VALUES (?, ?, ?)",
            CLIENTES,
        )

        con.executemany(
            "INSERT INTO faturas VALUES (?, ?, ?, ?, ?, ?)",
            FATURAS,
        )

        con.commit()

    return banco


def gravar_parquet(caminho, esquema, registros):
    """Cria Parquet binario real usando DuckDB."""
    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)

    con = duckdb.connect(":memory:")

    try:
        definicoes = ", ".join(
            f'"{nome}" {tipo}'
            for nome, tipo in esquema
        )

        con.execute(
            f"CREATE TABLE dados ({definicoes})"
        )

        if registros:
            parametros = ", ".join(
                "?" for _ in esquema
            )

            con.executemany(
                f"INSERT INTO dados VALUES ({parametros})",
                registros,
            )

        con.execute(
            f"COPY dados TO {literal_sql(caminho.as_posix())} "
            "(FORMAT PARQUET, COMPRESSION SNAPPY)"
        )
    finally:
        con.close()

    with caminho.open("rb") as entrada:
        inicio = entrada.read(4)
        entrada.seek(-4, os.SEEK_END)
        fim = entrada.read(4)

    if inicio != b"PAR1" or fim != b"PAR1":
        raise ValueError("Arquivo Parquet invalido")


def consultar_parquet(caminho, consulta, parametros=()):
    """Consulta o arquivo Parquet sem importar para outro DW."""
    con = duckdb.connect(":memory:")

    try:
        con.execute(
            "CREATE VIEW dados AS SELECT * FROM read_parquet("
            + literal_sql(Path(caminho).resolve().as_posix())
            + ")"
        )

        resultado = con.execute(
            consulta,
            list(parametros),
        )

        colunas = [
            descricao[0]
            for descricao in resultado.description
        ]

        return [
            dict(zip(colunas, linha))
            for linha in resultado.fetchall()
        ]
    finally:
        con.close()


def criar_manifesto(pasta, camada, arquivos):
    pasta = Path(pasta)

    escrever_json(
        pasta / "manifest.json",
        {
            "camada": camada,
            "arquivos": {
                nome: arquivo_hash(pasta / nome)
                for nome in arquivos
            },
        },
    )


def validar_manifesto(pasta, camada):
    pasta = Path(pasta)
    manifesto = ler_json(pasta / "manifest.json")

    if manifesto["camada"] != camada:
        raise ValueError("Camada incorreta")

    for nome, hash_esperado in manifesto["arquivos"].items():
        arquivo = pasta / nome

        if (
            not arquivo.is_file()
            or arquivo_hash(arquivo) != hash_esperado
        ):
            raise ValueError(
                f"Integridade comprometida: {nome}"
            )

    return True


def criar_bronze(banco, raiz):
    """Preserva dados de origem em Parquet e JSON."""
    raiz = Path(raiz)
    destino = raiz / "bronze"
    destino.mkdir(parents=True, exist_ok=True)

    if (destino / "manifest.json").exists():
        validar_manifesto(destino, "bronze")
        return destino

    with closing(sqlite3.connect(
        Path(banco).resolve().as_uri() + "?mode=ro",
        uri=True,
    )) as con:
        clientes = [
            {
                "id_cliente": linha[0],
                "nome": linha[1],
                "endereco": linha[2],
            }
            for linha in con.execute(
                "SELECT * FROM clientes ORDER BY id_cliente"
            )
        ]

        faturas = con.execute(
            "SELECT * FROM faturas ORDER BY id_fatura"
        ).fetchall()

    escrever_json(
        destino / "clientes.json",
        clientes,
    )

    gravar_parquet(
        destino / "faturas_2026_janeiro.parquet",
        ESQUEMA_FATURAS,
        faturas,
    )

    criar_manifesto(
        destino,
        "bronze",
        (
            "clientes.json",
            "faturas_2026_janeiro.parquet",
        ),
    )

    return destino


def classificar_fatura(fatura, cliente, referencia):
    """Aplica as regras da Silver com referencia temporal."""
    vencimento = formato_data(
        fatura["data_vencimento"]
    )

    pagamento = (
        formato_data(fatura["data_pagamento"])
        if fatura["data_pagamento"]
        else None
    )

    if pagamento and pagamento > referencia:
        raise ValueError(
            "Pagamento posterior a fotografia; "
            "o exemplo nao possui historico de recebimentos"
        )

    valor = fatura["valor_fatura_centavos"]
    recebido = fatura["valor_pago_centavos"]

    if (
        valor <= 0
        or recebido < 0
        or recebido > valor
    ):
        raise ValueError("Valores financeiros invalidos")

    endereco = cliente["endereco"].split(",")

    if len(endereco) != 3:
        raise ValueError("Endereco sem cidade e estado")

    cidade = endereco[1].strip()
    estado = endereco[2].strip()

    saldo = valor - recebido

    atraso_pagamento = (
        max((pagamento - vencimento).days, 0)
        if pagamento else 0
    )

    atraso_atual = (
        max((referencia - vencimento).days, 0)
        if saldo > 0 else 0
    )

    if saldo == 0:
        status = (
            "PAGO ATRASO"
            if atraso_pagamento > 0
            else "PAGO"
        )
    else:
        status = "ABERTO"

    return (
        fatura["id_fatura"],
        fatura["id_cliente"],
        valor,
        fatura["data_vencimento"],
        fatura["data_pagamento"],
        recebido,
        cliente["nome"],
        cidade,
        estado,
        status,
        atraso_pagamento,
        atraso_atual,
        saldo,
    )


def criar_silver(bronze, raiz, referencia):
    """Junta faturas e clientes, padroniza status e atraso."""
    validar_manifesto(bronze, "bronze")

    destino = Path(raiz) / "silver"
    destino.mkdir(parents=True, exist_ok=True)

    if (destino / "manifest.json").exists():
        validar_manifesto(destino, "silver")
        return destino

    clientes = {
        item["id_cliente"]: item
        for item in ler_json(
            Path(bronze) / "clientes.json"
        )
    }

    faturas = consultar_parquet(
        Path(bronze) / "faturas_2026_janeiro.parquet",
        "SELECT * FROM dados ORDER BY id_fatura",
    )

    registros = []

    for fatura in faturas:
        cliente = clientes.get(fatura["id_cliente"])

        if cliente is None:
            raise ValueError("Cliente nao encontrado")

        registros.append(
            classificar_fatura(
                fatura, cliente, referencia
            )
        )

    gravar_parquet(
        destino / "contas_receber.parquet",
        ESQUEMA_TRATADO,
        registros,
    )

    criar_manifesto(
        destino,
        "silver",
        ("contas_receber.parquet",),
    )

    return destino


def classificar_aging(registro):
    """Distingue fatura paga e saldo em aberto."""
    saldo = registro["saldo_aberto_centavos"]

    if saldo == 0:
        dias = registro["atraso_pagamento_dias"]

        if dias == 0:
            return "Em dia"

        if dias <= 15:
            return "0-15"

        if dias <= 30:
            return "16-30"

        if dias <= 60:
            return "31-60"

        return "61+"

    dias = registro["dias_vencido_referencia"]

    if dias == 0:
        return "Aberto"

    if dias <= 15:
        return "0-15"

    if dias <= 30:
        return "16-30"

    if dias <= 60:
        return "31-60"

    return "61+"


def criar_gold(silver, raiz):
    """Adiciona aging e flags analiticas sobre a Silver."""
    validar_manifesto(silver, "silver")

    destino = Path(raiz) / "gold"
    destino.mkdir(parents=True, exist_ok=True)

    if (destino / "manifest.json").exists():
        validar_manifesto(destino, "gold")
        return destino

    dados = consultar_parquet(
        Path(silver) / "contas_receber.parquet",
        "SELECT * FROM dados ORDER BY id_fatura",
    )

    campos = [
        nome for nome, _ in ESQUEMA_TRATADO
    ]

    registros = []

    for item in dados:
        registros.append(
            tuple(item[nome] for nome in campos) + (
                classificar_aging(item),
                bool(
                    item["saldo_aberto_centavos"] > 0
                    and item["dias_vencido_referencia"] > 0
                ),
                bool(
                    item["atraso_pagamento_dias"] > 0
                ),
            )
        )

    gravar_parquet(
        destino / "contas_receber_gold.parquet",
        ESQUEMA_GOLD,
        registros,
    )

    criar_manifesto(
        destino,
        "gold",
        ("contas_receber_gold.parquet",),
    )

    return destino


def consultar_gold(gold, consulta, parametros=()):
    validar_manifesto(gold, "gold")

    return consultar_parquet(
        Path(gold) / "contas_receber_gold.parquet",
        consulta,
        parametros,
    )


def indicadores(gold):
    """Totais e inadimplencia atual, calculados em SQL."""
    totais = consultar_gold(
        gold,
        """
        SELECT
            COUNT(*) AS faturas,
            SUM(valor_fatura_centavos) AS emitido_centavos,
            SUM(valor_pago_centavos) AS recebido_centavos,
            SUM(saldo_aberto_centavos) AS aberto_centavos,
            SUM(
                CASE WHEN inadimplente_atual
                     THEN saldo_aberto_centavos ELSE 0 END
            ) AS vencido_centavos,
            SUM(
                CASE WHEN pago_com_atraso
                     THEN 1 ELSE 0 END
            ) AS pagamentos_atrasados
        FROM dados
        """,
    )[0]

    totais["inadimplencia_pct_emitido"] = round(
        (
            100 * totais["vencido_centavos"]
            / totais["emitido_centavos"]
        )
        if totais["emitido_centavos"] else 0,
        2,
    )

    return totais


def inadimplencia_por_local(gold, coluna):
    if coluna not in ("cidade", "estado"):
        raise ValueError("Agrupamento invalido")

    return consultar_gold(
        gold,
        f"""
        SELECT
            {coluna} AS localidade,
            SUM(valor_fatura_centavos) AS emitido_centavos,
            SUM(
                CASE WHEN inadimplente_atual
                     THEN saldo_aberto_centavos ELSE 0 END
            ) AS vencido_centavos,
            ROUND(
                100.0 * SUM(
                    CASE WHEN inadimplente_atual
                         THEN saldo_aberto_centavos ELSE 0 END
                )
                / NULLIF(SUM(valor_fatura_centavos), 0),
                2
            ) AS inadimplencia_pct_emitido
        FROM dados
        GROUP BY {coluna}
        ORDER BY {coluna}
        """,
    )


def carregar_dw(gold, raiz):
    """Modelo dimensional criado exclusivamente a partir da Gold."""
    validar_manifesto(gold, "gold")

    destino = Path(raiz) / "dw_contas_receber.db"

    if destino.exists():
        return destino

    registros = consultar_gold(
        gold,
        "SELECT * FROM dados ORDER BY id_fatura",
    )

    with closing(sqlite3.connect(destino)) as con:
        con.execute("PRAGMA foreign_keys = ON")

        try:
            con.execute("BEGIN IMMEDIATE")

            con.executescript(
                """
                CREATE TABLE dim_cliente (
                    sk_cliente INTEGER PRIMARY KEY,
                    id_cliente TEXT NOT NULL UNIQUE,
                    nome TEXT NOT NULL,
                    cidade TEXT NOT NULL,
                    estado TEXT NOT NULL
                );

                CREATE TABLE dim_tempo (
                    sk_tempo INTEGER PRIMARY KEY,
                    data TEXT NOT NULL,
                    mes INTEGER NOT NULL,
                    trimestre INTEGER NOT NULL
                );

                CREATE TABLE dim_aging (
                    sk_aging INTEGER PRIMARY KEY,
                    nome TEXT NOT NULL UNIQUE
                );

                CREATE TABLE fato_contas_receber (
                    id_fatura TEXT PRIMARY KEY,
                    sk_cliente INTEGER NOT NULL,
                    sk_tempo INTEGER NOT NULL,
                    sk_aging INTEGER NOT NULL,
                    valor_fatura_centavos INTEGER NOT NULL,
                    valor_pago_centavos INTEGER NOT NULL,
                    saldo_aberto_centavos INTEGER NOT NULL,
                    inadimplente_atual INTEGER NOT NULL,
                    FOREIGN KEY(sk_cliente)
                        REFERENCES dim_cliente(sk_cliente),
                    FOREIGN KEY(sk_tempo)
                        REFERENCES dim_tempo(sk_tempo),
                    FOREIGN KEY(sk_aging)
                        REFERENCES dim_aging(sk_aging)
                );
                """
            )

            clientes = sorted({
                (
                    r["id_cliente"],
                    r["nome_cliente"],
                    r["cidade"],
                    r["estado"],
                )
                for r in registros
            })

            mapa_cliente = {}

            for sk, cliente in enumerate(clientes, 1):
                con.execute(
                    "INSERT INTO dim_cliente VALUES (?,?,?,?,?)",
                    (sk, *cliente),
                )
                mapa_cliente[cliente[0]] = sk

            nomes_aging = sorted({
                r["aging"] for r in registros
            })

            mapa_aging = {}

            for sk, nome in enumerate(nomes_aging, 1):
                con.execute(
                    "INSERT INTO dim_aging VALUES (?,?)",
                    (sk, nome),
                )
                mapa_aging[nome] = sk

            for r in registros:
                vencimento = formato_data(
                    r["data_vencimento"]
                )
                sk_tempo = int(
                    vencimento.strftime("%Y%m%d")
                )

                con.execute(
                    """
                    INSERT OR IGNORE INTO dim_tempo
                    VALUES (?,?,?,?)
                    """,
                    (
                        sk_tempo,
                        vencimento.isoformat(),
                        vencimento.month,
                        (vencimento.month - 1) // 3 + 1,
                    ),
                )

                con.execute(
                    """
                    INSERT INTO fato_contas_receber
                    VALUES (?,?,?,?,?,?,?,?)
                    """,
                    (
                        r["id_fatura"],
                        mapa_cliente[r["id_cliente"]],
                        sk_tempo,
                        mapa_aging[r["aging"]],
                        r["valor_fatura_centavos"],
                        r["valor_pago_centavos"],
                        r["saldo_aberto_centavos"],
                        int(r["inadimplente_atual"]),
                    ),
                )

            con.commit()

        except Exception:
            con.rollback()
            raise

    return destino


def indicadores_dw(banco):
    with closing(sqlite3.connect(
        Path(banco).resolve().as_uri() + "?mode=ro",
        uri=True,
    )) as con:
        return con.execute(
            """
            SELECT COUNT(*),
                   SUM(valor_fatura_centavos),
                   SUM(valor_pago_centavos),
                   SUM(saldo_aberto_centavos),
                   SUM(CASE WHEN inadimplente_atual = 1
                       THEN saldo_aberto_centavos ELSE 0 END)
            FROM fato_contas_receber
            """
        ).fetchone()


def executar(raiz=RAIZ, referencia="2026-01-31"):
    referencia_data = formato_data(referencia)

    raiz = Path(raiz) / referencia
    raiz.mkdir(parents=True, exist_ok=True)

    origem = gerar_oltp_exemplo(
        raiz / "oltp_contas_receber.db"
    )

    bronze = criar_bronze(origem, raiz)
    silver = criar_silver(
        bronze, raiz, referencia_data
    )
    gold = criar_gold(silver, raiz)
    dw = carregar_dw(gold, raiz)

    lake = indicadores(gold)
    warehouse = indicadores_dw(dw)

    if (
        lake["emitido_centavos"],
        lake["recebido_centavos"],
        lake["aberto_centavos"],
        lake["vencido_centavos"],
    ) != warehouse[1:]:
        raise ValueError(
            "Divergencia Gold x Data Warehouse"
        )

    catalogo = {
        "exemplo": "Contas a receber didaticas",
        "referencia": referencia,
        "tabelas": {
            "bronze_faturas": {
                "arquivo": str(
                    bronze / "faturas_2026_janeiro.parquet"
                ),
                "formato": "Parquet",
            },
            "silver_contas_receber": {
                "arquivo": str(
                    silver / "contas_receber.parquet"
                ),
                "formato": "Parquet",
            },
            "gold_contas_receber": {
                "arquivo": str(
                    gold / "contas_receber_gold.parquet"
                ),
                "formato": "Parquet",
            },
        },
    }

    escrever_json(
        raiz / "catalogo_lakehouse.json",
        catalogo,
    )

    return {
        "raiz": str(raiz),
        "oltp": str(origem),
        "bronze": str(bronze),
        "silver": str(silver),
        "gold": str(gold),
        "dw": str(dw),
        "referencia": referencia,
        "indicadores": lake,
        "por_cidade": inadimplencia_por_local(
            gold, "cidade"
        ),
        "por_estado": inadimplencia_por_local(
            gold, "estado"
        ),
        "reconciliado": True,
    }
