"""Gera o notebook da Aula 14."""

import json
from pathlib import Path

destino = Path(
    "notebooks/14_pyfunc_personalizado.ipynb"
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
            "# Aula 14 - PyFunc personalizado\n"
            "Probabilidade, classe e limiar."
        ),
        celula(
            "code",
            "import sys\n"
            "from pathlib import Path\n"
            "raiz = Path.cwd()\n"
            "if raiz.name == 'notebooks':\n"
            "    raiz = raiz.parent\n"
            "sys.path.insert(0, str(raiz))\n"
            "from src.aula14_pyfunc_personalizado import (\n"
            "    executar, testar_wrapper_local,\n"
            "    testar_registrado, PYFUNC_MODEL_NAME,\n"
            ")\n"
        ),
        celula(
            "markdown",
            "## Testando o wrapper antes do registro"
        ),
        celula(
            "code",
            "entrada, saida = testar_wrapper_local()\n"
            "display(saida)\n"
        ),
        celula(
            "markdown",
            "## Registrando o PyFunc"
        ),
        celula(
            "code",
            "resultado = executar()\n"
            "print(resultado['serving_alias_uri'])\n"
        ),
        celula(
            "markdown",
            "## Testando limiares diferentes"
        ),
        celula(
            "code",
            "padrao, alternativo = testar_registrado(\n"
            "    resultado['serving_alias_uri']\n"
            ")\n"
            "display(padrao)\n"
            "display(alternativo)\n"
        ),
        celula(
            "markdown",
            "## Proxima aula\n"
            "Serving REST e chamadas HTTP."
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
