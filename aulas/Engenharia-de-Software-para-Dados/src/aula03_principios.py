"""Aula 03: principios 4 a 7 da engenharia de software.

4. O que um produz, outros consomem.
5. Esteja aberto para o futuro.
6. Planeje com antecedencia.
7. Pense antes de agir.

Usa regras didaticas, nao um modelo real de churn.
"""

import csv
from pathlib import Path

from src.aula02_churn import validar_cliente


COLUNAS = {
    "cliente_id",
    "produto_codigo",
    "dias_sem_compra",
    "compras_90d",
    "reclamacoes_90d",
    "valor_total",
}

LIMITE_PADRAO = 60


def carregar_clientes_produtos(caminho):
    """Carrega e valida registros de varios produtos."""

    with Path(caminho).open(
        "r", encoding="utf-8-sig", newline=""
    ) as arquivo:
        leitor = csv.DictReader(arquivo)

        if not COLUNAS.issubset(leitor.fieldnames or []):
            raise ValueError("Colunas obrigatorias ausentes")

        clientes = []

        for linha in leitor:
            cliente = validar_cliente(linha)
            codigo = str(
                linha["produto_codigo"]
            ).strip()

            if not codigo:
                raise ValueError("Codigo de produto vazio")

            cliente["produto_codigo"] = codigo
            clientes.append(cliente)

    return clientes


def resolver_produto(codigo, catalogo):
    """Resolve o codigo sem depender de valores fixos."""

    if not isinstance(catalogo, dict):
        raise TypeError("Catalogo deve ser um dicionario")

    return catalogo.get(codigo, "PRODUTO_NAO_CADASTRADO")


def classificar_com_parametros(
    cliente,
    limite_dias=LIMITE_PADRAO,
    limite_reclamacoes=2,
):
    """Aplica regras configuraveis de atencao ao cliente.

    A classificacao e apenas uma regra de negocio
    ilustrativa, nao uma previsao de abandono.
    """

    if limite_dias < 0 or limite_reclamacoes < 0:
        raise ValueError("Limites nao podem ser negativos")

    inatividade = (
        cliente["dias_sem_compra"] >= limite_dias
        and cliente["compras_90d"] == 0
    )

    reclamacoes = (
        cliente["reclamacoes_90d"] >= limite_reclamacoes
    )

    if inatividade or reclamacoes:
        return "REVISAR_RELACIONAMENTO"

    return "ACOMPANHAMENTO_NORMAL"


def analisar_portfolio(
    clientes,
    catalogo,
    limite_dias=LIMITE_PADRAO,
):
    """Analisa todos os produtos com a mesma interface."""

    resultados = []

    for cliente in clientes:
        resultados.append({
            "cliente_id": cliente["cliente_id"],
            "produto_codigo": cliente["produto_codigo"],
            "produto_nome": resolver_produto(
                cliente["produto_codigo"], catalogo
            ),
            "classificacao": classificar_com_parametros(
                cliente,
                limite_dias=limite_dias,
            ),
        })

    return resultados


def resumir_portfolio(resultados):
    """Produz indicadores por produto."""

    resumo = {}

    for item in resultados:
        codigo = item["produto_codigo"]

        if codigo not in resumo:
            resumo[codigo] = {
                "total": 0,
                "revisar": 0,
                "normal": 0,
            }

        resumo[codigo]["total"] += 1

        if item["classificacao"] == "REVISAR_RELACIONAMENTO":
            resumo[codigo]["revisar"] += 1
        else:
            resumo[codigo]["normal"] += 1

    return resumo


def comparar_hipoteses(clientes, catalogo, limites):
    """Testa limites distintos antes de adotar mudancas."""

    if not limites:
        raise ValueError("Informe ao menos uma hipotese")

    comparacoes = []

    for limite in limites:
        resultados = analisar_portfolio(
            clientes, catalogo, limite
        )

        revisar = sum(
            item["classificacao"] == "REVISAR_RELACIONAMENTO"
            for item in resultados
        )

        comparacoes.append({
            "limite_dias": limite,
            "total": len(resultados),
            "clientes_para_revisao": revisar,
            "percentual_revisao": round(
                100 * revisar / len(resultados), 2
            ) if resultados else 0.0,
        })

    return comparacoes