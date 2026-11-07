"""Aula 27 - Consumo analitico pela camada semantica.

Dois dominios independentes:
1. Minishop: faturamento oficial de vendas, Aula 26.
2. Exemplo didatico de contas a receber, Aula 24.

Nao mistura recebimentos ilustrativos com o e-commerce real.
"""

from pathlib import Path

from src.aula26_camada_semantica import (
    METRICAS,
    DIMENSOES,
    consultar_metrica,
    auditar_consistencia,
    executar as executar_semantica,
)
from src.aula24_exemplo_camadas import (
    consultar_gold,
    executar as executar_contas,
)


CATALOGO_CONSUMO = {
    "minishop.faturamento": {
        "dominio": "minishop",
        "nome": "Faturamento da Minishop",
        "definicao": "Soma do valor das vendas registradas.",
        "unidade": "centavos",
        "fontes": ["lakehouse", "data_warehouse"],
        "dimensoes": [None, "cliente", "produto", "categoria", "mes"],
    },
    "minishop.pedidos": {
        "dominio": "minishop",
        "nome": "Pedidos de venda",
        "definicao": "Quantidade distinta de pedidos com vendas.",
        "unidade": "pedidos",
        "fontes": ["lakehouse", "data_warehouse"],
        "dimensoes": [None, "cliente", "produto", "categoria", "mes"],
    },
    "minishop.unidades": {
        "dominio": "minishop",
        "nome": "Unidades vendidas",
        "definicao": "Soma das quantidades vendidas.",
        "unidade": "unidades",
        "fontes": ["lakehouse", "data_warehouse"],
        "dimensoes": [None, "cliente", "produto", "categoria", "mes"],
    },
    "minishop.ticket_medio": {
        "dominio": "minishop",
        "nome": "Ticket medio por pedido",
        "definicao": (
            "Faturamento dividido pela quantidade distinta "
            "de pedidos de venda."
        ),
        "unidade": "centavos_por_pedido",
        "fontes": ["lakehouse", "data_warehouse"],
        "dimensoes": [None, "cliente", "produto", "categoria", "mes"],
    },
    "contas.valor_faturado": {
        "dominio": "contas_didaticas",
        "nome": "Valor das faturas emitidas",
        "definicao": "Soma dos valores nominais das faturas.",
        "unidade": "centavos",
        "fontes": ["contas_gold"],
        "dimensoes": [None, "estado"],
    },
    "contas.entrada_caixa": {
        "dominio": "contas_didaticas",
        "nome": "Valor recebido em caixa",
        "definicao": "Soma dos valores pagos registrados nas faturas.",
        "unidade": "centavos",
        "fontes": ["contas_gold"],
        "dimensoes": [None, "estado"],
    },
    "contas.saldo_aberto": {
        "dominio": "contas_didaticas",
        "nome": "Saldo ainda nao recebido",
        "definicao": "Soma do valor nominal menos o total recebido.",
        "unidade": "centavos",
        "fontes": ["contas_gold"],
        "dimensoes": [None, "estado"],
    },
}

COLUNAS_FINANCEIRAS = {
    "contas.valor_faturado": "valor_fatura_centavos",
    "contas.entrada_caixa": "valor_pago_centavos",
    "contas.saldo_aberto": "saldo_aberto_centavos",
}

FONTES_MINISHOP = ("lakehouse", "data_warehouse")


def catalogo_publico():
    """Lista oficial de indicadores para consumidores e BI."""
    return {
        "versao": "1.0",
        "indicadores": CATALOGO_CONSUMO,
        "observacao": (
            "O dominio contas_didaticas nao representa "
            "recebimentos operacionais da Minishop."
        ),
    }


def consultar_indicador(nome, fonte, contexto, dimensao=None):
    """Consulta de negocio; consumidor nao precisa escrever SQL."""
    if nome not in CATALOGO_CONSUMO:
        raise ValueError("Indicador nao definido: " + str(nome))

    definicao = CATALOGO_CONSUMO[nome]

    if fonte not in definicao["fontes"]:
        raise ValueError("Fonte nao autorizada para este indicador")

    if dimensao not in definicao["dimensoes"]:
        raise ValueError("Dimensao nao autorizada para este indicador")

    if definicao["dominio"] == "minishop":
        metrica = nome.split(".", 1)[1]

        resultado = consultar_metrica(
            metrica,
            fonte,
            gold=contexto["gold_minishop"],
            dw=contexto["dw_minishop"],
            dimensao=dimensao,
        )

        linhas = resultado["resultados"]

    else:
        coluna = COLUNAS_FINANCEIRAS[nome]

        # Colunas e agrupamentos provem de listas fixas,
        # nunca de texto SQL fornecido pelo consumidor.
        if dimensao is None:
            sql = (
                f"SELECT COALESCE(SUM({coluna}),0) "
                "AS valor FROM dados"
            )
        else:
            sql = (
                "SELECT estado AS dimensao, "
                f"COALESCE(SUM({coluna}),0) AS valor "
                "FROM dados GROUP BY estado ORDER BY estado"
            )

        linhas = consultar_gold(
            contexto["gold_contas"],
            sql,
        )

        linhas = [
            {
                **(
                    {"dimensao": linha["dimensao"]}
                    if dimensao else {}
                ),
                "valor": int(linha["valor"]),
            }
            for linha in linhas
        ]

    return {
        "indicador": nome,
        "nome": definicao["nome"],
        "definicao": definicao["definicao"],
        "fonte": fonte,
        "dimensao": dimensao,
        "unidade": definicao["unidade"],
        "resultados": linhas,
    }


def relatorio_area(area, contexto, fonte="lakehouse"):
    """Comercial e Financeiro usam a mesma metrica oficial."""
    if area not in ("comercial", "financeiro"):
        raise ValueError("Area nao cadastrada")

    if fonte not in FONTES_MINISHOP:
        raise ValueError("Fonte Minishop invalida")

    faturamento = consultar_indicador(
        "minishop.faturamento",
        fonte,
        contexto,
    )

    pedidos = consultar_indicador(
        "minishop.pedidos",
        fonte,
        contexto,
    )

    ticket = consultar_indicador(
        "minishop.ticket_medio",
        fonte,
        contexto,
    )

    return {
        "area": area,
        "fonte": fonte,
        "faturamento_centavos": faturamento["resultados"][0]["valor"],
        "pedidos": pedidos["resultados"][0]["valor"],
        "ticket_medio_centavos": ticket["resultados"][0]["valor"],
        "catalogo_usado": "camada_semantica_central",
    }


def demonstrar_conflito_semantico(contexto):
    """Exemplo da aula: dois conceitos com o mesmo rotulo.

    Usa SOMENTE as faturas didaticas da Aula 24.
    Nao atribui esses valores a operacoes reais da Minishop.
    """
    faturado = consultar_indicador(
        "contas.valor_faturado",
        "contas_gold",
        contexto,
    )["resultados"][0]["valor"]

    recebido = consultar_indicador(
        "contas.entrada_caixa",
        "contas_gold",
        contexto,
    )["resultados"][0]["valor"]

    return {
        "dominio": "contas_didaticas",
        "rotulo_ambiguo": "Faturamento",
        "interpretacao_comercial_centavos": faturado,
        "interpretacao_financeira_centavos": recebido,
        "diferenca_centavos": faturado - recebido,
        "iguais": faturado == recebido,
        "correcao": {
            "valor_faturado": "contas.valor_faturado",
            "entrada_caixa": "contas.entrada_caixa",
        },
    }


def auditar_consumo(contexto):
    """Audita padronizacao e conciliacao dos indicadores."""
    semantica = auditar_consistencia(
        contexto["gold_minishop"],
        contexto["dw_minishop"],
    )

    comercial = relatorio_area(
        "comercial",
        contexto,
        "lakehouse",
    )

    financeiro = relatorio_area(
        "financeiro",
        contexto,
        "data_warehouse",
    )

    mesmos_numeros = all(
        comercial[campo] == financeiro[campo]
        for campo in (
            "faturamento_centavos",
            "pedidos",
            "ticket_medio_centavos",
        )
    )

    faturado = consultar_indicador(
        "contas.valor_faturado", "contas_gold", contexto
    )["resultados"][0]["valor"]

    caixa = consultar_indicador(
        "contas.entrada_caixa", "contas_gold", contexto
    )["resultados"][0]["valor"]

    saldo = consultar_indicador(
        "contas.saldo_aberto", "contas_gold", contexto
    )["resultados"][0]["valor"]

    financeiro_conciliado = faturado == caixa + saldo

    return {
        "comparacoes_entre_fontes": semantica["comparacoes"],
        "fontes_consistentes": semantica["consistente"],
        "relatorios_equivalentes": mesmos_numeros,
        "contas_didaticas_conciliadas": financeiro_conciliado,
        "consistente": (
            semantica["consistente"]
            and mesmos_numeros
            and financeiro_conciliado
        ),
    }


def executar(oltp_minishop, lake, pasta_exemplo):
    """Prepara dois cenarios independentes e faz auditoria."""
    minishop = executar_semantica(
        oltp_minishop,
        lake,
    )

    contas = executar_contas(
        raiz=Path(pasta_exemplo),
        referencia="2026-01-31",
    )

    contexto = {
        "gold_minishop": minishop["gold"],
        "dw_minishop": minishop["data_warehouse"],
        "gold_contas": contas["gold"],
    }

    auditoria = auditar_consumo(contexto)

    if not auditoria["consistente"]:
        raise ValueError(
            "Inconsistencia na camada de consumo analitico"
        )

    return {
        "contexto": contexto,
        "catalogo": catalogo_publico(),
        "relatorios": {
            "comercial": relatorio_area(
                "comercial", contexto, "lakehouse"
            ),
            "financeiro": relatorio_area(
                "financeiro", contexto, "data_warehouse"
            ),
        },
        "conflito_didatico": demonstrar_conflito_semantico(
            contexto
        ),
        "auditoria": auditoria,
    }
