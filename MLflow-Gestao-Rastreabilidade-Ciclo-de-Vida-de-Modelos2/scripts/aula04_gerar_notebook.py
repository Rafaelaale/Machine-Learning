"""Gera notebook da primeira run MLflow."""

import json
from pathlib import Path


ARQUIVO = Path(
    "notebooks/04_primeira_run_mlflow.ipynb"
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
            "# Aula 04 — Primeira run MLflow\n"
            "Baseline de regressão logística para risco de crédito."
        ),
        celula(
            "code",
            "from pathlib import Path\n"
            "import sys\n"
            "raiz = Path.cwd()\n"
            "if raiz.name == 'notebooks':\n"
            "    raiz = raiz.parent\n"
            "sys.path.insert(0, str(raiz))\n"
            "import mlflow\n"
            "import pandas as pd\n"
            "from src.aula04_primeira_run_mlflow import (\n"
            "    configurar_tracking,\n"
            "    carregar_dados,\n"
            "    construir_pipeline,\n"
            "    novo_cliente,\n"
            "    executar_aula,\n"
            ")\n"
            "print('MLflow:', mlflow.__version__)\n"
            "print('Tracking:', configurar_tracking())\n"
        ),
        celula(
            "markdown",
            "## Dados e pipeline preparados"
        ),
        celula(
            "code",
            "base, X_train, X_test, y_train, y_test = carregar_dados()\n"
            "print('Treino:', X_train.shape)\n"
            "print('Teste:', X_test.shape)\n"
            "print(construir_pipeline())\n"
        ),
        celula(
            "markdown",
            "## Executando o baseline rastreado\n"
            "A função evita duplicar uma run já registrada."
        ),
        celula(
            "code",
            "relatorio = executar_aula()\n"
            "print('Run ID:', relatorio['run_id'])\n"
            "print('Experimento:', relatorio['experimento'])\n"
        ),
        celula(
            "markdown",
            "## Métricas do experimento"
        ),
        celula(
            "code",
            "display(pd.DataFrame([\n"
            "    relatorio['metricas']\n"
            "]).T.rename(columns={0: 'valor'}))\n"
        ),
        celula(
            "markdown",
            "## Cliente simulado"
        ),
        celula(
            "code",
            "display(novo_cliente())\n"
            "print('Probabilidade:',\n"
            "      f\"{relatorio['simulacao_cliente']['probabilidade_inadimplencia']:.2%}\")\n"
            "print('Classe:',\n"
            "      relatorio['simulacao_cliente']['classe_prevista'])\n"
        ),
        celula(
            "markdown",
            "## Interface MLflow\n"
            "Abra `http://localhost:5000` após iniciar "
            "o servidor de rastreamento.\n"
            "A próxima aula adicionará tags e artefatos."
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
