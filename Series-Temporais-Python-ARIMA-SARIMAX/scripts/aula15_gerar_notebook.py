import json
from pathlib import Path

arquivo = Path("notebooks/15_treinamento_sarimax.ipynb")


def celula(tipo, texto):
    c = {
        "cell_type": tipo,
        "metadata": {},
        "source": texto.splitlines(keepends=True),
    }
    if tipo == "code":
        c["execution_count"] = None
        c["outputs"] = []
    return c


notebook = {
    "cells": [
        celula(
            "markdown",
            "# Aula 15 - Treinamento SARIMAX\n"
            "SARIMAX com variaveis externas de clima e calendario."
        ),
        celula(
            "code",
            "from pathlib import Path\n"
            "import sys\n"
            "raiz = Path.cwd()\n"
            "if raiz.name == 'notebooks':\n"
            "    raiz = raiz.parent\n"
            "sys.path.insert(0, str(raiz))\n"
            "from src.aula15_treinamento_sarimax import (\n"
            "    carregar_dados, treinar_modelo, gerar_previsoes,\n"
            "    calcular_resultados, consolidar_previsoes,\n"
            ")\n"
            "X_treino, X_teste, y_treino, y_teste, teste = carregar_dados()\n"
            "print(X_treino.shape, X_teste.shape)\n"
            "display(X_treino.head())"
        ),
        celula(
            "markdown",
            "## Treinando SARIMAX"
        ),
        celula(
            "code",
            "resultado_sarimax, avisos = treinar_modelo(\n"
            "    y_treino, X_treino\n"
            ")\n"
            "print(resultado_sarimax.summary())\n"
            "print('Avisos:', avisos)"
        ),
        celula(
            "markdown",
            "## Previsoes com X_teste"
        ),
        celula(
            "code",
            "teste_resultado = gerar_previsoes(\n"
            "    resultado_sarimax, X_teste, teste\n"
            ")\n"
            "display(teste_resultado.head())"
        ),
        celula(
            "markdown",
            "## Comparacao dos quatro modelos"
        ),
        celula(
            "code",
            "df_metricas, comparacao, residuos = calcular_resultados(\n"
            "    teste_resultado\n"
            ")\n"
            "display(comparacao)\n"
            "display(consolidar_previsoes(teste_resultado).head())"
        ),
        celula(
            "markdown",
            "## Resultados ja salvos\n"
            "Use os graficos HTML e os CSVs na pasta do projeto.\n"
            "Atencao: X_teste contem clima historico observado."
        ),
    ],
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
        json.dumps(notebook, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print("NOTEBOOK CRIADO")
