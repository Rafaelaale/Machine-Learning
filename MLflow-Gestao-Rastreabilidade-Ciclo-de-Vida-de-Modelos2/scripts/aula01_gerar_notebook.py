"""Cria o notebook da Aula 01."""

from pathlib import Path
import json


ARQUIVO = Path(
    "notebooks/01_apresentando_problema_mlflow.ipynb"
)


def markdown(texto):
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": texto.splitlines(keepends=True),
    }


def codigo(texto):
    return {
        "cell_type": "code",
        "metadata": {},
        "execution_count": None,
        "outputs": [],
        "source": texto.splitlines(keepends=True),
    }


notebook = {
    "cells": [
        markdown(
            "# Aula 01 — Apresentando o problema\n"
            "## Reprodutibilidade de modelos de Machine Learning\n"
            "Projeto: classificação de risco de crédito."
        ),
        markdown(
            "## O problema\n"
            "Sem rastreabilidade, perdemos o histórico de "
            "parâmetros, métricas, artefatos e modelos."
        ),
        codigo(
            "from pathlib import Path\n"
            "import sys\n"
            "raiz = Path.cwd()\n"
            "if raiz.name == 'notebooks':\n"
            "    raiz = raiz.parent\n"
            "sys.path.insert(0, str(raiz))\n"
            "from src.aula01_conceitos_mlflow import CONCEITOS\n"
            "for chave, valor in CONCEITOS.items():\n"
            "    print(f'{chave}: {valor}')\n"
        ),
        markdown(
            "## Critérios de sucesso\n"
            "1. Desempenho técnico.\n"
            "2. Reprodutibilidade.\n"
            "3. Operacionalização."
        ),
        markdown(
            "## Próxima aula\n"
            "Preparação do ambiente, análise dos dados "
            "e criação do primeiro baseline."
        ),
    ],
    "metadata": {
        "kernelspec": {
            "display_name": "Python (.venv)",
            "language": "python",
            "name": "python3",
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
            notebook, ensure_ascii=False, indent=2
        ),
        encoding="utf-8",
    )
    print("NOTEBOOK CRIADO")
