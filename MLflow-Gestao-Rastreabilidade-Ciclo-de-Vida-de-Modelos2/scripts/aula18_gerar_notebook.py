import json
from pathlib import Path

dest = Path("notebooks/18_pipeline_reproduzivel.ipynb")

def cell(kind, text):
    obj = {
        "cell_type": kind,
        "metadata": {},
        "source": text.splitlines(keepends=True),
    }
    if kind == "code":
        obj.update(execution_count=None, outputs=[])
    return obj

nb = {
    "cells": [
        cell(
            "markdown",
            "# Aula 18 - Pipeline reproduzivel\n"
            "MLflow Projects: prepare, train e evaluate."
        ),
        cell(
            "code",
            "from pathlib import Path\n"
            "import json\n"
            "root = Path.cwd()\n"
            "if root.name == 'notebooks': root = root.parent\n"
            "resumo = json.loads((root / 'resultados/aula18_pipeline.json')"
            ".read_text(encoding='utf-8'))\n"
            "resumo\n"
        ),
        cell(
            "code",
            "print('PARENT:', resumo['parent_run_id'])\n"
            "print('PREPARE:', resumo['prepare_run_id'])\n"
            "print('TRAIN:', resumo['train_run_id'])\n"
            "print('EVALUATE:', resumo['evaluate_run_id'])\n"
        ),
        cell(
            "code",
            "print('MODEL_URI:', resumo['model_uri'])\n"
            "print('METRICAS:', resumo['metrics'])\n"
        ),
        cell(
            "markdown",
            "## Execucao no PowerShell\n"
            "mlflow run . -e pipeline -P model_name=random_forest "
            "-P threshold=0.5 --env-manager local"
        ),
        cell(
            "markdown",
            "## Proxima aula\nArquitetura de MLOps."
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

if dest.exists():
    print("NOTEBOOK PRESERVADO")
else:
    dest.write_text(
        json.dumps(nb, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print("NOTEBOOK CRIADO")
