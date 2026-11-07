"""Aula 09 - Preparacao e separacao temporal para ARIMA.

Nesta aula nao ha treinamento nem previsao de modelos.
"""

import json
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go

from src.aula04_decomposicao import carregar_serie_diaria
from src.visual_utils import (
    CORES,
    grafico_linha_padrao,
    aplicar_layout_padrao,
)


RAIZ = Path(__file__).resolve().parent.parent

PASTA_RESULTADOS = RAIZ / "resultados"
PASTA_GRAFICOS = RAIZ / "graficos"

CSV_MODELAGEM = (
    PASTA_RESULTADOS / "aula09_serie_modelagem.csv"
)
CSV_TREINO = (
    PASTA_RESULTADOS / "aula09_treino.csv"
)
CSV_TESTE = (
    PASTA_RESULTADOS / "aula09_teste.csv"
)
JSON_RELATORIO = (
    PASTA_RESULTADOS / "aula09_separacao_temporal.json"
)

HTML_SERIE = (
    PASTA_GRAFICOS / "aula09_serie_modelagem.html"
)
HTML_DIVISAO = (
    PASTA_GRAFICOS / "aula09_treino_teste.html"
)

TAMANHO_TESTE = 60


def preparar_serie():
    """Seleciona data e demanda, sem modificar a base original."""

    serie_diaria = carregar_serie_diaria()

    serie_modelagem = serie_diaria[
        ["data_hora", "demanda"]
    ].copy()

    serie_modelagem["data_hora"] = pd.to_datetime(
        serie_modelagem["data_hora"],
        errors="raise",
    )

    serie_modelagem["demanda"] = pd.to_numeric(
        serie_modelagem["demanda"],
        errors="raise",
    )

    serie_modelagem = (
        serie_modelagem
        .sort_values("data_hora")
        .reset_index(drop=True)
    )

    if serie_modelagem.empty:
        raise ValueError("A serie de modelagem esta vazia.")

    if serie_modelagem.isna().any().any():
        raise ValueError("Serie contem valores ausentes.")

    if serie_modelagem["data_hora"].duplicated().any():
        raise ValueError("Datas duplicadas.")

    return serie_modelagem


def separar_treino_teste(
    serie_modelagem,
    tamanho_teste=TAMANHO_TESTE,
):
    """Reserva as ultimas observacoes para o conjunto de teste."""

    if not isinstance(tamanho_teste, int):
        raise TypeError("tamanho_teste precisa ser inteiro.")

    if tamanho_teste <= 0:
        raise ValueError("tamanho_teste deve ser positivo.")

    if len(serie_modelagem) <= tamanho_teste:
        raise ValueError(
            "Sao necessarias observacoes suficientes "
            "para treino e teste."
        )

    if not serie_modelagem["data_hora"].is_monotonic_increasing:
        raise ValueError("A serie precisa estar ordenada.")

    if not serie_modelagem["data_hora"].is_unique:
        raise ValueError("Datas precisam ser unicas.")

    treino = (
        serie_modelagem
        .iloc[:-tamanho_teste]
        .copy()
    )

    teste = (
        serie_modelagem
        .iloc[-tamanho_teste:]
        .copy()
    )

    if treino["data_hora"].max() >= teste["data_hora"].min():
        raise ValueError("Treino e teste se sobrepoem no tempo.")

    if len(treino) + len(teste) != len(serie_modelagem):
        raise ValueError("A divisao perdeu observacoes.")

    return treino, teste


def diagnosticar_calendario(serie_modelagem, treino, teste):
    """Investiga lacunas entre datas e o horizonte efetivo."""

    dias = pd.DatetimeIndex(serie_modelagem["data_hora"])

    calendario = pd.date_range(
        start=dias.min(),
        end=dias.max(),
        freq="D",
    )

    ausentes = calendario.difference(dias)

    inicio_teste = teste["data_hora"].min()
    fim_teste = teste["data_hora"].max()

    dias_calendario_teste = int(
        (fim_teste - inicio_teste).days + 1
    )

    return {
        "observacoes_totais": int(len(serie_modelagem)),
        "observacoes_treino": int(len(treino)),
        "observacoes_teste": int(len(teste)),
        "data_inicial": str(dias.min().date()),
        "data_final": str(dias.max().date()),
        "inicio_treino": str(
            treino["data_hora"].min().date()
        ),
        "fim_treino": str(
            treino["data_hora"].max().date()
        ),
        "inicio_teste": str(inicio_teste.date()),
        "fim_teste": str(fim_teste.date()),
        "dias_calendario_no_intervalo_total": int(
            len(calendario)
        ),
        "dias_ausentes_no_intervalo_total": int(
            len(ausentes)
        ),
        "dias_calendario_cobertos_pelo_teste": (
            dias_calendario_teste
        ),
        "teste_pos_treino": bool(
            treino["data_hora"].max()
            < teste["data_hora"].min()
        ),
        "observacao": (
            "O teste tem 60 observacoes. "
            "Com lacunas na base, ele pode abranger "
            "mais de 60 dias de calendario."
        ),
    }


def grafico_serie_modelagem(serie_modelagem):
    """Visualizacao previa da demanda diaria."""

    return grafico_linha_padrao(
        df=serie_modelagem,
        x="data_hora",
        y="demanda",
        titulo="Série de demanda diária para modelagem",
        label_x="Data",
        label_y="Demanda diária",
        altura=500,
    )


def grafico_treino_teste(treino, teste):
    """Exibe dois conjuntos cronologicos sem embaralhamento."""

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=treino["data_hora"],
            y=treino["demanda"],
            mode="lines",
            name="Treino",
            line=dict(
                color=CORES["azul_principal"],
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
                color=CORES["rosa"],
                width=2,
            ),
        )
    )

    fig = aplicar_layout_padrao(
        fig,
        titulo="Separação temporal entre treino e teste",
        altura=500,
    )

    fig.update_xaxes(title_text="Data")
    fig.update_yaxes(title_text="Demanda diária")

    return fig


def executar_aula():
    """Executa a preparacao e salva os arquivos da Aula 09."""

    serie_modelagem = preparar_serie()

    treino, teste = separar_treino_teste(
        serie_modelagem,
        tamanho_teste=TAMANHO_TESTE,
    )

    diagnostico = diagnosticar_calendario(
        serie_modelagem,
        treino,
        teste,
    )

    PASTA_RESULTADOS.mkdir(
        parents=True,
        exist_ok=True,
    )

    PASTA_GRAFICOS.mkdir(
        parents=True,
        exist_ok=True,
    )

    for dataframe, caminho in (
        (serie_modelagem, CSV_MODELAGEM),
        (treino, CSV_TREINO),
        (teste, CSV_TESTE),
    ):
        dataframe.to_csv(
            caminho,
            index=False,
            encoding="utf-8-sig",
        )

    grafico_serie_modelagem(
        serie_modelagem
    ).write_html(
        str(HTML_SERIE),
        include_plotlyjs=True,
    )

    grafico_treino_teste(
        treino,
        teste,
    ).write_html(
        str(HTML_DIVISAO),
        include_plotlyjs=True,
    )

    relatorio = {
        "aula": 9,
        "titulo": "Separando treino e teste para ARIMA",
        "tamanho_teste": TAMANHO_TESTE,
        "diagnostico": diagnostico,
        "colunas_modelagem": [
            "data_hora",
            "demanda",
        ],
        "separacao_aleatoria": False,
        "modelo_treinado": False,
        "previsoes_geradas": False,
        "proxima_etapa": "Baseline de previsao",
    }

    JSON_RELATORIO.write_text(
        json.dumps(
            relatorio,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print("\n===== AULA 09 - TREINO E TESTE =====")

    print("\nSERIE DE MODELAGEM:")
    print(serie_modelagem.head().to_string(index=False))

    print("\nTamanho de treino:", len(treino))
    print("Tamanho de teste:", len(teste))

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

    print("\nQUALIDADE DO CALENDARIO:")
    print(json.dumps(
        diagnostico,
        indent=2,
        ensure_ascii=False,
    ))

    print("\nARQUIVOS GERADOS:")
    for caminho in (
        CSV_MODELAGEM,
        CSV_TREINO,
        CSV_TESTE,
        JSON_RELATORIO,
        HTML_SERIE,
        HTML_DIVISAO,
    ):
        print(caminho)

    print("\nAULA 09 EXECUTADA COM SUCESSO")

    return relatorio


if __name__ == "__main__":
    executar_aula()
