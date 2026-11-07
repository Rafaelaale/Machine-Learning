"""Aula 03: comparacao entre OLTP e OLAP da Minishop."""

import sqlite3
from contextlib import closing
from pathlib import Path
from time import perf_counter


CENARIOS = {
    "consultar_pedido": "OLTP",
    "consultar_estoque": "OLTP",
    "confirmar_pagamento": "OLTP",
    "cadastrar_cliente": "OLTP",
    "faturamento_mensal": "OLAP",
    "ticket_medio": "OLAP",
    "evolucao_vendas": "OLAP",
    "vendas_por_produto": "OLAP",
}


def classificar_pergunta(operacao):
    """Classifica operacoes conhecidas, sem adivinhar as demais."""
    if operacao not in CENARIOS:
        raise ValueError(f"Operacao desconhecida: {operacao}")

    return CENARIOS[operacao]


def medir_execucao(funcao):
    """Mede uma chamada local; nao constitui benchmark."""
    inicio = perf_counter()
    resultado = funcao()
    duracao_ms = (perf_counter() - inicio) * 1000

    return {
        "resultado": resultado,
        "duracao_ms": round(duracao_ms, 4),
    }


def consultar_operacao(banco_oltp, pedido_id):
    """Consulta pontual em banco transacional existente."""
    from src.minishop_oltp import consultar_pedido

    pedido = consultar_pedido(banco_oltp, pedido_id)

    if pedido is None:
        return None

    return {
        "pedido_id": pedido[0],
        "cliente_id": pedido[1],
        "total_centavos": pedido[2],
        "status": pedido[3],
    }


def consultar_analise(banco_olap):
    """Consulta consolidada no banco analitico."""
    from src.minishop_olap import (
        faturamento_mensal,
        faturamento_por_produto,
        indicadores,
    )

    return {
        "indicadores": indicadores(banco_olap),
        "produtos": faturamento_por_produto(banco_olap),
        "meses": faturamento_mensal(banco_olap),
    }


def apurar_origem(banco_oltp):
    """Calcula totais confirmados na origem para reconciliacao.

    Consulta somente leitura em conexao independente.
    """
    banco_oltp = Path(banco_oltp).resolve()

    if not banco_oltp.is_file():
        raise FileNotFoundError(banco_oltp)

    uri = banco_oltp.as_uri() + "?mode=ro"

    with closing(sqlite3.connect(uri, uri=True)) as conexao:
        pedidos, faturamento = conexao.execute(
            """
            SELECT
                COUNT(DISTINCT p.id),
                COALESCE(
                    SUM(i.quantidade * i.preco_unitario_centavos),
                    0
                )
            FROM pedidos AS p
            JOIN pagamentos AS pg
                ON pg.pedido_id = p.id
            LEFT JOIN itens_pedido AS i
                ON i.pedido_id = p.id
            WHERE p.status = 'confirmado'
              AND pg.status = 'aprovado'
            """
        ).fetchone()

    return {
        "pedidos": pedidos,
        "faturamento_centavos": faturamento,
    }


def comparar_totais(banco_oltp, banco_olap):
    """Compara receita e pedidos da origem e fotografia analitica."""
    from src.minishop_olap import indicadores

    origem = apurar_origem(banco_oltp)
    analitico = indicadores(banco_olap)

    reconciliado = (
        origem["pedidos"] == analitico["pedidos"]
        and origem["faturamento_centavos"]
        == analitico["faturamento_centavos"]
    )

    return {
        "oltp": origem,
        "olap": {
            "pedidos": analitico["pedidos"],
            "faturamento_centavos": (
                analitico["faturamento_centavos"]
            ),
        },
        "reconciliado": reconciliado,
        "observacao": (
            "Divergencias podem indicar fotografia desatualizada "
            "ou problemas na carga."
        ),
    }
