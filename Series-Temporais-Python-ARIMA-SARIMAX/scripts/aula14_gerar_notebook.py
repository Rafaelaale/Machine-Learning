import json
from pathlib import Path

arquivo = Path(
    "notebooks/14_variaveis_exogenas_sarimax.ipynb"
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
        "# Aula 14 — Variáveis exógenas no SARIMAX\n"
        "Preparação da base diária e separação de X e y."
    ),

    celula(
        "code",
        "from pathlib import Path\n"
        "import sys\n"
        "raiz = Path.cwd()\n"
        "if raiz.name == 'notebooks':\n"
        "    raiz = raiz.parent\n"
        "sys.path.insert(0, str(raiz))\n"
        "print('Projeto:', raiz)"
    ),

    celula(
        "code",
        "import pandas as pd\n"
        "import numpy as np\n"
        "import plotly.graph_objects as go\n"
        "from statsmodels.tsa.statespace.sarimax import SARIMAX\n"
        "from src.aula14_preparacao_exogenas_sarimax import (\n"
        "    carregar_base_horaria,\n"
        "    validar_calendario,\n"
        "    agregar_base_diaria,\n"
        "    preparar_base_modelagem,\n"
        "    separar_dados,\n"
        "    verificar_compatibilidade,\n"
        "    diagnosticar_calendario,\n"
        "    grafico_clima,\n"
        "    grafico_divisao,\n"
        "    executar_aula,\n"
        ")\n"
        "print('Importações concluídas')"
    ),

    celula(
        "markdown",
        "## Carregando a base horária"
    ),

    celula(
        "code",
        "df = carregar_base_horaria()\n"
        "print('Linhas:', df.shape[0])\n"
        "print('Colunas:', df.shape[1])\n"
        "display(df.head(10))"
    ),

    celula(
        "markdown",
        "## Validando o calendário"
    ),

    celula(
        "code",
        "validacao_calendario = validar_calendario(df)\n"
        "display(validacao_calendario.head())\n"
        "display((validacao_calendario == 1).all())"
    ),

    celula(
        "markdown",
        "## Agregando dados horários por dia"
    ),

    celula(
        "code",
        "base_diaria = agregar_base_diaria(df)\n"
        "print('Dias observados:', len(base_diaria))\n"
        "display(base_diaria.head())"
    ),

    celula(
        "code",
        "fig = grafico_clima(base_diaria)\n"
        "fig.show()"
    ),

    celula(
        "markdown",
        "## Codificando o dia da semana"
    ),

    celula(
        "code",
        "base_modelagem, dummies_dia_da_semana, variaveis_externas = (\n"
        "    preparar_base_modelagem(base_diaria)\n"
        ")\n"
        "display(dummies_dia_da_semana.head())\n"
        "display(base_modelagem.head())\n"
        "print('Variáveis externas:')\n"
        "for variavel in variaveis_externas:\n"
        "    print(' -', variavel)"
    ),

    celula(
        "markdown",
        "## Separando treino e teste"
    ),

    celula(
        "code",
        "treino, teste, y_treino, y_teste, X_treino, X_teste = (\n"
        "    separar_dados(base_modelagem, variaveis_externas)\n"
        ")\n"
        "print('Treino:', treino.shape)\n"
        "print('Teste:', teste.shape)\n"
        "print('X_treino:', X_treino.shape)\n"
        "print('X_teste:', X_teste.shape)\n"
        "print('y_treino:', y_treino.shape)\n"
        "print('y_teste:', y_teste.shape)"
    ),

    celula(
        "markdown",
        "## Verificando compatibilidade com ARIMA e SARIMA"
    ),

    celula(
        "code",
        "print('Divisão preservada:', verificar_compatibilidade(treino, teste))\n"
        "display(diagnosticar_calendario(base_diaria))\n"
        "fig = grafico_divisao(treino, teste)\n"
        "fig.show()"
    ),

    celula(
        "markdown",
        "## Salvando os resultados"
    ),

    celula(
        "code",
        "relatorio = executar_aula()\n"
        "display(relatorio)"
    ),

    celula(
        "markdown",
        "## Próxima aula\n"
        "Treinamento do SARIMAX com as variáveis exógenas."
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
    print("NOTEBOOK SALVO:", arquivo)
