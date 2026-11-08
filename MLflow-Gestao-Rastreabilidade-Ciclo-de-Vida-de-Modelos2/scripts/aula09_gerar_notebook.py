"""Cria notebook da Aula 09."""

import json
from pathlib import Path


ARQUIVO = Path(
    "notebooks/09_organizacao_experimentos.ipynb"
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
            "# Aula 09 - Organizacao de experimentos\n"
            "Tags, hipoteses e checklist de rastreabilidade."
        ),
        celula(
            "code",
            "from pathlib import Path\n"
            "import sys\n"
            "raiz = Path.cwd()\n"
            "if raiz.name == 'notebooks':\n"
            "    raiz = raiz.parent\n"
            "sys.path.insert(0, str(raiz))\n"
            "from src.aula09_organizacao_experimentos import (\n"
            "    executar, COMMON_TAGS, HYPOTHESES,\n"
            "    CHECKLIST, consultar_organizadas,\n"
            ")\n"
        ),
        celula(
            "markdown",
            "## Tags comuns"
        ),
        celula(
            "code",
            "for chave, valor in COMMON_TAGS.items():\n"
            "    print(chave, '=', valor)\n"
        ),
        celula(
            "markdown",
            "## Hipoteses dos candidatos"
        ),
        celula(
            "code",
            "for modelo, hipotese in HYPOTHESES.items():\n"
            "    print(modelo, '-', hipotese)\n"
        ),
        celula(
            "markdown",
            "## Organizando as runs existentes"
        ),
        celula(
            "code",
            "resultado = executar()\n"
            "print('Runs:', resultado['runs_organizadas'])\n"
            "print('Novos treinamentos:',\n"
            "      resultado['novos_treinamentos'])\n"
        ),
        celula(
            "markdown",
            "## Checklist de rastreabilidade"
        ),
        celula(
            "code",
            "for chave, descricao in CHECKLIST.items():\n"
            "    print(chave, ':', descricao)\n"
        ),
        celula(
            "markdown",
            "## Proxima etapa\n"
            "A escolha do campeao sera fundamentada em "
            "criterios tecnicos e operacionais."
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
