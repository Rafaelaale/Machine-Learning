"""Aula 22: Lakehouse didatico com DuckDB, Parquet e catalogo local."""

import json
import os
import re
import shutil
import tempfile
from pathlib import Path

import duckdb

from src.aula17_data_lake import LAKE, hash_arquivo
from src.aula20_data_lake_minishop import (
    obter_snapshot, criar_bronze_dominios, preparar_silver,
    criar_gold_mensal, ler_silver, ler_jsonl, validar_camada,
)

ESQUEMAS = {
    "clientes": [
        ("cliente_id", "BIGINT"),
        ("nome", "VARCHAR"),
        ("email", "VARCHAR"),
    ],
    "produtos": [
        ("produto_id", "BIGINT"),
        ("produto_nome", "VARCHAR"),
        ("categoria_id", "BIGINT"),
        ("categoria_nome", "VARCHAR"),
    ],
    "vendas": [
        ("pedido_id", "BIGINT"),
        ("cliente_id", "BIGINT"),
        ("data", "VARCHAR"),
        ("produto_id", "BIGINT"),
        ("produto_nome", "VARCHAR"),
        ("quantidade", "BIGINT"),
        ("preco_unitario_centavos", "BIGINT"),
        ("valor_total_centavos", "BIGINT"),
    ],
    "movimentos": [
        ("movimento_id", "BIGINT"),
        ("produto_id", "BIGINT"),
        ("data", "VARCHAR"),
        ("quantidade", "BIGINT"),
    ],
}


def escrever_json(caminho, objeto):
    Path(caminho).write_text(
        json.dumps(objeto, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def literal_sql(valor):
    return "'" + str(valor).replace("'", "''") + "'"


def validar_catalogo(pasta):
    pasta = Path(pasta)
    manifest_path = pasta / "manifest.json"
    catalogo_path = pasta / "catalogo.json"

    if not manifest_path.is_file() or not catalogo_path.is_file():
        raise ValueError("Manifesto ou catalogo ausente")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    catalogo = json.loads(catalogo_path.read_text(encoding="utf-8"))

    if (
        manifest.get("camada") != "lakehouse"
        or manifest.get("snapshot_id") != pasta.name
        or catalogo.get("snapshot_id") != pasta.name
    ):
        raise ValueError("Identificador do snapshot invalido")

    tabelas = catalogo.get("tabelas", {})
    if set(tabelas) != set(ESQUEMAS):
        raise ValueError("Catalogo incompleto")

    esperados = {"catalogo.json"}
    for nome, esquema in ESQUEMAS.items():
        definicao = tabelas[nome]
        arquivo = f"{nome}.parquet"
        colunas = [
            {"nome": coluna, "tipo": tipo}
            for coluna, tipo in esquema
        ]
        if (
            definicao.get("arquivo") != arquivo
            or definicao.get("esquema") != colunas
        ):
            raise ValueError("Definicao de tabela divergente")
        esperados.add(arquivo)

    arquivos = manifest.get("arquivos", {})
    presentes = {
        p.name for p in pasta.iterdir()
        if p.is_file() and p.name != "manifest.json"
    }

    if set(arquivos) != esperados or presentes != esperados:
        raise ValueError("Arquivos nao correspondem ao catalogo")

    for nome, hash_esperado in arquivos.items():
        arquivo = pasta / nome
        if not arquivo.is_file() or hash_arquivo(arquivo) != hash_esperado:
            raise ValueError(f"Integridade comprometida: {nome}")

    return catalogo


def validar_vendas(dados):
    clientes = {c["cliente_id"] for c in dados["clientes"]}
    produtos = {p["produto_id"] for p in dados["produtos"]}
    chaves = set()

    for v in dados["vendas"]:
        chave = (v["pedido_id"], v["produto_id"])
        if chave in chaves:
            raise ValueError("Venda duplicada")
        chaves.add(chave)

        if v["cliente_id"] not in clientes or v["produto_id"] not in produtos:
            raise ValueError("Cliente ou produto inexistente")

        quantidade = v["quantidade"]
        unitario = v["preco_unitario_centavos"]
        total = v["valor_total_centavos"]

        if (
            type(quantidade) is not int
            or type(unitario) is not int
            or type(total) is not int
            or quantidade <= 0
            or unitario < 0
            or total != quantidade * unitario
        ):
            raise ValueError("Medidas de venda invalidas")

    return True


def criar_lakehouse(pasta_silver, lake=LAKE):
    manifest_silver = validar_camada(pasta_silver, "silver")
    snapshot_id = manifest_silver["snapshot_id"]

    destino = (
        Path(lake) / "lakehouse" / "minishop" / snapshot_id
    )
    destino.parent.mkdir(parents=True, exist_ok=True)

    if destino.exists():
        validar_catalogo(destino)
        return {
            "pasta": str(destino), "snapshot_id": snapshot_id, "novo": False
        }

    dados = ler_silver(pasta_silver)
    validar_vendas(dados)

    temporaria = Path(tempfile.mkdtemp(
        prefix=".aula22_", dir=destino.parent
    ))

    try:
        catalogo = {
            "snapshot_id": snapshot_id,
            "motor": "DuckDB",
            "formato": "Parquet",
            "origem": "Silver da Minishop",
            "tabelas": {},
        }

        con = duckdb.connect(":memory:")
        try:
            for nome, esquema in ESQUEMAS.items():
                definicao = ", ".join(
                    f'"{coluna}" {tipo}' for coluna, tipo in esquema
                )
                tabela = f"stage_{nome}"
                con.execute(f"CREATE TABLE {tabela} ({definicao})")

                registros = dados[nome]
                if registros:
                    parametros = ", ".join("?" for _ in esquema)
                    valores = [
                        tuple(linha[coluna] for coluna, _ in esquema)
                        for linha in registros
                    ]
                    con.executemany(
                        f"INSERT INTO {tabela} VALUES ({parametros})",
                        valores,
                    )

                arquivo = temporaria / f"{nome}.parquet"
                con.execute(
                    f"COPY {tabela} TO {literal_sql(arquivo.as_posix())} "
                    "(FORMAT PARQUET, COMPRESSION SNAPPY)"
                )

                catalogo["tabelas"][nome] = {
                    "arquivo": f"{nome}.parquet",
                    "linhas": len(registros),
                    "esquema": [
                        {"nome": c, "tipo": t} for c, t in esquema
                    ],
                }
        finally:
            con.close()

        escrever_json(temporaria / "catalogo.json", catalogo)

        nomes = [
            "catalogo.json",
            *(f"{nome}.parquet" for nome in ESQUEMAS),
        ]
        manifest = {
            "camada": "lakehouse",
            "snapshot_id": snapshot_id,
            "arquivos": {
                nome: hash_arquivo(temporaria / nome)
                for nome in nomes
            },
        }
        escrever_json(temporaria / "manifest.json", manifest)

        os.rename(temporaria, destino)
    finally:
        if temporaria.exists():
            shutil.rmtree(temporaria)

    validar_catalogo(destino)
    return {
        "pasta": str(destino), "snapshot_id": snapshot_id, "novo": True
    }


def consultar_parquet(pasta, sql, parametros=()):
    catalogo = validar_catalogo(pasta)

    if not isinstance(sql, str):
        raise ValueError("Consulta SQL invalida")

    comando = sql.strip()

    if not re.match(r"^SELECT\b", comando, re.IGNORECASE):
        raise ValueError("Somente SELECT e permitido")
    if ";" in comando.rstrip(";"):
        raise ValueError("Comandos multiplos nao permitidos")

    con = duckdb.connect(":memory:")
    try:
        for nome, definicao in catalogo["tabelas"].items():
            arquivo = (Path(pasta) / definicao["arquivo"]).resolve()
            con.execute(
                f"CREATE VIEW {nome} AS "
                f"SELECT * FROM read_parquet({literal_sql(arquivo.as_posix())})"
            )

        resultado = con.execute(comando, list(parametros))
        colunas = [item[0] for item in resultado.description]
        return [
            dict(zip(colunas, linha))
            for linha in resultado.fetchall()
        ]
    finally:
        con.close()


def resumo_vendas(pasta):
    return consultar_parquet(
        pasta,
        """
        SELECT COUNT(*) AS linhas_vendas,
               COALESCE(SUM(quantidade),0) AS unidades,
               COALESCE(SUM(valor_total_centavos),0)
                   AS faturamento_centavos,
               COUNT(DISTINCT pedido_id) AS pedidos
        FROM vendas
        """,
    )[0]


def vendas_por_mes(pasta):
    return consultar_parquet(
        pasta,
        """
        SELECT substr(data,1,7) AS periodo,
               COUNT(DISTINCT pedido_id) AS pedidos,
               COUNT(*) AS itens,
               COALESCE(SUM(quantidade),0) AS unidades,
               COALESCE(SUM(valor_total_centavos),0)
                   AS faturamento_centavos
        FROM vendas
        GROUP BY substr(data,1,7)
        ORDER BY periodo
        """,
    )


def vendas_por_produto(pasta):
    return consultar_parquet(
        pasta,
        """
        SELECT p.produto_id, p.produto_nome, p.categoria_nome,
               SUM(v.quantidade) AS unidades,
               SUM(v.valor_total_centavos) AS faturamento_centavos
        FROM vendas v
        JOIN produtos p ON p.produto_id = v.produto_id
        GROUP BY p.produto_id, p.produto_nome, p.categoria_nome
        ORDER BY p.produto_id
        """,
    )


def vendas_por_cliente(pasta):
    return consultar_parquet(
        pasta,
        """
        SELECT c.cliente_id, c.nome,
               COUNT(DISTINCT v.pedido_id) AS pedidos,
               SUM(v.valor_total_centavos) AS faturamento_centavos
        FROM vendas v
        JOIN clientes c ON c.cliente_id = v.cliente_id
        GROUP BY c.cliente_id, c.nome
        ORDER BY c.cliente_id
        """,
    )


def reconciliar_gold(pasta_lakehouse, pasta_gold):
    validar_camada(pasta_gold, "gold")
    gold = ler_jsonl(Path(pasta_gold) / "indicadores_mensais.jsonl")
    sql = vendas_por_mes(pasta_lakehouse)
    return {
        "reconciliado": sql == sorted(gold, key=lambda x: x["periodo"]),
        "lakehouse": sql,
        "gold": gold,
    }


def executar(oltp, lake=LAKE):
    snapshot = obter_snapshot(oltp, lake)
    bronze = criar_bronze_dominios(snapshot["pasta"], lake)
    silver = preparar_silver(bronze["pasta"], lake)
    gold = criar_gold_mensal(silver["pasta"], lake)
    lakehouse = criar_lakehouse(silver["pasta"], lake)

    pasta = lakehouse["pasta"]
    comparacao = reconciliar_gold(pasta, gold["pasta"])
    if not comparacao["reconciliado"]:
        raise ValueError("Gold e Lakehouse divergentes")

    return {
        "snapshot": snapshot,
        "bronze": bronze,
        "silver": silver,
        "gold": gold,
        "lakehouse": lakehouse,
        "resumo": resumo_vendas(pasta),
        "mensal": vendas_por_mes(pasta),
        "produtos": vendas_por_produto(pasta),
        "clientes": vendas_por_cliente(pasta),
        "reconciliacao": comparacao,
    }
