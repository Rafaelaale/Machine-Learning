"""Funcoes didaticas de analise de clientes.

Principios:
1. Razao de existir
2. KISS
3. Manter a visao

Nao e um modelo treinado de Machine Learning.
"""

import csv
from pathlib import Path


CAMPOS = (
    "cliente_id",
    "dias_sem_compra",
    "compras_90d",
    "reclamacoes_90d",
    "valor_total",
)


def carregar_clientes(caminho):
    """Carrega dados uma unica vez, sem duplicar leitura."""

    caminho = Path(caminho)

    with caminho.open(
        "r", newline="", encoding="utf-8-sig"
    ) as arquivo:
        leitor = csv.DictReader(arquivo)

        if not set(CAMPOS).issubset(leitor.fieldnames or []):
            raise ValueError("Colunas obrigatorias ausentes")

        return [validar_cliente(linha) for linha in leitor]


def validar_cliente(linha):
    """Valida e converte os dados de um cliente."""

    cliente_id = str(linha["cliente_id"]).strip()

    if not cliente_id:
        raise ValueError("Identificador vazio")

    cliente = {
        "cliente_id": cliente_id,
        "dias_sem_compra": int(linha["dias_sem_compra"]),
        "compras_90d": int(linha["compras_90d"]),
        "reclamacoes_90d": int(linha["reclamacoes_90d"]),
        "valor_total": float(linha["valor_total"]),
    }

    for campo in (
        "dias_sem_compra",
        "compras_90d",
        "reclamacoes_90d",
        "valor_total",
    ):
        if cliente[campo] < 0:
            raise ValueError(
                f"Valor negativo em {campo}"
            )

    return cliente


def classificar_atencao(cliente):
    """Regra ilustrativa para priorizar analise humana.

    Nao calcula uma probabilidade de churn.
    """

    sem_compras_recentes = (
        cliente["dias_sem_compra"] >= 60
        and cliente["compras_90d"] == 0
    )

    muitas_reclamacoes = (
        cliente["reclamacoes_90d"] >= 2
    )

    if sem_compras_recentes or muitas_reclamacoes:
        return "REVISAR_RELACIONAMENTO"

    return "ACOMPANHAMENTO_NORMAL"


def analisar_clientes(clientes):
    """Aplica uma unica regra central a todos os clientes."""

    resultado = []

    for cliente in clientes:
        resultado.append({
            **cliente,
            "classificacao": classificar_atencao(cliente),
        })

    return resultado


def resumir(resultados):
    total = len(resultados)
    revisar = sum(
        item["classificacao"] == "REVISAR_RELACIONAMENTO"
        for item in resultados
    )

    return {
        "total_clientes": total,
        "clientes_para_revisao": revisar,
        "acompanhamento_normal": total - revisar,
        "percentual_revisao": (
            round(100 * revisar / total, 2)
            if total else 0.0
        ),
    }