"""Aula 21 - Introducao ao Lakehouse da Minishop.

Objetivo didatico:
consultar datasets Silver com SQL sem criar outro DW
persistente e reconciliar resultados com a camada Gold.

SQLite e utilizado em memoria como motor de consulta.
Nao representa Delta Lake, Iceberg ou Hudi.
"""

import json
import sqlite3
from contextlib import closing, contextmanager
from pathlib import Path

from src.aula17_data_lake import (
    LAKE,
    hash_arquivo,
    validar_snapshot,
)
from src.aula20_data_lake_minishop import (
    obter_snapshot,
    criar_bronze_dominios,
    preparar_silver,
    criar_gold_mensal,
    ler_silver,
    ler_jsonl,
    validar_camada,
)


def preparar_camadas(oltp, lake=LAKE):
    """Reutiliza as camadas existentes, sem substitui-las."""
    snapshot = obter_snapshot(oltp, lake)
    bronze = criar_bronze_dominios(
        snapshot["pasta"], lake
    )
    silver = preparar_silver(bronze["pasta"], lake)
    gold = criar_gold_mensal(silver["pasta"], lake)

    return {
        "snapshot": snapshot,
        "bronze": bronze,
        "silver": silver,
        "gold": gold,
    }


def conferir_camadas(camadas):
    """Garante que os dados utilizados estao integrados."""
    validar_snapshot(camadas["snapshot"]["pasta"])

    for nome, tipo in (
        ("bronze", "bronze"),
        ("silver", "silver"),
        ("gold", "gold"),
    ):
        manifesto = validar_camada(
            camadas[nome]["pasta"], tipo
        )

        if (
            manifesto["snapshot_id"]
            != camadas["snapshot"]["snapshot_id"]
        ):
            raise ValueError(
                "Identificadores de snapshot divergentes"
            )

    return True


@contextmanager
def abrir_consulta_silver(pasta_silver):
    """Le arquivos Silver e disponibiliza tabelas SQL em RAM.

    O banco SQLite nao e salvo no disco. Os arquivos
    originais nao sao alterados.

    O SQLite e um motor didatico; a leitura inicial
    materializa os registros na memoria do processo.
    """
    validar_camada(pasta_silver, "silver")
    dados = ler_silver(pasta_silver)

    con = sqlite3.connect(":memory:")
    con.row_factory = sqlite3.Row

    try:
        con.executescript(
            """
            PRAGMA foreign_keys = ON;

            CREATE TABLE clientes (
                cliente_id INTEGER PRIMARY KEY,
                nome TEXT NOT NULL
            );

            CREATE TABLE produtos (
                produto_id INTEGER PRIMARY KEY,
                produto_nome TEXT NOT NULL,
                categoria_id INTEGER NOT NULL,
                categoria_nome TEXT NOT NULL
            );

            CREATE TABLE vendas (
                pedido_id INTEGER NOT NULL,
                cliente_id INTEGER NOT NULL,
                data TEXT NOT NULL,
                produto_id INTEGER NOT NULL,
                quantidade INTEGER NOT NULL,
                preco_unitario_centavos INTEGER NOT NULL,
                valor_total_centavos INTEGER NOT NULL,
                PRIMARY KEY (pedido_id, produto_id),
                FOREIGN KEY (cliente_id)
                    REFERENCES clientes(cliente_id),
                FOREIGN KEY (produto_id)
                    REFERENCES produtos(produto_id)
            );

            CREATE TABLE movimentos (
                movimento_id INTEGER PRIMARY KEY,
                produto_id INTEGER NOT NULL,
                data TEXT NOT NULL,
                quantidade INTEGER NOT NULL,
                FOREIGN KEY (produto_id)
                    REFERENCES produtos(produto_id)
            );

            CREATE VIEW vw_vendas_analiticas AS
            SELECT
                v.pedido_id,
                v.data,
                v.cliente_id,
                c.nome AS cliente,
                v.produto_id,
                p.produto_nome AS produto,
                p.categoria_nome AS categoria,
                v.quantidade,
                v.preco_unitario_centavos,
                v.valor_total_centavos
            FROM vendas v
            JOIN clientes c
              ON c.cliente_id = v.cliente_id
            JOIN produtos p
              ON p.produto_id = v.produto_id;
            """
        )

        with con:
            for item in dados["clientes"]:
                con.execute(
                    """
                    INSERT INTO clientes(cliente_id, nome)
                    VALUES (?, ?)
                    """,
                    (
                        item["cliente_id"],
                        item["nome"],
                    ),
                )

            for item in dados["produtos"]:
                con.execute(
                    """
                    INSERT INTO produtos(
                        produto_id,
                        produto_nome,
                        categoria_id,
                        categoria_nome
                    )
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        item["produto_id"],
                        item["produto_nome"],
                        item["categoria_id"],
                        item["categoria_nome"],
                    ),
                )

            for item in dados["vendas"]:
                quantidade = item["quantidade"]
                preco = item["preco_unitario_centavos"]
                total = item["valor_total_centavos"]

                if (
                    type(quantidade) is not int
                    or quantidade <= 0
                    or type(preco) is not int
                    or preco < 0
                    or type(total) is not int
                    or total != quantidade * preco
                ):
                    raise ValueError(
                        "Medidas de venda inconsistentes"
                    )

                con.execute(
                    """
                    INSERT INTO vendas(
                        pedido_id, cliente_id, data,
                        produto_id, quantidade,
                        preco_unitario_centavos,
                        valor_total_centavos
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        item["pedido_id"],
                        item["cliente_id"],
                        item["data"],
                        item["produto_id"],
                        quantidade,
                        preco,
                        total,
                    ),
                )

            for item in dados["movimentos"]:
                if (
                    type(item["quantidade"]) is not int
                    or item["quantidade"] <= 0
                ):
                    raise ValueError(
                        "Movimento de estoque invalido"
                    )

                con.execute(
                    """
                    INSERT INTO movimentos(
                        movimento_id, produto_id,
                        data, quantidade
                    )
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        item["movimento_id"],
                        item["produto_id"],
                        item["data"],
                        item["quantidade"],
                    ),
                )

        # O motor SQL passa a aceitar apenas leitura.
        con.execute("PRAGMA query_only = ON")

        yield con

    finally:
        con.close()


def consulta_sql(pasta_silver, comando, parametros=()):
    """Executa SELECT sobre as tabelas em memoria.

    A restricao query_only tambem impede escrita
    realizada indiretamente por um comando SQL.
    """
    if (
        not isinstance(comando, str)
        or comando.strip().split(None, 1)[0].upper() != "SELECT"
    ):
        raise ValueError(
            "A consulta deve ser um SELECT"
        )

    with abrir_consulta_silver(pasta_silver) as con:
        resultado = con.execute(
            comando,
            tuple(parametros),
        ).fetchall()

        return [
            dict(registro)
            for registro in resultado
        ]


def indicadores_silver(pasta_silver):
    """Agrega vendas e inventario com SQL."""
    vendas = consulta_sql(
        pasta_silver,
        """
        SELECT
            COUNT(*) AS linhas_vendas,
            COALESCE(SUM(quantidade), 0) AS unidades,
            COALESCE(SUM(valor_total_centavos), 0)
                AS faturamento_centavos,
            COUNT(DISTINCT pedido_id) AS pedidos,
            COUNT(DISTINCT produto_id)
                AS produtos_distintos
        FROM vendas
        """,
    )[0]

    inventario = consulta_sql(
        pasta_silver,
        """
        SELECT
            COUNT(*) AS movimentos,
            COALESCE(SUM(quantidade), 0)
                AS unidades_saida
        FROM movimentos
        """,
    )[0]

    return {
        **vendas,
        **inventario,
    }


def consultar_mensal(pasta_silver):
    return consulta_sql(
        pasta_silver,
        """
        SELECT
            substr(data, 1, 7) AS periodo,
            COUNT(DISTINCT pedido_id) AS pedidos,
            COUNT(*) AS itens,
            SUM(quantidade) AS unidades,
            SUM(valor_total_centavos)
                AS faturamento_centavos
        FROM vendas
        GROUP BY substr(data, 1, 7)
        ORDER BY periodo
        """,
    )


def consultar_produtos(pasta_silver):
    return consulta_sql(
        pasta_silver,
        """
        SELECT
            produto_id,
            produto,
            categoria,
            SUM(quantidade) AS unidades,
            SUM(valor_total_centavos)
                AS faturamento_centavos
        FROM vw_vendas_analiticas
        GROUP BY produto_id, produto, categoria
        ORDER BY faturamento_centavos DESC, produto_id
        """,
    )


def consultar_clientes(pasta_silver):
    return consulta_sql(
        pasta_silver,
        """
        SELECT
            cliente_id,
            cliente,
            COUNT(DISTINCT pedido_id) AS pedidos,
            SUM(valor_total_centavos)
                AS faturamento_centavos
        FROM vw_vendas_analiticas
        GROUP BY cliente_id, cliente
        ORDER BY cliente_id
        """,
    )


def reconciliar_gold(pasta_silver, pasta_gold):
    """Compara a consulta SQL com a Gold mensal existente."""
    validar_camada(pasta_gold, "gold")

    sql = consultar_mensal(pasta_silver)

    gold = ler_jsonl(
        Path(pasta_gold)
        / "indicadores_mensais.jsonl"
    )

    chave = lambda item: item["periodo"]

    sql = sorted(sql, key=chave)
    gold = sorted(gold, key=chave)

    igual = sql == gold

    return {
        "mensal_sql": sql,
        "mensal_gold": gold,
        "reconciliado": igual,
        "faturamento_sql_centavos": sum(
            item["faturamento_centavos"]
            for item in sql
        ),
        "faturamento_gold_centavos": sum(
            item["faturamento_centavos"]
            for item in gold
        ),
    }


def consultar_snapshot_sem_oltp(pasta_silver):
    """Consulta um snapshot existente sem conexao operacional."""
    validar_camada(pasta_silver, "silver")

    return {
        "indicadores": indicadores_silver(pasta_silver),
        "mensal": consultar_mensal(pasta_silver),
        "produtos": consultar_produtos(pasta_silver),
        "clientes": consultar_clientes(pasta_silver),
    }


def executar_laboratorio(oltp, lake=LAKE):
    """Prepara camadas e executa consultas sem gerar DW."""
    camadas = preparar_camadas(oltp, lake)
    conferir_camadas(camadas)

    silver = camadas["silver"]["pasta"]
    gold = camadas["gold"]["pasta"]

    resultado = consultar_snapshot_sem_oltp(silver)
    conciliacao = reconciliar_gold(silver, gold)

    if not conciliacao["reconciliado"]:
        raise ValueError(
            "Indicadores SQL e Gold divergentes"
        )

    return {
        "snapshot_id": camadas["snapshot"]["snapshot_id"],
        "camadas": camadas,
        "consultas": resultado,
        "reconciliacao": conciliacao,
        "banco_dw_persistente_criado": False,
    }
