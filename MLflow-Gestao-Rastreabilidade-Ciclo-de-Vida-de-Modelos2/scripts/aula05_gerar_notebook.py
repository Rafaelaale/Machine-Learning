"""Gera notebook da Aula 05."""

import json
from pathlib import Path


ARQUIVO = Path(
    "notebooks/05_logging_manual_mlflow.ipynb"
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
            "# Aula 05 — Logging manual no MLflow\n"
            "Segunda run do experimento de risco de crédito."
        ),
        celula(
            "code",
            "import sys\n"
            "from pathlib import Path\n"
            "raiz = Path.cwd()\n"
            "if raiz.name == 'notebooks':\n"
            "    raiz = raiz.parent\n"
            "sys.path.insert(0, str(raiz))\n"
            "import mlflow\n"
            "from src.aula05_logging_manual import (\n"
            "    configurar_tracking,\n"
            "    carregar_dados,\n"
            "    construir_pipeline,\n"
            "    executar,\n"
            "    RUN_NAME,\n"
            ")\n"
            "configurar_tracking()\n"
            "print('MLflow:', mlflow.__version__)\n"
        ),
        celula(
            "markdown",
            "## Treinamento e logging manual\n"
            "Esta função cria a run uma vez e verifica "
            "o registro em execuções posteriores."
        ),
        celula(
            "code",
            "relatorio = executar()\n"
            "print('Run ID:', relatorio['run_id'])\n"
            "print('Parâmetros:', len(relatorio['params']))\n"
            "print('Métricas:', len(relatorio['metrics']))\n"
        ),
        celula(
            "markdown",
            "## Parâmetros registrados"
        ),
        celula(
            "code",
            "for chave, valor in relatorio['params'].items():\n"
            "    print(chave, ':', valor)\n"
        ),
        celula(
            "markdown",
            "## Métricas e matriz de confusão"
        ),
        celula(
            "code",
            "for chave, valor in relatorio['metrics'].items():\n"
            "    print(chave, ':', valor)\n"
        ),
        celula(
            "markdown",
            "## Consultando a run pelo cliente MLflow"
        ),
        celula(
            "code",
            "from mlflow.tracking import MlflowClient\n"
            "run = MlflowClient().get_run(relatorio['run_id'])\n"
            "print('Status:', run.info.status)\n"
            "print('Run:', run.data.tags['mlflow.runName'])\n"
        ),
        celula(
            "markdown",
            "## Próxima etapa\n"
            "Adicionar tags e artefatos, incluindo "
            "gráficos e relatórios de classificação."
        ),
    ],
    "metadata": {
        "kernelspec": {
            "display_name": "Python (MLflow - Alura)",
            "language": "python",
            "name": "mlflow-rastreabilidade",
        },
        "language_info": {
            "name": "python",
        },
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
