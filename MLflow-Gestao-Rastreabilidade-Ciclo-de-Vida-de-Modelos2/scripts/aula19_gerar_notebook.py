import json
from pathlib import Path


destino = Path("notebooks/19_servidor_remoto.ipynb")


def celula(tipo, conteudo):
    item = {
        "cell_type": tipo,
        "metadata": {},
        "source": conteudo.splitlines(keepends=True),
    }
    if tipo == "code":
        item["execution_count"] = None
        item["outputs"] = []
    return item


notebook = {
    "cells": [
        celula(
            "markdown",
            "# Aula 19 - Tracking Server remoto\n"
            "Laboratorio cliente-servidor via HTTP em localhost."
        ),
        celula(
            "code",
            "import json\n"
            "from pathlib import Path\n"
            "raiz = Path.cwd()\n"
            "if raiz.name == 'notebooks': raiz = raiz.parent\n"
            "arquivo = raiz / 'resultados/aula19_servidor_remoto.json'\n"
            "resultado = json.loads(arquivo.read_text(encoding='utf-8'))\n"
            "resultado\n"
        ),
        celula(
            "code",
            "print('TRACKING:', resultado['tracking_uri'])\n"
            "print('RUN:', resultado['run_id'])\n"
            "print('METRICAS:', resultado['metrics'])\n"
            "print('ARTEFATO:', resultado['artifact_downloaded'])\n"
        ),
        celula(
            "markdown",
            "## Arquitetura\n"
            "- Cliente: Python / MLflow API\n"
            "- Tracking Server: HTTP em 127.0.0.1:5050\n"
            "- Backend Store: SQLite isolado\n"
            "- Artifact Store: diretorio separado com proxy\n"
            "\n"
            "Para producao: HTTPS, autenticacao, permissoes, "
            "PostgreSQL gerenciado e S3 ou equivalente."
        ),
    ],
    "metadata": {
        "kernelspec": {
            "display_name": "Python (MLflow - Alura)",
            "language": "python",
            "name": "python3",
        }
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}

if destino.exists():
    print("NOTEBOOK PRESERVADO")
else:
    destino.write_text(
        json.dumps(notebook, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print("NOTEBOOK CRIADO:", destino)
