"""Gera notebook da Aula 08."""

import json
from pathlib import Path


ARQUIVO = Path(
    "notebooks/08_comparando_runs_mlflow.ipynb"
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
            "# Aula 08 - Comparando runs\n"
            "Busca, filtros e ranking pela API MLflow."
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
            "from src.aula08_comparando_runs import (\n"
            "    executar, consultar_experimento,\n"
            "    criar_ranking, buscar_shortlist,\n"
            ")\n"
            "print('MLflow:', mlflow.__version__)\n"
        ),
        celula(
            "markdown",
            "## Consultando runs"
        ),
        celula(
            "code",
            "experimento, runs = consultar_experimento()\n"
            "print('Shape:', runs.shape)\n"
            "display(runs.head())\n"
        ),
        celula(
            "markdown",
            "## Ranking por ROC-AUC"
        ),
        celula(
            "code",
            "ranking, papeis = criar_ranking(runs)\n"
            "display(papeis)\n"
        ),
        celula(
            "markdown",
            "## Shortlist inicial: recall >= 0.70"
        ),
        celula(
            "code",
            "shortlist = buscar_shortlist(\n"
            "    experimento.experiment_id, 0.70\n"
            ")\n"
            "display(shortlist)\n"
        ),
        celula(
            "markdown",
            "## Shortlist rigorosa: recall >= 0.85"
        ),
        celula(
            "code",
            "shortlist_rigorosa = buscar_shortlist(\n"
            "    experimento.experiment_id, 0.85\n"
            ")\n"
            "display(shortlist_rigorosa)\n"
        ),
        celula(
            "markdown",
            "## Salvando ranking e resumo"
        ),
        celula(
            "code",
            "resumo = executar()\n"
            "print('Candidato:', resumo['candidato_campeao'])\n"
            "print('Definitivo:',\n"
            "      resumo['campeao_definitivo_selecionado'])\n"
        ),
        celula(
            "markdown",
            "## Proxima etapa\n"
            "Selecao fundamentada do modelo campeao."
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
