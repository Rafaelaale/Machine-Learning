"""Helpers para o pipeline de vendas da Vende+."""

import os
from pathlib import Path

import pandas as pd


COLUNAS_ESPERADAS = [
    "data",
    "pedido_id",
    "produto",
    "categoria",
    "quantidade",
    "valor_unitario",
]


def extrair_vendas(caminho_arquivo: str) -> dict:
    """Lê o CSV de vendas e valida sua estrutura.

    Args:
        caminho_arquivo: caminho absoluto do CSV de entrada.

    Returns:
        Dicionário com caminho do arquivo e contagem de linhas processadas.

    Raises:
        FileNotFoundError: se o arquivo não existir.
        ValueError: se o arquivo estiver vazio ou com colunas faltando.
    """
    if not os.path.exists(caminho_arquivo):
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho_arquivo}")

    df = pd.read_csv(caminho_arquivo)

    if df.empty:
        raise ValueError(f"Arquivo vazio: {caminho_arquivo}")

    colunas_faltando = set(COLUNAS_ESPERADAS) - set(df.columns)
    if colunas_faltando:
        raise ValueError(f"Colunas faltando no arquivo: {colunas_faltando}")

    return {
        "caminho": caminho_arquivo,
        "linhas": len(df),
    }


def transformar_vendas(caminho_entrada: str, caminho_saida: str) -> str:
    """Agrupa vendas por categoria e calcula métricas.

    Args:
        caminho_entrada: caminho do CSV de entrada.
        caminho_saida: caminho onde o CSV transformado será salvo.

    Returns:
        Caminho do arquivo transformado.
    """
    df = pd.read_csv(caminho_entrada)

    df["valor_total"] = df["quantidade"] * df["valor_unitario"]

    resumo = (
        df.groupby("categoria")
        .agg(
            total_pedidos=("pedido_id", "count"),
            valor_total_brl=("valor_total", "sum"),
        )
        .reset_index()
    )

    resumo["ticket_medio_brl"] = (
        resumo["valor_total_brl"] / resumo["total_pedidos"]
    ).round(2)
    resumo["valor_total_brl"] = resumo["valor_total_brl"].round(2)

    Path(caminho_saida).parent.mkdir(parents=True, exist_ok=True)
    resumo.to_csv(caminho_saida, index=False)

    return caminho_saida


def carregar_resumo(caminho_transformado: str, caminho_final: str) -> str:
    """Move o resumo transformado para o destino final.

    Args:
        caminho_transformado: caminho do arquivo já transformado.
        caminho_final: caminho final onde o resumo deve ficar.

    Returns:
        Caminho final do arquivo.
    """
    Path(caminho_final).parent.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(caminho_transformado)
    df.to_csv(caminho_final, index=False)

    return caminho_final
