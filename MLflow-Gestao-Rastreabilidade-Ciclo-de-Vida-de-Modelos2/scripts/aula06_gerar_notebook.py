"""Gera notebook da Aula 06."""

import json
from pathlib import Path


ARQUIVO = Path(
    "notebooks/06_tags_artefatos_mlflow.ipynb"
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
            "# Aula 06 — Tags e artefatos\n"
            "Tracking manual enriquecido do baseline."
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
            "from src.aula06_tags_artefatos import (\n"
            "    executar,\n"
            "    ARTEFATOS,\n"
            "    TAGS,\n"
            "    PASTA_LOCAL,\n"
            ")\n"
            "print('MLflow:', mlflow.__version__)\n"
        ),
        celula(
            "markdown",
            "## Executando a run com tags e artefatos\n"
            "Uma run ja concluida sera reutilizada."
        ),
        celula(
            "code",
            "relatorio = executar()\n"
            "print('Run ID:', relatorio['run_id'])\n"
            "print('Artefatos:', len(relatorio['artefatos']))\n"
        ),
        celula(
            "markdown",
            "## Tags registradas"
        ),
        celula(
            "code",
            "for chave, valor in relatorio['tags'].items():\n"
            "    print(chave, '=', valor)\n"
        ),
        celula(
            "markdown",
            "## Matriz de confusao, curva ROC e coeficientes"
        ),
        celula(
            "code",
            "from IPython.display import display, Image\n"
            "for nome in [\n"
            "    'matriz_confusao.png',\n"
            "    'curva_roc.png',\n"
            "    'coeficientes_modelo.png',\n"
            "]:\n"
            "    display(Image(filename=str(PASTA_LOCAL / 'plots' / nome)))\n"
        ),
        celula(
            "markdown",
            "## Consultando artefatos na run"
        ),
        celula(
            "code",
            "from mlflow.tracking import MlflowClient\n"
            "from src.aula06_tags_artefatos import (\n"
            "    artefatos_remotos,\n"
            ")\n"
            "client = MlflowClient()\n"
            "for item in sorted(artefatos_remotos(client, relatorio['run_id'])):\n"
            "    print(item)\n"
        ),
        celula(
            "markdown",
            "## Proxima etapa\n"
            "Autolog, novos algoritmos e comparacao de runs."
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
