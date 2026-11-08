"""Cria notebook Jupyter da Aula 07."""

import json
from pathlib import Path


ARQUIVO = Path(
    "notebooks/07_autolog_comparacao_modelos.ipynb"
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
            "# Aula 07 — Autolog\n"
            "Comparação entre três algoritmos no MLflow."
        ),
        celula(
            "code",
            "from pathlib import Path\n"
            "import sys\n"
            "raiz = Path.cwd()\n"
            "if raiz.name == 'notebooks':\n"
            "    raiz = raiz.parent\n"
            "sys.path.insert(0, str(raiz))\n"
            "import pandas as pd\n"
            "import mlflow\n"
            "from src.aula07_autolog import (\n"
            "    executar,\n"
            "    make_candidates,\n"
            "    make_pipeline,\n"
            "    ARQUIVO_CSV,\n"
            "    EXPERIMENT_NAME,\n"
            ")\n"
            "print('MLflow:', mlflow.__version__)\n"
        ),
        celula(
            "markdown",
            "## Candidatos e pipelines"
        ),
        celula(
            "code",
            "for nome, modelo in make_candidates().items():\n"
            "    print(nome)\n"
            "    print(make_pipeline(modelo))\n"
        ),
        celula(
            "markdown",
            "## Execução com autolog\n"
            "A função verifica runs anteriores para "
            "não repetir treinamentos concluídos."
        ),
        celula(
            "code",
            "resumo = executar()\n"
            "print('Experimento:', resumo['experimento'])\n"
            "print('Runs:', resumo['total_runs'])\n"
        ),
        celula(
            "markdown",
            "## Comparação de resultados"
        ),
        celula(
            "code",
            "tabela = pd.read_csv(ARQUIVO_CSV)\n"
            "display(tabela)\n"
        ),
        celula(
            "markdown",
            "## Ranking por ROC-AUC de teste"
        ),
        celula(
            "code",
            "display(tabela[[\n"
            "    'modelo',\n"
            "    'roc_auc_teste',\n"
            "    'roc_auc_cv_media',\n"
            "    'precision_inadimplente',\n"
            "    'recall_inadimplente',\n"
            "    'f1_inadimplente',\n"
            "]])\n"
        ),
        celula(
            "markdown",
            "## Próxima etapa\n"
            "Consultar as runs por meio da interface "
            "e da API do MLflow."
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
