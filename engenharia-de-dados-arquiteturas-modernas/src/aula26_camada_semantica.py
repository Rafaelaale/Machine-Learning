"""Aula 26 - Camada semantica centralizada da Minishop.

Implementa um contrato unico para metricas e dimensoes
sobre duas fontes fisicas:
- Lakehouse: Parquet da Gold, consultado pelo DuckDB.
- Data Warehouse: modelo dimensional SQLite.

Nao cria copias adicionais dos datasets.
Nao modifica os arquivos das fontes.
"""

import json
import sqlite3

from contextlib import closing
from pathlib import Path

from src.aula25_lakehouse_minishop import (
    consultar_lakehouse,
    validar_gold_analitica,
    executar as executar_arquitetura,
)


METRICAS = {
    "faturamento": {
        "nome": "Faturamento",
        "descricao": "Soma do valor total das vendas.",
        "regra": "SUM(valor_total_centavos)",
        "unidade": "centavos",
        "tipo": "inteiro",
        "agregacao": "soma",
    },
    "pedidos": {
        "nome": "Quantidade de pedidos",
        "descricao": "Pedidos distintos com vendas registradas.",
        "regra": "COUNT(DISTINCT pedido_id)",
        "unidade": "pedidos",
        "tipo": "inteiro",
        "agregacao": "contagem_distinta",
    },
    "unidades": {
        "nome": "Unidades vendidas",
        "descricao": "Soma das quantidades comercializadas.",
        "regra": "SUM(quantidade)",
        "unidade": "unidades",
        "tipo": "inteiro",
        "agregacao": "soma",
    },
    "ticket_medio": {
        "nome": "Ticket medio por pedido",
        "descricao": "Faturamento dividido pelos pedidos distintos.",
        "regra": (
            "SUM(valor_total_centavos) / "
            "COUNT(DISTINCT pedido_id)"
        ),
        "unidade": "centavos_por_pedido",
        "tipo": "decimal",
        "agregacao": "razao_entre_agregacoes",
    },
}

DIMENSOES = {
    "cliente": {
        "nome": "Cliente",
        "descricao": "Cliente associado a venda.",
    },
    "produto": {
        "nome": "Produto",
        "descricao": "Produto comercializado.",
    },
    "categoria": {
        "nome": "Categoria",
        "descricao": "Categoria do produto.",
    },
    "mes": {
        "nome": "Mes",
        "descricao": "Mes da venda no formato YYYY-MM.",
    },
}

FONTES = {
    "lakehouse": {
        "tipo": "Parquet",
        "motor": "DuckDB",
        "descricao": "Consulta SQL diretamente na Gold analitica.",
    },
    "data_warehouse": {
        "tipo": "SQLite",
        "motor": "SQLite",
        "descricao": "Consulta dimensional de fatos e dimensoes.",
    },
}

# Campos fisicos diferentes recebem os mesmos nomes de negocio.
CAMPOS = {
    "lakehouse": {
        "cliente": "v.cliente_nome",
        "produto": "v.produto_nome",
        "categoria": "v.categoria_nome",
        "mes": "substr(v.data, 1, 7)",
    },
    "data_warehouse": {
        "cliente": "c.nome",
        "produto": "p.nome",
        "categoria": "p.categoria",
        "mes": "substr(t.data, 1, 7)",
    },
}

ORIGENS_SQL = {
    "lakehouse": "FROM vendas_enriquecidas v",
    "data_warehouse": """
        FROM fato_vendas v
        JOIN dim_cliente c ON c.sk_cliente = v.sk_cliente
        JOIN dim_produto p ON p.sk_produto = v.sk_produto
        JOIN dim_tempo t ON t.sk_tempo = v.sk_tempo
    """,
}


def catalogo_semantico():
    """Contrato publico de metricas e dimensoes."""
    return {
        "versao": "1.0",
        "nome": "Camada Semantica Minishop",
        "metricas": METRICAS,
        "dimensoes": DIMENSOES,
        "fontes": FONTES,
        "politicas": {
            "moeda": "BRL",
            "armazenamento_financeiro": "centavos",
            "pedidos": "contagem_distinta",
            "ticket_medio": "por_pedido",
            "dimensoes_permitidas": sorted(DIMENSOES),
            "consultas": "somente leitura",
        },
    }


def validar_pedido(metrica, dimensao, fonte):
    """Impede consultas a metricas, dimensoes ou fontes nao definidas."""
    if metrica not in METRICAS:
        raise ValueError("Metrica desconhecida: " + str(metrica))

    if dimensao is not None and dimensao not in DIMENSOES:
        raise ValueError("Dimensao desconhecida: " + str(dimensao))

    if fonte not in FONTES:
        raise ValueError("Fonte desconhecida: " + str(fonte))


def expressao_metrica(metrica):
    """Uma unica definicao matematica para as duas fontes."""
    if metrica == "faturamento":
        return "COALESCE(SUM(v.valor_total_centavos), 0)"

    if metrica == "pedidos":
        return "COUNT(DISTINCT v.pedido_id)"

    if metrica == "unidades":
        return "COALESCE(SUM(v.quantidade), 0)"

    if metrica == "ticket_medio":
        return """
            COALESCE(
                ROUND(
                    1.0 * SUM(v.valor_total_centavos)
                    / NULLIF(COUNT(DISTINCT v.pedido_id), 0),
                    2
                ),
                0
            )
        """

    raise ValueError("Metrica nao reconhecida")


def construir_sql(metrica, dimensao, fonte):
    """Traduz a linguagem de negocio para SQL da fonte escolhida."""
    validar_pedido(metrica, dimensao, fonte)

    medida = expressao_metrica(metrica)
    origem = ORIGENS_SQL[fonte]

    if dimensao is None:
        return (
            f"SELECT {medida} AS valor "
            f"{origem}"
        )

    campo = CAMPOS[fonte][dimensao]

    return f"""
        SELECT
            {campo} AS dimensao,
            {medida} AS valor
        {origem}
        GROUP BY {campo}
        ORDER BY dimensao
    """


def normalizar_valor(valor, metrica):
    """Padroniza os tipos retornados por DuckDB e SQLite."""
    if valor is None:
        valor = 0

    if metrica == "ticket_medio":
        return round(float(valor), 2)

    return int(valor)


def consultar_dw(banco, sql):
    """Leitura exclusivamente do DW, sem criar tabelas."""
    banco = Path(banco)

    if not banco.is_file():
        raise FileNotFoundError(banco)

    with closing(sqlite3.connect(
        banco.resolve().as_uri() + "?mode=ro",
        uri=True,
    )) as con:
        cursor = con.execute(sql)
        colunas = [
            coluna[0] for coluna in cursor.description
        ]

        return [
            dict(zip(colunas, linha))
            for linha in cursor.fetchall()
        ]


def consultar_metrica(
    metrica,
    fonte,
    gold=None,
    dw=None,
    dimensao=None,
):
    """Interface unica para os consumidores analiticos.

    Exemplo:
        consultar_metrica(
            "faturamento",
            "lakehouse",
            gold=pasta_gold,
            dimensao="categoria",
        )
    """
    validar_pedido(metrica, dimensao, fonte)

    sql = construir_sql(
        metrica, dimensao, fonte
    )

    if fonte == "lakehouse":
        if gold is None:
            raise ValueError("Informe a pasta Gold analitica")

        validar_gold_analitica(gold)
        linhas = consultar_lakehouse(gold, sql)

    else:
        if dw is None:
            raise ValueError("Informe o banco Data Warehouse")

        linhas = consultar_dw(dw, sql)

    resultado = []

    for linha in linhas:
        item = {
            "valor": normalizar_valor(
                linha["valor"], metrica
            ),
        }

        if dimensao is not None:
            item["dimensao"] = linha["dimensao"]

        resultado.append(item)

    return {
        "metrica": metrica,
        "nome": METRICAS[metrica]["nome"],
        "fonte": fonte,
        "dimensao": dimensao,
        "unidade": METRICAS[metrica]["unidade"],
        "resultados": resultado,
    }


def comparar_fontes(metrica, gold, dw, dimensao=None):
    """Garante resultado semantico igual entre duas origens."""
    lakehouse = consultar_metrica(
        metrica,
        "lakehouse",
        gold=gold,
        dimensao=dimensao,
    )

    warehouse = consultar_metrica(
        metrica,
        "data_warehouse",
        dw=dw,
        dimensao=dimensao,
    )

    iguais = (
        lakehouse["resultados"]
        == warehouse["resultados"]
    )

    return {
        "metrica": metrica,
        "dimensao": dimensao,
        "lakehouse": lakehouse["resultados"],
        "data_warehouse": warehouse["resultados"],
        "iguais": iguais,
    }


def auditar_consistencia(gold, dw):
    """Testa todas as combinacoes oficiais.

    4 metricas x (sem dimensao + 4 dimensoes)
    = 20 comparacoes.
    """
    verificacoes = []

    for metrica in METRICAS:
        for dimensao in (None, *DIMENSOES):
            verificacoes.append(
                comparar_fontes(
                    metrica,
                    gold,
                    dw,
                    dimensao,
                )
            )

    return {
        "comparacoes": len(verificacoes),
        "consistente": all(
            item["iguais"]
            for item in verificacoes
        ),
        "divergencias": [
            item
            for item in verificacoes
            if not item["iguais"]
        ],
    }


def relatorio_bi(gold, dw, fonte="lakehouse"):
    """Um consumidor de BI utiliza apenas nomes de negocio."""
    if fonte not in FONTES:
        raise ValueError("Fonte nao suportada")

    consultas = {}

    for metrica in METRICAS:
        consultas[metrica] = consultar_metrica(
            metrica,
            fonte,
            gold=gold,
            dw=dw,
        )["resultados"][0]["valor"]

    consultas["faturamento_por_categoria"] = (
        consultar_metrica(
            "faturamento",
            fonte,
            gold=gold,
            dw=dw,
            dimensao="categoria",
        )["resultados"]
    )

    return consultas


def executar(oltp, lake):
    """Executa a arquitetura existente e a camada semantica."""
    arquitetura = executar_arquitetura(
        oltp, lake
    )

    gold = Path(
        arquitetura["gold_analitica"]
    )
    dw = Path(
        arquitetura["data_warehouse"]
    )

    auditoria = auditar_consistencia(gold, dw)

    if not auditoria["consistente"]:
        raise ValueError(
            "Metricas divergentes entre DW e Lakehouse"
        )

    painel_lakehouse = relatorio_bi(
        gold, dw, "lakehouse"
    )

    painel_dw = relatorio_bi(
        gold, dw, "data_warehouse"
    )

    if painel_lakehouse != painel_dw:
        raise ValueError(
            "Consumidores de BI retornaram resultados diferentes"
        )

    return {
        "snapshot_id": arquitetura["snapshot_id"],
        "gold": str(gold),
        "data_warehouse": str(dw),
        "catalogo_semantico": catalogo_semantico(),
        "auditoria": auditoria,
        "bi_lakehouse": painel_lakehouse,
        "bi_data_warehouse": painel_dw,
    }
