"""Aula 08 - Matriz dimensao-indicador da Minishop.

Distingue necessidades do negocio de dados existentes.
Consultas leem somente o DW construido na Aula 06.
"""

import sqlite3
from contextlib import closing
from pathlib import Path


DIMENSOES = {
    "tempo": "Data da venda",
    "cliente": "Cliente comprador",
    "produto": "Produto vendido",
    "categoria": "Categoria do produto",
    "cidade": "Cidade do cliente",
    "estado": "Estado do cliente",
    "faixa_etaria": "Idade na data do evento",
    "canal": "Dispositivo ou canal da compra",
    "promocao": "Promocao vigente no momento da compra",
    "aging": "Faixa de vencimento ou atraso",
}

INDICADORES = {
    "quantidade": {
        "nome": "Quantidade vendida",
        "grupo": "vendas",
        "unidade": "unidades",
    },
    "preco_medio": {
        "nome": "Preco medio unitario ponderado",
        "grupo": "vendas",
        "unidade": "centavos por unidade",
    },
    "valor_vendido": {
        "nome": "Valor vendido",
        "grupo": "vendas",
        "unidade": "centavos",
    },
    "saida_inventario": {
        "nome": "Saida de inventario",
        "grupo": "inventario",
        "unidade": "unidades",
    },
    "valor_a_cobrar": {
        "nome": "Valor a cobrar nao vencido",
        "grupo": "financeiro",
        "unidade": "centavos",
    },
    "valor_em_mora": {
        "nome": "Valor vencido nao pago",
        "grupo": "financeiro",
        "unidade": "centavos",
    },
}

VENDAS = {
    "tempo", "cliente", "produto", "categoria",
    "cidade", "estado", "faixa_etaria",
    "canal", "promocao",
}

INVENTARIO = {"tempo", "produto", "categoria"}

FINANCEIRO = {
    "tempo", "cliente", "cidade", "estado",
    "faixa_etaria", "aging",
}

# Dimensoes que estao disponiveis no DW atual.
DISPONIVEIS_VENDAS = {
    "tempo", "cliente", "produto", "categoria"
}

# Fontes existentes possuem dados de vendas.
# O data mart de inventario e o financeiro ainda nao
# foram implementados para a matriz desta aula.
FONTES_DISPONIVEIS = {"vendas"}


def matriz():
    """Gera uma matriz sem confundir plano e implementacao."""
    linhas = []

    for indicador, informacao in INDICADORES.items():
        grupo = informacao["grupo"]

        previstas = {
            "vendas": VENDAS,
            "inventario": INVENTARIO,
            "financeiro": FINANCEIRO,
        }[grupo]

        for dimensao in DIMENSOES:
            if dimensao not in previstas:
                situacao = "nao_aplicavel"
            elif (
                grupo in FONTES_DISPONIVEIS
                and dimensao in DISPONIVEIS_VENDAS
            ):
                situacao = "disponivel"
            else:
                situacao = "pendente"

            linhas.append({
                "indicador": indicador,
                "dimensao": dimensao,
                "situacao": situacao,
            })

    return linhas


def situacao_cruzamento(indicador, dimensao):
    """Consulta a situacao de um cruzamento especifico."""
    if indicador not in INDICADORES:
        raise ValueError("Indicador desconhecido")

    if dimensao not in DIMENSOES:
        raise ValueError("Dimensao desconhecida")

    return next(
        linha["situacao"]
        for linha in matriz()
        if linha["indicador"] == indicador
        and linha["dimensao"] == dimensao
    )


# SQL dinamico restrito a esta lista fixa de consultas.
AGRUPAMENTOS = {
    "tempo": "f.data",
    "cliente": "c.nome",
    "produto": "p.nome",
    "categoria": "p.categoria",
}


def consultar_vendas(banco_dw, indicador, dimensao):
    """Consulta apenas cruzamentos realmente disponiveis."""
    situacao = situacao_cruzamento(indicador, dimensao)

    if situacao != "disponivel":
        raise ValueError(
            f"Cruzamento indisponivel: {indicador}/{dimensao}"
            f" ({situacao})"
        )

    banco = Path(banco_dw).resolve()

    if not banco.is_file():
        raise FileNotFoundError(banco)

    campo = AGRUPAMENTOS[dimensao]

    consulta = f"""
        SELECT
            {campo} AS grupo,
            SUM(f.quantidade) AS unidades,
            SUM(f.valor_centavos) AS total_centavos
        FROM fato_vendas AS f
        JOIN dim_clientes AS c
          ON c.lote_id = f.lote_id
         AND c.cliente_id = f.cliente_id
        JOIN dim_produtos AS p
          ON p.lote_id = f.lote_id
         AND p.produto_id = f.produto_id
        WHERE f.lote_id = ?
        GROUP BY {campo}
        ORDER BY {campo}
    """

    with closing(
        sqlite3.connect(
            banco.as_uri() + "?mode=ro",
            uri=True,
        )
    ) as conexao:
        lote = conexao.execute(
            "SELECT MAX(lote_id) FROM lotes_carga"
        ).fetchone()[0]

        if lote is None:
            return []

        registros = conexao.execute(
            consulta, (lote,)
        ).fetchall()

    resultado = []

    for grupo, unidades, total in registros:
        valores = {
            "quantidade": unidades,
            "valor_vendido": total,
            "preco_medio": (
                round(total / unidades, 2)
                if unidades else None
            ),
        }

        resultado.append({
            "grupo": grupo,
            "valor": valores[indicador],
        })

    return resultado


REQUISITOS_PENDENTES = [
    {
        "campo": "endereco_estruturado",
        "motivo": "Obter cidade e estado verificaveis",
    },
    {
        "campo": "data_nascimento",
        "motivo": "Calcular faixa etaria na data da venda",
    },
    {
        "campo": "canal_venda",
        "motivo": "Analisar vendas por dispositivo",
    },
    {
        "campo": "promocao_no_momento_da_compra",
        "motivo": "Preservar o status historico da promocao",
    },
    {
        "campo": "data_vencimento_fatura",
        "motivo": "Determinar faixas de vencimento",
    },
    {
        "campo": "saldo_em_aberto_e_pagamentos",
        "motivo": "Identificar contas a receber e atrasos",
    },
    {
        "campo": "fato_movimentos_estoque",
        "motivo": "Separar indicadores de inventario dos de venda",
    },
]


def definicao_aging():
    """Especifica as faixas sem calcular valores inventados."""
    return {
        "nome": "Aging List - contas a receber",
        "data_referencia": "Data da consulta",
        "faixas_dias": [
            "0 a 15",
            "16 a 30",
            "31 a 60",
            "mais de 60",
        ],
        "grupos": [
            "a_vencer",
            "vencido",
        ],
        "criterio": (
            "Comparar vencimento com a data de referencia "
            "e considerar apenas saldo em aberto."
        ),
        "implementado": False,
        "motivo": (
            "OLTP atual nao possui vencimento e "
            "saldo financeiro detalhado."
        ),
    }


def validar_matriz():
    """Garante consistencia entre matriz e disponibilidade."""
    linhas = matriz()
    erros = []
    pares = set()

    for linha in linhas:
        par = (linha["indicador"], linha["dimensao"])

        if par in pares:
            erros.append(f"Cruzamento duplicado: {par}")

        pares.add(par)

        if linha["situacao"] not in {
            "disponivel", "pendente", "nao_aplicavel"
        }:
            erros.append(f"Situacao invalida: {par}")

        if (
            linha["situacao"] == "disponivel"
            and (
                linha["indicador"] not in {
                    "quantidade", "preco_medio", "valor_vendido"
                }
                or linha["dimensao"] not in AGRUPAMENTOS
            )
        ):
            erros.append(f"Disponibilidade indevida: {par}")

    esperado = len(INDICADORES) * len(DIMENSOES)

    if len(linhas) != esperado:
        erros.append("Quantidade de cruzamentos incorreta")

    return erros
