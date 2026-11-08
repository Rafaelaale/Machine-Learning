"""Gerador do notebook da Aula 02."""

import json
from pathlib import Path


ARQUIVO = Path(
    "notebooks/02_projeto_base_mlflow.ipynb"
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
            "# Aula 02 — Projeto base\n"
            "## Componentes e fundamentos do MLflow\n"
            "Projeto: classificacao de risco de credito."
        ),
        celula(
            "markdown",
            "## Experimentos e runs\n"
            "Um experimento agrupa runs relacionadas.\n"
            "Cada run representa uma execucao especifica."
        ),
        celula(
            "code",
            "from pathlib import Path\n"
            "import sys\n"
            "raiz = Path.cwd()\n"
            "if raiz.name == 'notebooks':\n"
            "    raiz = raiz.parent\n"
            "sys.path.insert(0, str(raiz))\n"
            "from src.aula02_projeto_base_mlflow import (\n"
            "    COMPONENTES,\n"
            "    EXPERIMENTOS_EXEMPLO,\n"
            "    diferenciar_registros,\n"
            ")\n"
            "for nome, detalhe in COMPONENTES.items():\n"
            "    print(nome, '-', detalhe['objetivo'])"
        ),
        celula(
            "markdown",
            "## Parametros, metricas e artefatos"
        ),
        celula(
            "code",
            "for tipo, descricao in diferenciar_registros().items():\n"
            "    print(tipo, ':', descricao)\n"
            "print('Experimentos de exemplo:', EXPERIMENTOS_EXEMPLO)"
        ),
        celula(
            "markdown",
            "## Proxima etapa\n"
            "Configurar MLflow, analisar o dataset "
            "e registrar o primeiro baseline.\n"
            "Ainda nao criamos runs nem treinamos modelos."
        ),
    ],
    "metadata": {
        "kernelspec": {
            "display_name": "Python (.venv)",
            "language": "python",
            "name": "python3",
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
