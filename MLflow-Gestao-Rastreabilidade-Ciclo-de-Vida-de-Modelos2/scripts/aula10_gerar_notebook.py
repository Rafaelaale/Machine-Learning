"""Gera o notebook e as anotacoes da Aula 10."""

import json
from pathlib import Path

destino = Path("notebooks/10_escolha_campeao.ipynb")

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
            "# Aula 10 - Escolha do campeao\n"
            "Politica ponderada e rastreabilidade da decisao."
        ),
        celula(
            "code",
            "import sys\n"
            "from pathlib import Path\n"
            "raiz = Path.cwd()\n"
            "if raiz.name == 'notebooks':\n"
            "    raiz = raiz.parent\n"
            "sys.path.insert(0, str(raiz))\n"
            "from src.aula10_escolha_campeao import (\n"
            "    buscar_candidatos, calcular_ranking,\n"
            "    executar, POLITICA\n"
            ")\n"
        ),
        celula(
            "markdown",
            "## Politica de selecao"
        ),
        celula(
            "code",
            "POLITICA"
        ),
        celula(
            "markdown",
            "## Buscando runs existentes"
        ),
        celula(
            "code",
            "experimento, runs = buscar_candidatos()\n"
            "print('Runs:', runs.shape)\n"
        ),
        celula(
            "markdown",
            "## Matriz de decisao"
        ),
        celula(
            "code",
            "ranking = calcular_ranking(runs)\n"
            "display(ranking)\n"
        ),
        celula(
            "markdown",
            "## Registrando a escolha"
        ),
        celula(
            "code",
            "resultado = executar()\n"
            "print(resultado['champion']['model_name'])\n"
            "print(resultado['model']['model_uri'])\n"
        ),
        celula(
            "markdown",
            "## Proxima etapa\n"
            "Model Registry e versionamento."
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
        json.dumps(notebook, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print("NOTEBOOK CRIADO")
else:
    print("NOTEBOOK PRESERVADO")
