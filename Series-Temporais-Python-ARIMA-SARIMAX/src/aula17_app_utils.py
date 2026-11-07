"""Funcoes auxiliares da aplicacao Streamlit.

Mantem as validacoes e graficos separados
da interface visual do app.py.
"""

from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go


RAIZ_PROJETO = Path(__file__).resolve().parent.parent

CAMINHO_TABELAS = (
    RAIZ_PROJETO / "outputs" / "tabelas"
)

ARQUIVOS = {
    "historico": "serie_historica.csv",
    "metricas": "metricas.csv",
    "previsoes": "previsoes.csv",
    "resumo": "resumo_projeto.csv",
}

COLUNAS_PREVISOES = {
    "Demanda real": "demanda",
    "Baseline": "previsao_baseline",
    "ARIMA": "previsao_arima",
    "SARIMA": "previsao_sarima",
    "SARIMAX": "previsao_sarimax",
}

CORES = {
    "Demanda real": "#132A4A",
    "Baseline": "#9BA4B4",
    "ARIMA": "#377EB8",
    "SARIMA": "#F28E2B",
    "SARIMAX": "#159A77",
}


def validar_colunas(dataframe, colunas, nome):
    """Informa quais colunas obrigatorias estao ausentes."""

    ausentes = [
        coluna
        for coluna in colunas
        if coluna not in dataframe.columns
    ]

    if ausentes:
        raise ValueError(
            f"{nome}: colunas ausentes: "
            + ", ".join(ausentes)
        )


def carregar_dados():
    """Le os quatro arquivos gerados na Aula 16."""

    caminhos = {
        nome: CAMINHO_TABELAS / arquivo
        for nome, arquivo in ARQUIVOS.items()
    }

    ausentes = [
        str(caminho)
        for caminho in caminhos.values()
        if not caminho.is_file()
    ]

    if ausentes:
        raise FileNotFoundError(
            "Arquivos nao encontrados: "
            + ", ".join(ausentes)
        )

    historico = pd.read_csv(
        caminhos["historico"],
        parse_dates=["data_hora"],
    )

    metricas = pd.read_csv(
        caminhos["metricas"]
    )

    previsoes = pd.read_csv(
        caminhos["previsoes"],
        parse_dates=["data_hora"],
    )

    resumo = pd.read_csv(
        caminhos["resumo"]
    )

    validar_colunas(
        historico,
        ["data_hora", "demanda"],
        "serie_historica.csv",
    )

    validar_colunas(
        metricas,
        ["modelo", "MAE", "RMSE", "MAPE"],
        "metricas.csv",
    )

    validar_colunas(
        previsoes,
        ["data_hora"] + list(
            COLUNAS_PREVISOES.values()
        ),
        "previsoes.csv",
    )

    validar_colunas(
        resumo,
        [
            "modelo_final",
            "MAE",
            "RMSE",
            "MAPE",
            "inicio_historico",
            "fim_historico",
            "dias_historico",
            "dias_teste",
        ],
        "resumo_projeto.csv",
    )

    if resumo.empty:
        raise ValueError(
            "resumo_projeto.csv esta vazio."
        )

    if len(resumo) != 1:
        raise ValueError(
            "O resumo deve conter exatamente uma linha."
        )

    if len(historico) != 456:
        raise ValueError(
            "Esperadas 456 observacoes historicas."
        )

    if len(previsoes) != 60:
        raise ValueError(
            "Esperadas 60 observacoes de teste."
        )

    if len(metricas) != 4:
        raise ValueError(
            "Esperadas metricas de quatro modelos."
        )

    for nome, tabela in (
        ("historico", historico),
        ("metricas", metricas),
        ("previsoes", previsoes),
        ("resumo", resumo),
    ):
        if tabela.isna().any().any():
            raise ValueError(
                f"Valores ausentes em {nome}."
            )

    for nome, tabela in (
        ("historico", historico),
        ("previsoes", previsoes),
    ):
        if not tabela["data_hora"].is_unique:
            raise ValueError(
                f"Datas duplicadas: {nome}."
            )

        if not tabela["data_hora"].is_monotonic_increasing:
            raise ValueError(
                f"Datas fora de ordem: {nome}."
            )

    if not np.isfinite(
        metricas[["MAE", "RMSE", "MAPE"]]
        .to_numpy(dtype=float)
    ).all():
        raise ValueError(
            "Metricas numericas invalidas."
        )

    for nome, tabela, colunas in (
        ("historico", historico, ["demanda"]),
        (
            "previsoes",
            previsoes,
            list(COLUNAS_PREVISOES.values()),
        ),
    ):
        if not np.isfinite(
            tabela[colunas].to_numpy(dtype=float)
        ).all():
            raise ValueError(
                f"Valores numericos invalidos: {nome}"
            )

    historico_teste = (
        historico.tail(60)
        .reset_index(drop=True)
    )

    pd.testing.assert_series_equal(
        historico_teste["data_hora"],
        previsoes["data_hora"].reset_index(drop=True),
        check_names=False,
    )

    np.testing.assert_allclose(
        historico_teste["demanda"],
        previsoes["demanda"],
    )

    melhor = (
        metricas.sort_values("MAPE")
        .iloc[0]
    )

    registro = resumo.iloc[0]

    if registro["modelo_final"] != melhor["modelo"]:
        raise ValueError(
            "Modelo final diferente do menor MAPE."
        )

    for coluna in ("MAE", "RMSE", "MAPE"):
        if not np.isclose(
            float(registro[coluna]),
            float(melhor[coluna]),
        ):
            raise ValueError(
                f"Resumo inconsistente: {coluna}"
            )

    if int(registro["dias_historico"]) != len(historico):
        raise ValueError(
            "Quantidade historica inconsistente."
        )

    if int(registro["dias_teste"]) != len(previsoes):
        raise ValueError(
            "Quantidade de teste inconsistente."
        )

    return historico, metricas, previsoes, resumo


def formatar_data(valor):
    """Converte uma data para DD/MM/AAAA."""

    data = pd.to_datetime(valor, errors="raise")
    return data.strftime("%d/%m/%Y")


def diagnosticar_calendario(historico):
    """Conta datas sem registros dentro do periodo."""

    calendario = pd.date_range(
        historico["data_hora"].min(),
        historico["data_hora"].max(),
        freq="D",
    )

    observadas = pd.DatetimeIndex(
        historico["data_hora"]
    )

    return int(
        len(calendario.difference(observadas))
    )


def grafico_historico(historico):
    """Grafico interativo de demanda diaria."""

    figura = go.Figure()

    figura.add_trace(
        go.Scatter(
            x=historico["data_hora"],
            y=historico["demanda"],
            name="Demanda observada",
            mode="lines",
            line=dict(
                color=CORES["Demanda real"],
                width=2,
            ),
        )
    )

    figura.update_layout(
        title="Serie historica de demanda",
        xaxis_title="Data",
        yaxis_title="Bicicletas alugadas",
        template="plotly_white",
        height=490,
        hovermode="x unified",
    )

    return figura


def grafico_metricas(metricas):
    """Mostra o MAPE dos quatro modelos."""

    ordenadas = metricas.sort_values(
        "MAPE"
    )

    figura = go.Figure()

    figura.add_trace(
        go.Bar(
            x=ordenadas["modelo"],
            y=ordenadas["MAPE"],
            text=ordenadas["MAPE"].round(2),
            texttemplate="%{text:.2f}%",
            textposition="outside",
            marker_color=[
                "#159A77" if "SARIMAX" in nome
                else "#5A7DAB"
                for nome in ordenadas["modelo"]
            ],
        )
    )

    figura.update_layout(
        title="MAPE por modelo - menor e melhor",
        xaxis_title="Modelo",
        yaxis_title="MAPE (%)",
        template="plotly_white",
        height=470,
        showlegend=False,
        margin=dict(t=75),
    )

    return figura


def grafico_previsoes(previsoes, modelos=None):
    """Desenha a demanda real e os modelos selecionados."""

    if modelos is None:
        modelos = list(COLUNAS_PREVISOES)

    invalidos = [
        nome
        for nome in modelos
        if nome not in COLUNAS_PREVISOES
    ]

    if invalidos:
        raise ValueError(
            "Modelos desconhecidos: "
            + ", ".join(invalidos)
        )

    figura = go.Figure()

    for nome in modelos:
        coluna = COLUNAS_PREVISOES[nome]

        figura.add_trace(
            go.Scatter(
                x=previsoes["data_hora"],
                y=previsoes[coluna],
                name=nome,
                mode="lines",
                line=dict(
                    color=CORES[nome],
                    width=3 if nome == "Demanda real" else 2,
                    dash=(
                        "dash"
                        if nome == "Baseline"
                        else "solid"
                    ),
                ),
            )
        )

    figura.update_layout(
        title="Demanda real versus previsoes",
        xaxis_title="Data",
        yaxis_title="Bicicletas alugadas",
        template="plotly_white",
        height=540,
        hovermode="x unified",
        legend=dict(orientation="h", y=-0.25),
    )

    return figura
