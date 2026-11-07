"""Aula 13 - SARIMA sazonal, previsoes e comparacao.

Modelo: SARIMA(1,1,1)x(1,0,1,7).
A sazonalidade usa sete observacoes, e nao
necessariamente sete dias consecutivos.
"""

import json
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from statsmodels.tsa.statespace.sarimax import SARIMAX
from src.aula11_metricas_arima import calcular_metrica


RAIZ = Path(__file__).resolve().parent.parent

RESULTADOS = RAIZ / "resultados"
GRAFICOS = RAIZ / "graficos"
MODELOS = RAIZ / "modelos"

TREINO_ORIGEM = RESULTADOS / "aula12_treino_sarima.csv"
TESTE_ORIGEM = RESULTADOS / "aula12_teste_sarima.csv"
METRICAS_ANTERIORES = RESULTADOS / "aula11_metricas_arima.csv"
ARIMA_PREVISOES = RESULTADOS / "aula11_previsoes_arima.csv"

CSV_PREVISOES = RESULTADOS / "aula13_previsoes_sarima.csv"
CSV_METRICAS = RESULTADOS / "aula13_metricas_sarima.csv"
CSV_COMPARACAO = RESULTADOS / "aula13_comparacao_modelos.csv"
CSV_RESIDUOS = RESULTADOS / "aula13_residuos_sarima.csv"

JSON_RELATORIO = RESULTADOS / "aula13_relatorio_sarima.json"
TXT_RESUMO = RESULTADOS / "aula13_resumo_sarima.txt"
ARQUIVO_MODELO = MODELOS / "aula13_sarima_111_1017.pkl"

HTML_PREVISOES = GRAFICOS / "aula13_real_vs_sarima.html"
HTML_MAPE = GRAFICOS / "aula13_comparacao_mape.html"
HTML_RESIDUOS = GRAFICOS / "aula13_residuos_sarima.html"

ORDEM_SARIMA = (1, 1, 1)
ORDEM_SAZONAL = (1, 0, 1, 7)


def carregar_dados():
    """Carrega treino e teste salvos na Aula 12."""

    treino = pd.read_csv(
        TREINO_ORIGEM,
        parse_dates=["data_hora"],
    )

    teste = pd.read_csv(
        TESTE_ORIGEM,
        parse_dates=["data_hora"],
    )

    colunas = ["data_hora", "demanda"]

    for nome, tabela in [
        ("treino", treino),
        ("teste", teste),
    ]:
        if tabela.columns.tolist() != colunas:
            raise ValueError(
                f"Colunas inesperadas em {nome}."
            )

        if tabela.isna().any().any():
            raise ValueError(
                f"Dados ausentes em {nome}."
            )

        if not tabela["data_hora"].is_monotonic_increasing:
            raise ValueError(
                f"Datas fora de ordem em {nome}."
            )

        if not tabela["data_hora"].is_unique:
            raise ValueError(
                f"Datas duplicadas em {nome}."
            )

        if not np.isfinite(
            tabela["demanda"].to_numpy(dtype=float)
        ).all():
            raise ValueError(
                f"Demanda invalida em {nome}."
            )

    if len(treino) != 396 or len(teste) != 60:
        raise ValueError(
            "Divisao diferente das 396 observacoes "
            "de treino e 60 de teste."
        )

    if treino["data_hora"].max() >= teste["data_hora"].min():
        raise ValueError(
            "Treino e teste se sobrepoem."
        )

    return treino, teste


def verificar_calendario(treino, teste):
    """Registra lacunas sem preencher dias ausentes."""

    dados = pd.concat(
        [treino, teste],
        ignore_index=True,
    )

    datas = pd.DatetimeIndex(
        dados["data_hora"]
    )

    calendario = pd.date_range(
        datas.min(),
        datas.max(),
        freq="D",
    )

    faltantes = calendario.difference(datas)

    return {
        "datas_ausentes": int(len(faltantes)),
        "ciclo_sazonal": 7,
        "ciclo_corresponde_a_semana_regular": bool(
            len(faltantes) == 0
        ),
        "interpretacao": (
            "Com lacunas, s=7 representa sete "
            "observacoes anteriores, e nao "
            "necessariamente sete dias de calendario."
        ),
    }


def ajustar_sarima(
    treino,
    ordem=ORDEM_SARIMA,
    sazonal=ORDEM_SAZONAL,
):
    """Ajusta o SARIMA somente ao conjunto de treino."""

    valores = (
        treino["demanda"]
        .astype(float)
        .reset_index(drop=True)
    )

    modelo_sarima = SARIMAX(
        valores,
        order=ordem,
        seasonal_order=sazonal,
        enforce_stationarity=False,
        enforce_invertibility=False,
    )

    with warnings.catch_warnings(record=True) as avisos:
        warnings.simplefilter("always")
        resultado_sarima = modelo_sarima.fit(
            disp=False,
            maxiter=200,
        )

    mensagens = [
        str(aviso.message)
        for aviso in avisos
    ]

    return resultado_sarima, mensagens


def prever_sarima(resultado_sarima, teste):
    """Gera previsoes para as 60 observacoes futuras."""

    previsao_sarima = resultado_sarima.forecast(
        steps=len(teste)
    )

    valores = np.asarray(
        previsao_sarima,
        dtype=float,
    )

    if len(valores) != len(teste):
        raise ValueError(
            "Numero de previsoes incorreto."
        )

    if not np.isfinite(valores).all():
        raise ValueError(
            "Previsoes SARIMA nao finitas."
        )

    resultado = teste.copy()

    resultado["previsao_sarima"] = valores

    return resultado


def calcular_resultados(teste):
    """Calcula metricas, residuos e comparacao."""

    metricas_sarima = calcular_metrica(
        teste["demanda"],
        teste["previsao_sarima"],
    )

    df_metricas_sarima = pd.DataFrame([
        {
            "modelo": "SARIMA(1,1,1)x(1,0,1,7)",
            **metricas_sarima,
        }
    ])

    anteriores = pd.read_csv(
        METRICAS_ANTERIORES
    )

    colunas_metricas = [
        "modelo", "MAE", "RMSE", "MAPE"
    ]

    if not set(colunas_metricas).issubset(
        anteriores.columns
    ):
        raise ValueError(
            "Metricas anteriores incompletas."
        )

    nomes_anteriores = set(
        anteriores["modelo"]
    )

    if nomes_anteriores != {
        "Baseline", "ARIMA(1,1,1)"
    }:
        raise ValueError(
            "A comparacao anterior deve conter "
            "Baseline e ARIMA(1,1,1)."
        )

    # Confirma que o teste SARIMA corresponde
    # as mesmas observacoes usadas para ARIMA.
    previsoes_arima = pd.read_csv(
        ARIMA_PREVISOES,
        parse_dates=["data_hora"],
    )

    pd.testing.assert_series_equal(
        teste["data_hora"].reset_index(drop=True),
        previsoes_arima["data_hora"].reset_index(drop=True),
        check_names=False,
    )

    np.testing.assert_allclose(
        teste["demanda"].to_numpy(dtype=float),
        previsoes_arima["demanda"].to_numpy(dtype=float),
    )

    df_comparacao_modelos = pd.concat(
        [
            anteriores[colunas_metricas],
            df_metricas_sarima[colunas_metricas],
        ],
        ignore_index=True,
    ).sort_values(
        "MAPE",
        ascending=True,
        kind="stable",
    ).reset_index(drop=True)

    residuos = teste[
        ["data_hora", "demanda", "previsao_sarima"]
    ].copy()

    residuos["residuos_sarima"] = (
        residuos["demanda"]
        - residuos["previsao_sarima"]
    )

    return (
        df_metricas_sarima,
        df_comparacao_modelos,
        residuos,
    )


def grafico_previsoes(teste):
    """Visualiza demanda real versus SARIMA."""

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=teste["data_hora"],
            y=teste["demanda"],
            name="Demanda real",
            mode="lines",
            line=dict(
                color="#003f5c",
                width=3,
            ),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=teste["data_hora"],
            y=teste["previsao_sarima"],
            name="SARIMA",
            mode="lines",
            line=dict(
                color="#7a9ec2",
                width=3,
            ),
        )
    )

    fig.update_layout(
        title="Real versus previsto - SARIMA",
        xaxis_title="Data",
        yaxis_title="Demanda diaria",
        template="plotly_white",
        height=530,
        hovermode="x unified",
    )

    return fig


def grafico_mape(comparacao):
    """Exibe os tres modelos ordenados pelo MAPE."""

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=comparacao["modelo"],
            y=comparacao["MAPE"],
            text=comparacao["MAPE"].round(2),
            texttemplate="%{text:.2f}%",
            textposition="auto",
            name="MAPE",
        )
    )

    fig.update_layout(
        title="Comparacao entre Baseline, ARIMA e SARIMA",
        xaxis_title="Modelo",
        yaxis_title="MAPE (%) - menor e melhor",
        template="plotly_white",
        height=510,
    )

    return fig


def grafico_residuos(residuos):
    """Exibe erros da previsao SARIMA."""

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=residuos["data_hora"],
            y=residuos["residuos_sarima"],
            mode="lines+markers",
            name="Residuos SARIMA",
            line=dict(
                color="#2f4b7c",
                width=2,
            ),
            marker=dict(size=4),
        )
    )

    fig.add_hline(
        y=0,
        line_dash="dash",
        line_color="#d45087",
    )

    fig.update_layout(
        title="Residuos do SARIMA no periodo de teste",
        xaxis_title="Data",
        yaxis_title="Demanda real - previsao SARIMA",
        template="plotly_white",
        height=510,
    )

    return fig


def executar_aula():
    """Treina, preve, compara e salva os resultados."""

    treino, teste = carregar_dados()

    calendario = verificar_calendario(
        treino,
        teste,
    )

    print("\n===== AULA 13 - MODELO SARIMA =====")
    print("Parametros nao sazonais:", ORDEM_SARIMA)
    print("Parametros sazonais:", ORDEM_SAZONAL)
    print("Treino:", len(treino))
    print("Teste:", len(teste))

    print("\n===== TREINANDO SARIMA =====")

    resultado_sarima, avisos = ajustar_sarima(
        treino
    )

    resumo = str(
        resultado_sarima.summary()
    )

    print(resumo)

    teste_previsto = prever_sarima(
        resultado_sarima,
        teste,
    )

    print("\n===== PRIMEIRAS PREVISOES =====")

    print(
        teste_previsto[
            ["data_hora", "demanda", "previsao_sarima"]
        ].head().to_string(index=False)
    )

    (
        metricas_sarima,
        comparacao,
        residuos,
    ) = calcular_resultados(
        teste_previsto
    )

    print("\n===== METRICAS SARIMA =====")

    print(
        metricas_sarima.to_string(
            index=False,
            float_format=lambda x: f"{x:.4f}",
        )
    )

    print("\n===== COMPARACAO DOS TRES MODELOS =====")

    print(
        comparacao.to_string(
            index=False,
            float_format=lambda x: f"{x:.4f}",
        )
    )

    melhor_modelo = str(
        comparacao.iloc[0]["modelo"]
    )

    convergiu = bool(
        resultado_sarima.mle_retvals.get(
            "converged",
            False,
        )
    )

    print("\nMELHOR MODELO POR MAPE:", melhor_modelo)
    print("CONVERGENCIA DO SARIMA:", convergiu)
    print("DATAS AUSENTES:", calendario["datas_ausentes"])

    if not convergiu:
        print(
            "ATENCAO: O ajuste nao confirmou "
            "convergencia. Interpretar com cautela."
        )

    if calendario["datas_ausentes"]:
        print(
            "ATENCAO: s=7 e um ciclo de observacoes, "
            "nao uma semana calendario regular."
        )

    RESULTADOS.mkdir(
        parents=True,
        exist_ok=True,
    )

    GRAFICOS.mkdir(
        parents=True,
        exist_ok=True,
    )

    MODELOS.mkdir(
        parents=True,
        exist_ok=True,
    )

    teste_previsto[
        ["data_hora", "demanda", "previsao_sarima"]
    ].to_csv(
        CSV_PREVISOES,
        index=False,
        encoding="utf-8-sig",
    )

    metricas_sarima.to_csv(
        CSV_METRICAS,
        index=False,
        encoding="utf-8-sig",
    )

    comparacao.to_csv(
        CSV_COMPARACAO,
        index=False,
        encoding="utf-8-sig",
    )

    residuos.to_csv(
        CSV_RESIDUOS,
        index=False,
        encoding="utf-8-sig",
    )

    TXT_RESUMO.write_text(
        resumo + "\n",
        encoding="utf-8",
    )

    resultado_sarima.save(
        str(ARQUIVO_MODELO)
    )

    grafico_previsoes(
        teste_previsto
    ).write_html(
        str(HTML_PREVISOES),
        include_plotlyjs=True,
    )

    grafico_mape(
        comparacao
    ).write_html(
        str(HTML_MAPE),
        include_plotlyjs=True,
    )

    grafico_residuos(
        residuos
    ).write_html(
        str(HTML_RESIDUOS),
        include_plotlyjs=True,
    )

    relatorio = {
        "aula": 13,
        "modelo": "SARIMA",
        "ordem": list(ORDEM_SARIMA),
        "ordem_sazonal": list(ORDEM_SAZONAL),
        "observacoes_treino": len(treino),
        "observacoes_teste": len(teste),
        "convergiu": convergiu,
        "avisos_ajuste": avisos,
        "aic": float(resultado_sarima.aic),
        "bic": float(resultado_sarima.bic),
        "metricas_sarima": (
            metricas_sarima.iloc[0].to_dict()
        ),
        "melhor_modelo_por_mape": melhor_modelo,
        "ranking_modelos": comparacao.to_dict(
            orient="records"
        ),
        "calendario": calendario,
        "variaveis_exogenas_utilizadas": False,
        "modelo_salvo": str(ARQUIVO_MODELO),
        "proxima_aula": (
            "Introducao as variaveis exogenas "
            "para SARIMAX."
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

    print("\n===== ARQUIVOS GERADOS =====")

    for caminho in (
        CSV_PREVISOES,
        CSV_METRICAS,
        CSV_COMPARACAO,
        CSV_RESIDUOS,
        JSON_RELATORIO,
        TXT_RESUMO,
        ARQUIVO_MODELO,
        HTML_PREVISOES,
        HTML_MAPE,
        HTML_RESIDUOS,
    ):
        print(caminho)

    print("\nAULA 13 EXECUTADA COM SUCESSO")

    return relatorio


if __name__ == "__main__":
    executar_aula()
