"""Pre-processamento de pedidos com boas praticas.

Aula 06 - Engenharia de Software para Dados.

Conceitos aplicados:
- PEP 8.
- Nomes descritivos.
- Funcoes pequenas.
- Docstrings e type hints.
- Pipeline reutilizavel.
- Preservacao dos dados de entrada.
"""

import pandas as pd


COLUNAS_OBRIGATORIAS = {
    "quantidade_pedida",
    "categoria",
    "data_pedido",
    "valor_compra",
}


def validar_colunas(df: pd.DataFrame) -> None:
    """Verifica as colunas obrigatorias do processamento."""
    ausentes = COLUNAS_OBRIGATORIAS - set(df.columns)

    if ausentes:
        raise ValueError(
            "Colunas ausentes: " + ", ".join(sorted(ausentes))
        )


def preencher_valores_ausentes(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Preenche quantidade ausente e categoria desconhecida.

    Parametros:
        df: DataFrame com dados de pedidos.

    Retorno:
        Copia do DataFrame com valores preenchidos.
    """
    resultado = df.copy()

    resultado["quantidade_pedida"] = pd.to_numeric(
        resultado["quantidade_pedida"], errors="raise"
    ).fillna(0)

    resultado["categoria"] = (
        resultado["categoria"].fillna("desconhecido")
    )

    return resultado


def calcular_tempo_do_pedido(
    df: pd.DataFrame,
    ano_referencia: int,
) -> pd.DataFrame:
    """Calcula a idade dos pedidos em anos inteiros.

    Parametros:
        df: DataFrame contendo a coluna data_pedido.
        ano_referencia: Ano escolhido para a analise.

    Retorno:
        Copia com a coluna tempo_pedido_anos.
    """
    if not isinstance(ano_referencia, int):
        raise TypeError("Ano de referencia deve ser inteiro")

    resultado = df.copy()

    datas = pd.to_datetime(
        resultado["data_pedido"], errors="raise"
    )

    resultado["tempo_pedido_anos"] = (
        ano_referencia - datas.dt.year
    )

    if (resultado["tempo_pedido_anos"] < 0).any():
        raise ValueError(
            "Existem pedidos posteriores ao ano de referencia"
        )

    return resultado


def normalizar_valor_da_compra(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Aplica normalizacao min-max ao valor da compra.

    Quando todos os valores sao iguais, retorna
    zero para evitar divisao por zero.

    Observacao:
        O minimo e o maximo sao calculados neste
        DataFrame. Em ML real, os parametros devem
        ser aprendidos no treino e aplicados no teste.
    """
    resultado = df.copy()

    valores = pd.to_numeric(
        resultado["valor_compra"], errors="raise"
    )

    if valores.isna().any():
        raise ValueError("Valor de compra ausente")

    valor_min = valores.min()
    valor_max = valores.max()

    if len(resultado) == 0:
        resultado["valor_compra_normalizado"] = (
            pd.Series(dtype=float)
        )
    elif valor_max == valor_min:
        resultado["valor_compra_normalizado"] = 0.0
    else:
        resultado["valor_compra_normalizado"] = (
            (valores - valor_min)
            / (valor_max - valor_min)
        )

    return resultado


def preprocessar_pedidos(
    df: pd.DataFrame,
    ano_referencia: int = 2026,
) -> pd.DataFrame:
    """Executa o pipeline completo de pre-processamento.

    Parametros:
        df: Pedidos originados de dados ficticios.
        ano_referencia: Ano usado no calculo temporal.

    Retorno:
        Novo DataFrame processado, sem alterar
        o objeto original.
    """
    validar_colunas(df)

    resultado = df.copy()

    resultado = preencher_valores_ausentes(resultado)

    resultado = calcular_tempo_do_pedido(
        resultado, ano_referencia
    )

    resultado = normalizar_valor_da_compra(resultado)

    return resultado