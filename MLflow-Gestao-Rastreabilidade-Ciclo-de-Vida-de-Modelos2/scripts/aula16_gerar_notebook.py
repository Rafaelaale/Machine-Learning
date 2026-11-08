import json
from pathlib import Path

path = Path("notebooks/16_docker_smoke.ipynb")
if not path.exists():
    def cell(kind, source):
        c = {"cell_type": kind, "metadata": {},
             "source": source.splitlines(keepends=True)}
        if kind == "code":
            c.update(execution_count=None, outputs=[])
        return c

    notebook = {
        "cells": [
            cell("markdown", "# Aula 16 - Docker e smoke tests\n"
                 "Imagem Docker, contrato REST e testes de regressao."),
            cell("code",
                 "import sys\nfrom pathlib import Path\n"
                 "root = Path.cwd()\n"
                 "if root.name == 'notebooks': root = root.parent\n"
                 "sys.path.insert(0, str(root))\n"
                 "from src.aula16_docker_smoke import payload, health, predict, invalid_input, executar\n"),
            cell("code", "health()"),
            cell("code", "payload(0.3)"),
            cell("code", "predict(0.3)"),
            cell("code", "invalid_input()"),
            cell("code", "executar()"),
            cell("markdown", "## Proxima aula\nMLflow Projects e entry points."),
        ],
        "metadata": {
            "kernelspec": {
                "display_name": "Python (MLflow - Alura)",
                "language": "python",
                "name": "mlflow-rastreabilidade"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 5
    }
    path.write_text(
        json.dumps(notebook, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )
    print("NOTEBOOK CRIADO")
else:
    print("NOTEBOOK PRESERVADO")
