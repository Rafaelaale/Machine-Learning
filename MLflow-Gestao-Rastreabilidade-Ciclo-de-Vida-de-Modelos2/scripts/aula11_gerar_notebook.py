"""Cria o notebook Jupyter da Aula 11."""

import json
from pathlib import Path


destino = Path(
    "notebooks/11_registry_versoes.ipynb"
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
            "# Aula 11 - Model Registry e versoes\n"
            "Registro, metadados e aliases."
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
            "from mlflow.tracking import MlflowClient\n"
            "from src.aula11_model_registry import (\n"
            "    executar, carregar_decisao,\n"
            "    build_estimator, configurar_registry,\n"
            "    REGISTERED_MODEL_NAME,\n"
            ")\n"
        ),
        celula(
            "markdown",
            "## Recuperando o campeao da Aula 10"
        ),
        celula(
            "code",
            "decisao = carregar_decisao()\n"
            "print(decisao)\n"
        ),
        celula(
            "markdown",
            "## Construindo o estimador"
        ),
        celula(
            "code",
            "estimador = build_estimator(\n"
            "    decisao['model_name']\n"
            ")\n"
            "print(estimador)\n"
        ),
        celula(
            "markdown",
            "## Registro e versionamento"
        ),
        celula(
            "code",
            "resultado = executar()\n"
            "print('Versao:', resultado['version'])\n"
            "print('URI:', resultado['model_uri'])\n"
        ),
        celula(
            "markdown",
            "## Consultando alias candidate"
        ),
        celula(
            "code",
            "cliente = MlflowClient()\n"
            "versao = cliente.get_model_version_by_alias(\n"
            "    REGISTERED_MODEL_NAME,\n"
            "    'candidate',\n"
            ")\n"
            "print('Versao por alias:', versao.version)\n"
        ),
        celula(
            "markdown",
            "## Proxima aula\n"
            "Promocao controlada e inferencia."
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

if not destino.exists():
    destino.write_text(
        json.dumps(
            notebook,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print("NOTEBOOK CRIADO")
else:
    print("NOTEBOOK PRESERVADO")
