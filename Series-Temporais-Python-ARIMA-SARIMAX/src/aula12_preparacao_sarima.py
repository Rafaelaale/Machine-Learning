"""Aula 12 - Sazonalidade e preparacao para SARIMA.

Reutiliza a divisao temporal da Aula 09.
Nao treina SARIMA e nao gera previsoes.
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from statsmodels.tsa.statespace.sarimax import SARIMAX

from src.aula09_separacao_temporal import (
    preparar_serie,
    separar_treino_teste,
)


RAIZ = Path(__file__).resolve().parent.parent

RESULTADOS = RAIZ / "resultados"
GRAFICOS = RAIZ / "graficos"

ARIMA_TREINO = RESULTADOS / "aula09_treino.csv"
ARIMA_TESTE = RESULTADOS / "aula09_teste.csv"

CSV_SERIE = RESULTADOS / "aula12_serie_diaria.csv"
CSV_TREINO = RESULTADOS / "aula12_treino_sarima.csv"
CSV_TESTE = RESULTADOS / "aula12_teste_sarima.csv"

CSV_CALENDARIO = (
    RESULTADOS / "aula12_dias_ausentes.csv"
)

JSON_RELATORIO = (
    RESULTADOS / "aula12_preparacao_sarima.json"
)

HTML_SERIE = (
    GRAFICOS / "aula12_serie_diaria.html"
)

HTML_DIVISAO = (
    GRAFICOS / "aula12_treino_teste_sarima.html"
)

TAMANHO_TESTE = 60
CICLO_SEMANAL_CANDIDATO = 7


def carregar_serie_diaria():
    """Recupera as colunas preparadas nas aulas anteriores."""

    serie_diaria = preparar_serie()

    if serie_diaria.columns.tolist() != [
        "data_hora", "demanda"
    ]:
        raise ValueError("Colunas inesperadas.")

    if not serie_diaria["data_hora"].is_monotonic_increasing:
        raise ValueError("Serie fora da ordem temporal.")

    if not serie_diaria["data_hora"].is_unique:
        raise ValueError("Datas duplicadas.")

    return serie_diaria


def preparar_treino_teste(serie_diaria):
    """Mantem a mesma divisao de treino/teste do ARIMA."""

    treino, teste = separar_treino_teste(
        serie_diaria,
        tamanho_teste=TAMANHO_TESTE,
    )

    return treino, teste


def verificar_divisao_anterior(treino, teste):
    """Confere datas e demandas frente aos CSVs da Aula 09."""

    if not ARIMA_TREINO.is_file():
        raise FileNotFoundError(
            "Arquivo de treino da Aula 09 ausente."
        )

    if not ARIMA_TESTE.is_file():
        raise FileNotFoundError(
            "Arquivo de teste da Aula 09 ausente."
        )

    treino_anterior = pd.read_csv(
        ARIMA_TREINO,
        parse_dates=["data_hora"],
    )

    teste_anterior = pd.read_csv(
        ARIMA_TESTE,
        parse_dates=["data_hora"],
    )

    colunas = ["data_hora", "demanda"]

    pd.testing.assert_frame_equal(
        treino[colunas].reset_index(drop=True),
        treino_anterior[colunas].reset_index(drop=True),
        check_dtype=False,
    )

    pd.testing.assert_frame_equal(
        teste[colunas].reset_index(drop=True),
        teste_anterior[colunas].reset_index(drop=True),
        check_dtype=False,
    )

    return True


def investigar_calendario(serie_diaria, treino, teste):
    """Investiga lacunas de datas sem preencher demanda."""

    datas = pd.DatetimeIndex(
        serie_diaria["data_hora"]
    )

    calendario_completo = pd.date_range(
        start=datas.min(),
        end=datas.max(),
        freq="D",
    )

    dias_ausentes = calendario_completo.difference(
        datas
    )

    tabela_ausentes = pd.DataFrame({
        "data_hora": dias_ausentes,
    })

    periodo_teste = (
        teste["data_hora"].max()
        - teste["data_hora"].min()
    ).days + 1

    periodo_treino = (
        treino["data_hora"].max()
        - treino["data_hora"].min()
    ).days + 1

    diagnostico = {
        "observacoes_total": int(len(serie_diaria)),
        "observacoes_treino": int(len(treino)),
        "observacoes_teste": int(len(teste)),
        "inicio_treino": str(
            treino["data_hora"].min().date()
        ),
        "fim_treino": str(
            treino["data_hora"].max().date()
        ),
        "inicio_teste": str(
            teste["data_hora"].min().date()
        ),
        "fim_teste": str(
            teste["data_hora"].max().date()
        ),
        "dias_calendario_treino": int(periodo_treino),
        "dias_calendario_teste": int(periodo_teste),
        "dias_ausentes_total": int(
            len(dias_ausentes)
        ),
        "serie_diaria_regular": bool(
            len(dias_ausentes) == 0
        ),
        "divisao_preserva_ordem": bool(
            treino["data_hora"].max()
            < teste["data_hora"].min()
        ),
        "ciclo_semanal_a_investigar": (
            CICLO_SEMANAL_CANDIDATO
        ),
        "nota_metodologica": (
            "Uma sazonalidade de sete observacoes "
            "nao equivale necessariamente a sete "
            "dias de calendario quando ha lacunas. "
            "A regularizacao requer decisao "
            "metodologica antes de ajustar SARIMA."
        ),
    }

    return diagnostico, tabela_ausentes


def grafico_demanda(serie_diaria):
    """Exibe demanda diaria observada."""

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=serie_diaria["data_hora"],
            y=serie_diaria["demanda"],
            mode="lines",
            name="Demanda diaria",
            line=dict(
                color="#2f4b7c",
                width=2,
            ),
        )
    )

    fig.update_layout(
        title="Demanda diaria - preparacao SARIMA",
        xaxis_title="Data",
        yaxis_title="Bicicletas",
        template="plotly_white",
        height=520,
    )

    return fig


def grafico_divisao(treino, teste):
    """Exibe a separacao temporal destinada ao SARIMA."""

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=treino["data_hora"],
            y=treino["demanda"],
            mode="lines",
            name="Treino",
            line=dict(
                color="#003f5c",
                width=2,
            ),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=teste["data_hora"],
            y=teste["demanda"],
            mode="lines",
            name="Teste",
            line=dict(
                color="#7a9ec2",
                width=2,
            ),
        )
    )

    fig.update_layout(
        title="Preparacao SARIMA - treino e teste",
        xaxis_title="Data",
        yaxis_title="Demanda diaria",
        template="plotly_white",
        height=520,
        hovermode="x unified",
    )

    return fig


def executar_aula():
    """Executa a preparacao e salva os resultados."""

    serie_diaria = carregar_serie_diaria()

    treino, teste = preparar_treino_teste(
        serie_diaria
    )

    verificar_divisao_anterior(
        treino,
        teste,
    )

    diagnostico, tabela_ausentes = (
        investigar_calendario(
            serie_diaria,
            treino,
            teste,
        )
    )

    RESULTADOS.mkdir(
        parents=True,
        exist_ok=True,
    )

    GRAFICOS.mkdir(
        parents=True,
        exist_ok=True,
    )

    for tabela, arquivo in [
        (serie_diaria, CSV_SERIE),
        (treino, CSV_TREINO),
        (teste, CSV_TESTE),
        (tabela_ausentes, CSV_CALENDARIO),
    ]:
        tabela.to_csv(
            arquivo,
            index=False,
            encoding="utf-8-sig",
        )

    grafico_demanda(
        serie_diaria
    ).write_html(
        str(HTML_SERIE),
        include_plotlyjs=True,
    )

    grafico_divisao(
        treino,
        teste,
    ).write_html(
        str(HTML_DIVISAO),
        include_plotlyjs=True,
    )

    relatorio = {
        "aula": 12,
        "titulo": (
            "Entendendo sazonalidade e preparando SARIMA"
        ),
        "modelo_anterior": "ARIMA(1,1,1)",
        "novo_modelo": "SARIMA",
        "biblioteca_disponivel": "statsmodels SARIMAX",
        "componente_sazonal": (
            "Ciclo recorrente que pode ser modelado "
            "com parametros sazonais."
        ),
        "ciclo_semanal_candidato": 7,
        "ciclo_semanal_validado": False,
        "comparacao_com_arima": (
            "Os conjuntos de treino e teste "
            "sao identicos aos da Aula 09."
        ),
        "diagnostico": diagnostico,
        "sarima_treinado": False,
        "previsoes_sarima_geradas": False,
        "dados_externos_utilizados": False,
        "proxima_aula": (
            "Definir parametros sazonais e treinar SARIMA"
        ),
    }

    JSON_RELATORIO.write_text(
        json.dumps(
            relatorio,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print("\n===== AULA 12 - PREPARACAO SARIMA =====")

    print("\nCOLUNAS:")
    print(serie_diaria.columns.tolist())

    print("\nFORMATO:")
    print(serie_diaria.shape)

    print("\nPRIMEIRAS OBSERVACOES:")
    print(
        serie_diaria.head().to_string(index=False)
    )

    print("\nTAMANHOS:")
    print("Treino:", len(treino))
    print("Teste:", len(teste))

    print("\nPERIODO DE TREINO:")
    print(
        treino["data_hora"].min(),
        "ate",
        treino["data_hora"].max(),
    )

    print("\nPERIODO DE TESTE:")
    print(
        teste["data_hora"].min(),
        "ate",
        teste["data_hora"].max(),
    )

    print("\nDIVISAO IGUAL A AULA 09: SIM")

    print("\nDIAGNOSTICO DO CALENDARIO:")
    print(
        json.dumps(
            diagnostico,
            indent=2,
            ensure_ascii=False,
        )
    )

    print("\nSAZONALIDADE CANDIDATA: 7 DIAS")
    print("SARIMA TREINADO: NAO")

    print("\nAULA 12 EXECUTADA COM SUCESSO")

    return relatorio


if __name__ == "__main__":
    executar_aula()
