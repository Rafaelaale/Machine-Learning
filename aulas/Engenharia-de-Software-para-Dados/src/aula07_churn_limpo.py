"""Funcoes limpas para revisao didatica de um modelo de churn."""

import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split


COLUNAS_MODELO = (
    "total_spent",
    "num_orders",
    "days_since_last_purchase",
)

COLUNA_ALVO = "churn"


def carregar_clientes(caminho: str) -> pd.DataFrame:
    """Carrega clientes e verifica a estrutura minima do CSV."""
    clientes = pd.read_csv(caminho, low_memory=False)
    obrigatorias = set(COLUNAS_MODELO) | {COLUNA_ALVO}
    ausentes = obrigatorias - set(clientes.columns)

    if ausentes:
        raise ValueError(
            "Colunas obrigatorias ausentes: "
            + ", ".join(sorted(ausentes))
        )

    return clientes


def preparar_dados(clientes: pd.DataFrame) -> pd.DataFrame:
    """Seleciona, valida e organiza os atributos e o alvo.

    Descarta registros incompletos apenas para o laboratorio.
    O tratamento adequado deve ser analisado antes da producao.
    """
    obrigatorias = list(COLUNAS_MODELO) + [COLUNA_ALVO]
    ausentes = set(obrigatorias) - set(clientes.columns)

    if ausentes:
        raise ValueError(
            "Colunas ausentes: " + ", ".join(sorted(ausentes))
        )

    dados_modelo = clientes.loc[:, obrigatorias].copy()

    for coluna in COLUNAS_MODELO:
        dados_modelo[coluna] = pd.to_numeric(
            dados_modelo[coluna],
            errors="coerce",
        )

    alvo = dados_modelo[COLUNA_ALVO]

    if not pd.api.types.is_numeric_dtype(alvo):
        valores = (
            alvo.astype("string")
            .str.strip()
            .str.lower()
        )

        alvo = valores.map({
            "yes": 1,
            "no": 0,
            "sim": 1,
            "nao": 0,
            "não": 0,
            "true": 1,
            "false": 0,
            "1": 1,
            "0": 0,
        })

    dados_modelo[COLUNA_ALVO] = pd.to_numeric(
        alvo, errors="coerce"
    )

    dados_modelo = dados_modelo.dropna().copy()

    if dados_modelo.empty:
        raise ValueError("Nao ha dados validos para modelagem")

    classes = set(dados_modelo[COLUNA_ALVO].unique())

    if not classes.issubset({0, 1}):
        raise ValueError("Churn precisa conter classes 0 e 1")

    dados_modelo[COLUNA_ALVO] = (
        dados_modelo[COLUNA_ALVO].astype(int)
    )

    return dados_modelo


def separar_treino_teste(
    dados_modelo: pd.DataFrame,
    proporcao_teste: float = 0.25,
    semente: int = 42,
):
    """Divide atributos e alvo de maneira reproduzivel."""
    if not 0 < proporcao_teste < 1:
        raise ValueError("Proporcao de teste invalida")

    atributos = dados_modelo.loc[:, COLUNAS_MODELO]
    alvo = dados_modelo[COLUNA_ALVO]

    contagens = alvo.value_counts()

    if len(contagens) != 2:
        raise ValueError("Treinamento requer duas classes")

    if contagens.min() < 2:
        raise ValueError("Cada classe deve ter duas amostras")

    return train_test_split(
        atributos,
        alvo,
        test_size=proporcao_teste,
        random_state=semente,
        stratify=alvo,
    )


def treinar_regressao_logistica(
    atributos_treino: pd.DataFrame,
    alvo_treino: pd.Series,
) -> LogisticRegression:
    """Treina um classificador com configuracao explicita."""
    modelo = LogisticRegression(
        max_iter=1000,
        random_state=42,
    )

    modelo.fit(atributos_treino, alvo_treino)

    return modelo


def avaliar_modelo(
    modelo: LogisticRegression,
    atributos_teste: pd.DataFrame,
    alvo_teste: pd.Series,
) -> dict:
    """Calcula metricas de classificacao no conjunto de teste."""
    previsoes = modelo.predict(atributos_teste)

    return classification_report(
        alvo_teste,
        previsoes,
        labels=[0, 1],
        output_dict=True,
        zero_division=0,
    )


def executar_pipeline(clientes: pd.DataFrame) -> dict:
    """Orquestra as etapas sem misturar responsabilidades."""
    dados_modelo = preparar_dados(clientes)

    (
        atributos_treino,
        atributos_teste,
        alvo_treino,
        alvo_teste,
    ) = separar_treino_teste(dados_modelo)

    modelo = treinar_regressao_logistica(
        atributos_treino,
        alvo_treino,
    )

    metricas = avaliar_modelo(
        modelo,
        atributos_teste,
        alvo_teste,
    )

    return {
        "registros_utilizados": len(dados_modelo),
        "registros_treino": len(atributos_treino),
        "registros_teste": len(atributos_teste),
        "atributos": list(COLUNAS_MODELO),
        "distribuicao_churn": {
            str(chave): int(valor)
            for chave, valor in (
                dados_modelo[COLUNA_ALVO]
                .value_counts()
                .items()
            )
        },
        "metricas": metricas,
    }
