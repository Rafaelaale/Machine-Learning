import json
from pathlib import Path

arquivo = Path(
    "notebooks/16_preparacao_aplicacao_streamlit.ipynb"
)


def celula(tipo, fonte):
    item = {
        "cell_type": tipo,
        "metadata": {},
        "source": fonte.splitlines(keepends=True),
    }

    if tipo == "code":
        item["execution_count"] = None
        item["outputs"] = []

    return item


partes = [
    celula(
        "markdown",
        "# Aula 16 — Preparando dados para Streamlit\n"
        "Organizando histórico, métricas, previsões e resumo."
    ),

    celula(
        "code",
        "from pathlib import Path\n"
        "import sys\n"
        "raiz = Path.cwd()\n"
        "if raiz.name == 'notebooks':\n"
        "    raiz = raiz.parent\n"
        "sys.path.insert(0, str(raiz))\n"
        "import pandas as pd\n"
        "import plotly.graph_objects as go\n"
        "from src.aula16_preparacao_streamlit import (\n"
        "    carregar_arquivos,\n"
        "    validar_dados,\n"
        "    selecionar_melhor_modelo,\n"
        "    criar_resumo,\n"
        "    grafico_historico,\n"
        "    grafico_previsoes,\n"
        "    executar_aula,\n"
        ")"
    ),

    celula(
        "markdown",
        "## Carregando arquivos finais da modelagem"
    ),

    celula(
        "code",
        "serie_historica, metricas, previsoes_teste, relatorio = (\n"
        "    carregar_arquivos()\n"
        ")\n"
        "print('Histórico:', serie_historica.shape)\n"
        "print('Métricas:', metricas.shape)\n"
        "print('Previsões:', previsoes_teste.shape)\n"
        "display(metricas)\n"
        "display(previsoes_teste.head())"
    ),

    celula(
        "markdown",
        "## Validando a integridade dos dados"
    ),

    celula(
        "code",
        "print(validar_dados(\n"
        "    serie_historica, metricas, previsoes_teste\n"
        "))"
    ),

    celula(
        "markdown",
        "## Identificando o melhor modelo"
    ),

    celula(
        "code",
        "melhor_modelo = selecionar_melhor_modelo(metricas)\n"
        "nome_melhor_modelo = melhor_modelo['modelo']\n"
        "print('Melhor modelo:', nome_melhor_modelo)\n"
        "display(melhor_modelo)"
    ),

    celula(
        "markdown",
        "## Resumo do projeto para o aplicativo"
    ),

    celula(
        "code",
        "resumo_projeto = criar_resumo(\n"
        "    serie_historica, metricas, previsoes_teste\n"
        ")\n"
        "display(resumo_projeto)"
    ),

    celula(
        "markdown",
        "## Gráfico da série histórica"
    ),

    celula(
        "code",
        "grafico_historico(serie_historica).show()"
    ),

    celula(
        "markdown",
        "## Gráfico de comparação das previsões"
    ),

    celula(
        "code",
        "grafico_previsoes(previsoes_teste).show()"
    ),

    celula(
        "markdown",
        "## Exportando quatro CSVs para o Streamlit"
    ),

    celula(
        "code",
        "relatorio_final = executar_aula()\n"
        "display(relatorio_final)"
    ),

    celula(
        "markdown",
        "## Próxima aula\n"
        "Construir app.py com Streamlit."
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
        "language_info": {
            "name": "python",
        },
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}

if arquivo.exists():
    print("NOTEBOOK PRESERVADO:", arquivo)
else:
    arquivo.write_text(
        json.dumps(
            notebook,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print("NOTEBOOK CRIADO:", arquivo)
