import json
from pathlib import Path

arquivo = Path(
    "notebooks/17_explorando_app_streamlit.ipynb"
)


def celula(tipo, fonte):
    resultado = {
        "cell_type": tipo,
        "metadata": {},
        "source": fonte.splitlines(keepends=True),
    }

    if tipo == "code":
        resultado["execution_count"] = None
        resultado["outputs"] = []

    return resultado


partes = [
    celula(
        "markdown",
        "# Aula 17 — Aplicação Streamlit\n"
        "Explorando app.py e os resultados finais."
    ),

    celula(
        "code",
        "from pathlib import Path\n"
        "import sys\n"
        "raiz = Path.cwd()\n"
        "if raiz.name == 'notebooks':\n"
        "    raiz = raiz.parent\n"
        "sys.path.insert(0, str(raiz))\n"
        "from src.aula17_app_utils import (\n"
        "    carregar_dados, grafico_historico,\n"
        "    grafico_metricas, grafico_previsoes,\n"
        "    diagnosticar_calendario,\n"
        ")\n"
        "historico, metricas, previsoes, resumo = carregar_dados()\n"
        "display(resumo)"
    ),

    celula(
        "markdown",
        "## Métricas dos quatro modelos"
    ),

    celula(
        "code",
        "display(metricas.sort_values('MAPE'))\n"
        "grafico_metricas(metricas).show()"
    ),

    celula(
        "markdown",
        "## Histórico de demanda"
    ),

    celula(
        "code",
        "grafico_historico(historico).show()\n"
        "print('Datas ausentes:', diagnosticar_calendario(historico))"
    ),

    celula(
        "markdown",
        "## Previsões"
    ),

    celula(
        "code",
        "grafico_previsoes(previsoes).show()"
    ),

    celula(
        "markdown",
        "## Executando o aplicativo\n"
        "No terminal PowerShell:\n\n"
        "```powershell\n"
        ".\\.venv\\Scripts\\python.exe -m streamlit run app.py\n"
        "```\n\n"
        "O aplicativo lê os CSVs já salvos."
    ),
]

notebook = {
    "cells": partes,
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

if arquivo.exists():
    print("NOTEBOOK PRESERVADO")
else:
    arquivo.write_text(
        json.dumps(
            notebook,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print("NOTEBOOK CRIADO")
