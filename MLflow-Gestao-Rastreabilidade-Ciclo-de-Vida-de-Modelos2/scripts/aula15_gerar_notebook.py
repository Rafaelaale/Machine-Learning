"""Gera o notebook da Aula 15."""

import json
from pathlib import Path

destino = Path(
    "notebooks/15_serving_rest.ipynb"
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
            "# Aula 15 - Serving via REST\n"
            "Testes HTTP com MLflow e PyFunc."
        ),
        celula(
            "code",
            "import sys\n"
            "from pathlib import Path\n"
            "raiz = Path.cwd()\n"
            "if raiz.name == 'notebooks':\n"
            "    raiz = raiz.parent\n"
            "sys.path.insert(0, str(raiz))\n"
            "from src.aula15_serving_rest import (\n"
            "    MODEL_URI, criar_payload,\n"
            "    verificar_health, chamar_api,\n"
            "    extrair_predicao, executar,\n"
            ")\n"
        ),
        celula(
            "markdown",
            "## Modelo servido"
        ),
        celula(
            "code",
            "print(MODEL_URI)\n"
        ),
        celula(
            "markdown",
            "## Health checks"
        ),
        celula(
            "code",
            "print(verificar_health())\n"
        ),
        celula(
            "markdown",
            "## Payload valido"
        ),
        celula(
            "code",
            "payload = criar_payload(0.30)\n"
            "print(payload)\n"
        ),
        celula(
            "markdown",
            "## Inferencia HTTP"
        ),
        celula(
            "code",
            "resposta = chamar_api(payload)\n"
            "print(extrair_predicao(resposta))\n"
        ),
        celula(
            "markdown",
            "## Erro de coluna obrigatoria"
        ),
        celula(
            "code",
            "invalido = criar_payload(\n"
            "    remover_coluna='score_interno'\n"
            ")\n"
            "print(chamar_api(invalido))\n"
        ),
        celula(
            "markdown",
            "## Auditoria completa"
        ),
        celula(
            "code",
            "resultado = executar()\n"
            "print(resultado['previsoes'])\n"
        ),
        celula(
            "markdown",
            "## Proxima aula\n"
            "Docker e smoke tests do serving."
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
