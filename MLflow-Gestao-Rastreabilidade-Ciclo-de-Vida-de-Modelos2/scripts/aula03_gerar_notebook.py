"""Cria notebook Jupyter da Aula 03."""

import json
from pathlib import Path


ARQUIVO = Path(
    "notebooks/03_ambiente_dataset_baseline.ipynb"
)


def celula(tipo, texto):
    item = {
        "cell_type": tipo,
        "metadata": {},
        "source": texto.splitlines(keepends=True),
    }

    if tipo == "code":
        item["execution_count"] = None
        item["outputs"] = []

    return item


notebook = {
    "cells": [
        celula(
            "markdown",
            "# Aula 03 — Ambiente, dataset e baseline\n"
            "Projeto de classificação de risco de crédito."
        ),
        celula(
            "code",
            "from pathlib import Path\n"
            "import sys\n"
            "raiz = Path.cwd()\n"
            "if raiz.name == 'notebooks':\n"
            "    raiz = raiz.parent\n"
            "sys.path.insert(0, str(raiz))\n"
            "import numpy as np\n"
            "import pandas as pd\n"
            "import matplotlib.pyplot as plt\n"
            "from src.aula03_ambiente_dataset import (\n"
            "    gerar_base_credito,\n"
            "    preparar_divisao,\n"
            "    construir_pipeline,\n"
            "    TARGET,\n"
            "    FEATURES,\n"
            "    NUM_COLS,\n"
            "    CAT_COLS,\n"
            "    RANDOM_STATE,\n"
            ")\n"
            "np.random.seed(RANDOM_STATE)\n"
        ),
        celula(
            "markdown",
            "## Gerando 6000 registros sintéticos"
        ),
        celula(
            "code",
            "df = gerar_base_credito(6000)\n"
            "display(df.head())\n"
            "display(df.tail())\n"
            "print('Dimensões:', df.shape)\n"
        ),
        celula(
            "markdown",
            "## Distribuição da variável inadimplente"
        ),
        celula(
            "code",
            "display(df[TARGET].value_counts())\n"
            "display(df[TARGET].value_counts(normalize=True))\n"
        ),
        celula(
            "markdown",
            "## Exploração: score interno e renda"
        ),
        celula(
            "code",
            "fig, axes = plt.subplots(1, 2, figsize=(12, 4))\n"
            "for ax, coluna in zip(axes, ['score_interno', 'renda_mensal']):\n"
            "    df.boxplot(column=coluna, by=TARGET, ax=ax)\n"
            "    ax.set_title(coluna)\n"
            "    ax.set_xlabel('inadimplente')\n"
            "plt.suptitle('')\n"
            "plt.tight_layout()\n"
            "plt.show()\n"
        ),
        celula(
            "markdown",
            "## Separação estratificada em treino e teste"
        ),
        celula(
            "code",
            "X = df[FEATURES]\n"
            "y = df[TARGET]\n"
            "X_train, X_test, y_train, y_test = preparar_divisao(df)\n"
            "print('Treino:', X_train.shape, y_train.shape)\n"
            "print('Teste:', X_test.shape, y_test.shape)\n"
        ),
        celula(
            "markdown",
            "## Pipeline de pré-processamento e baseline"
        ),
        celula(
            "code",
            "model_pipe = construir_pipeline()\n"
            "print(model_pipe)\n"
            "print('Modelo treinado:', hasattr(\n"
            "    model_pipe.named_steps['model'], 'coef_'\n"
            "))\n"
        ),
        celula(
            "markdown",
            "## Próxima etapa\n"
            "Treinar a regressão logística e registrar "
            "a primeira execução no MLflow.\n"
            "O pipeline desta aula ainda não foi treinado."
        ),
    ],
    "metadata": {
        "kernelspec": {
            "display_name": "Python (MLflow - Alura)",
            "language": "python",
            "name": "mlflow-rastreabilidade",
        },
        "language_info": {"name": "python"},
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}

if ARQUIVO.exists():
    print("NOTEBOOK PRESERVADO")
else:
    ARQUIVO.write_text(
        json.dumps(
            notebook,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print("NOTEBOOK CRIADO")
