"""Gera notebook da Aula 12."""

import json
from pathlib import Path

destino = Path(
    "notebooks/12_promocao_modelos.ipynb"
)


def celula(tipo, conteudo):
    item = {
        "cell_type": tipo,
        "metadata": {},
        "source": conteudo.splitlines(keepends=True),
    }

    if tipo == "code":
        item["execution_count"] = None
        item["outputs"] = []

    return item


notebook = {
    "cells": [
        celula(
            "markdown",
            "# Aula 12 - Promovendo modelos\n"
            "Staging, production, aliases e inferencia."
        ),
        celula(
            "code",
            "import sys\n"
            "from pathlib import Path\n"
            "raiz = Path.cwd()\n"
            "if raiz.name == 'notebooks':\n"
            "    raiz = raiz.parent\n"
            "sys.path.insert(0, str(raiz))\n"
            "from src.aula12_promovendo_modelos import (\n"
            "    executar, novo_cliente,\n"
            "    validar_inferencia, configurar_registry,\n"
            "    REGISTERED_MODEL_NAME,\n"
            ")\n"
        ),
        celula(
            "markdown",
            "## Cliente sintetico"
        ),
        celula(
            "code",
            "cliente = novo_cliente()\n"
            "display(cliente)\n"
        ),
        celula(
            "markdown",
            "## Promocao didatica"
        ),
        celula(
            "code",
            "resultado = executar()\n"
            "print(resultado['production_uri'])\n"
        ),
        celula(
            "markdown",
            "## Consultando aliases"
        ),
        celula(
            "code",
            "client, _ = configurar_registry()\n"
            "for alias in ['candidate', 'staging',\n"
            "              'production', 'champion']:\n"
            "    v = client.get_model_version_by_alias(\n"
            "        REGISTERED_MODEL_NAME, alias\n"
            "    )\n"
            "    print(alias, '=>', v.version)\n"
        ),
        celula(
            "markdown",
            "## Inferencia por production"
        ),
        celula(
            "code",
            "predicao = validar_inferencia(\n"
            "    resultado['production_uri'], cliente\n"
            ")\n"
            "print(predicao)\n"
        ),
        celula(
            "markdown",
            "## Rollback\n"
            "Reversao por alias exige uma versao "
            "anterior existente e aprovada.\n"
            "Nenhum rollback e executado nesta aula."
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

if destino.exists():
    print("NOTEBOOK PRESERVADO")
else:
    destino.write_text(
        json.dumps(
            notebook,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print("NOTEBOOK CRIADO")
