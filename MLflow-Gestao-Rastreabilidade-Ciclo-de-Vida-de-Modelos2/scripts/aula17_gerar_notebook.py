import json
from pathlib import Path

destino = Path("notebooks/17_mlflow_projects.ipynb")

def celula(tipo, conteudo):
    item = {
        "cell_type": tipo,
        "metadata": {},
        "source": conteudo.splitlines(keepends=True),
    }
    if tipo == "code":
        item.update(execution_count=None, outputs=[])
    return item

notebook = {
    "cells": [
        celula(
            "markdown",
            "# Aula 17 - MLflow Projects\n"
            "Prepare e Train com parametros explicitos."
        ),
        celula(
            "code",
            "import sys\n"
            "from pathlib import Path\n"
            "root = Path.cwd()\n"
            "if root.name == 'notebooks': root = root.parent\n"
            "sys.path.insert(0, str(root))\n"
            "import json\n"
        ),
        celula(
            "markdown",
            "## Entrypoints\n"
            "`mlflow run . -e prepare`\n\n"
            "`mlflow run . -e train`"
        ),
        celula(
            "code",
            "preparo = json.loads(\n"
            "    (root / 'resultados/aula17_prepare.json')\n"
            "    .read_text(encoding='utf-8')\n"
            ")\n"
            "preparo\n"
        ),
        celula(
            "code",
            "treino = json.loads(\n"
            "    (root / 'resultados/aula17_train.json')\n"
            "    .read_text(encoding='utf-8')\n"
            ")\n"
            "treino\n"
        ),
        celula(
            "markdown",
            "## Proxima parte\n"
            "Evaluate e Pipeline encadeado."
        ),
    ],
    "metadata": {
        "kernelspec": {
            "display_name": "Python (MLflow - Alura)",
            "language": "python",
            "name": "mlflow-rastreabilidade",
        }
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
