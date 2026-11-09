import json
from pathlib import Path

destino = Path("notebooks/03_arquitetura_kubeflow.ipynb")


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
            "# Aula 03 - Arquitetura do Kubeflow\n"
            "Notebooks, KFP, Katib, Trainer e KServe.\n",
        ),
        celula(
            "markdown",
            "## Kubeflow Pipelines\n"
            "Uma pipeline conecta componentes com entradas "
            "e saidas declaradas.\n",
        ),
        celula(
            "code",
            "from pathlib import Path\n"
            "root = Path.cwd()\n"
            "if root.name == 'notebooks':\n"
            "    root = root.parent\n"
            "arquivo = root / 'pipelines/aula03_arquitetura_kfp.py'\n"
            "print(arquivo.read_text(encoding='utf-8'))\n",
        ),
        celula(
            "markdown",
            "## Componentes\n"
            "- Notebooks: exploracao\n"
            "- KFP: orquestracao\n"
            "- Katib: otimizacao (depreciado na documentacao atual)\n"
            "- Trainer: treinamento\n"
            "- KServe: inferencia\n",
        ),
        celula(
            "markdown",
            "## Validacao\n"
            "A compilacao do exemplo exige o SDK kfp instalado.\n"
            "Os testes desta aula validam a estrutura do codigo.\n",
        ),
    ],
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        }
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}

if destino.exists():
    print("NOTEBOOK EXISTENTE PRESERVADO")
else:
    destino.write_text(
        json.dumps(notebook, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print("NOTEBOOK CRIADO:", destino)
