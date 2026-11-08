"""Gera o notebook da Aula 13."""

import json
from pathlib import Path

destino = Path(
    "notebooks/13_formato_mlmodel.ipynb"
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
            "# Aula 13 - Formato MLmodel\n"
            "Flavors, signature e validacao de entrada."
        ),
        celula(
            "code",
            "import sys\n"
            "from pathlib import Path\n"
            "raiz = Path.cwd()\n"
            "if raiz.name == 'notebooks':\n"
            "    raiz = raiz.parent\n"
            "sys.path.insert(0, str(raiz))\n"
            "from src.aula13_formato_mlmodel import (\n"
            "    executar, baixar_modelo,\n"
            "    inspecionar_pacote,\n"
            "    inspecionar_contrato,\n"
            "    validar_flavors,\n"
            "    validar_cenarios,\n"
            "    MODEL_URI,\n"
            ")\n"
        ),
        celula(
            "markdown",
            "## URI production"
        ),
        celula(
            "code",
            "print(MODEL_URI)\n"
        ),
        celula(
            "markdown",
            "## Baixando e inspecionando o pacote"
        ),
        celula(
            "code",
            "pasta = baixar_modelo()\n"
            "pacote = inspecionar_pacote(pasta)\n"
            "for item in pacote['inventario']:\n"
            "    print(item['arquivo'])\n"
        ),
        celula(
            "markdown",
            "## Flavors e assinatura"
        ),
        celula(
            "code",
            "print(pacote['flavors'])\n"
            "print(inspecionar_contrato())\n"
        ),
        celula(
            "markdown",
            "## Comparando sklearn e pyfunc"
        ),
        celula(
            "code",
            "print(validar_flavors())\n"
        ),
        celula(
            "markdown",
            "## Entradas validas e invalidas"
        ),
        celula(
            "code",
            "print(validar_cenarios())\n"
        ),
        celula(
            "markdown",
            "## Salvando resultados"
        ),
        celula(
            "code",
            "resultado = executar()\n"
            "print('Arquivos:', resultado['total_arquivos'])\n"
        ),
        celula(
            "markdown",
            "## Proxima aula\n"
            "PyFunc personalizado e contrato de inferencia."
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
