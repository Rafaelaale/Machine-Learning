"""Aula 11 - Avaliacao do ARIMA por MAE, RMSE e MAPE.

Utiliza previsoes da Aula 10.
Nao realiza novo treinamento.
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
)


RAIZ = Path(__file__).resolve().parent.parent

PREVISOES_ORIGINAIS = (
    RAIZ / "resultados"
    / "aula10_previsoes_baseline_arima.csv"
)

RELATORIO_AULA10 = (
    RAIZ / "resultados"
    / "aula10_baseline_arima.json"
)

CSV_PREVISOES = (
    RAIZ / "resultados"
    / "aula11_previsoes_arima.csv"
)

CSV_METRICAS = (
    RAIZ / "resultados"
    / "aula11_metricas_arima.csv"
)

CSV_RESIDUOS = (
    RAIZ / "resultados"
    / "aula11_residuos_arima.csv"
)

JSON_RELATORIO = (
    RAIZ / "resultados"
    / "aula11_avaliacao_arima.json"
)

HTML_METRICAS = (
    RAIZ / "graficos"
    / "aula11_comparacao_metricas.html"
)

HTML_RESIDUOS = (
    RAIZ / "graficos"
    / "aula11_residuos_arima.html"
)

COLUNAS = [
    "data_hora",
    "demanda",
    "previsao_baseline",
    "previsao_arima",
]


def carregar_previsoes():
    """Carrega as previsoes previamente geradas."""

    if not PREVISOES_ORIGINAIS.is_file():
        raise FileNotFoundError(
            "Execute primeiro a Aula 10."
        )

    teste = pd.read_csv(
        PREVISOES_ORIGINAIS,
        parse_dates=["data_hora"],
    )

    ausentes = [
        coluna
        for coluna in COLUNAS
        if coluna not in teste.columns
    ]

    if ausentes:
        raise ValueError(
            f"Colunas ausentes: {ausentes}"
        )

    teste = teste[COLUNAS].copy()

    for coluna in COLUNAS[1:]:
        teste[coluna] = pd.to_numeric(
            teste[coluna],
            errors="raise",
        )

    if teste.isna().any().any():
        raise ValueError(
            "Previsoes possuem valores ausentes."
        )

    if not np.isfinite(
        teste[COLUNAS[1:]].to_numpy(dtype=float)
    ).all():
        raise ValueError(
            "Previsoes possuem valores nao finitos."
        )

    if not teste["data_hora"].is_monotonic_increasing:
        raise ValueError(
            "Datas nao estao em ordem cronologica."
        )

    if not teste["data_hora"].is_unique:
        raise ValueError(
            "Datas duplicadas no teste."
        )

    if len(teste) != 60:
        raise ValueError(
            "Esperadas 60 observacoes da Aula 10."
        )

    return teste


def calcular_metrica(y_real, y_pred):
    """Calcula MAE, RMSE e MAPE.

    MAPE exclui pares cuja demanda real e zero.
    Se todos os valores reais forem zero, retorna
    ValueError em vez de um resultado enganoso.
    """

    y_real = np.asarray(
        y_real,
        dtype=float,
    ).reshape(-1)

    y_pred = np.asarray(
        y_pred,
        dtype=float,
    ).reshape(-1)

    if len(y_real) == 0:
        raise ValueError("Dados vazios.")

    if len(y_real) != len(y_pred):
        raise ValueError(
            "Valores reais e previstos "
            "precisam ter o mesmo tamanho."
        )

    if not np.isfinite(y_real).all():
        raise ValueError(
            "Valores reais invalidos."
        )

    if not np.isfinite(y_pred).all():
        raise ValueError(
            "Previsoes invalidas."
        )

    mae = mean_absolute_error(
        y_real,
        y_pred,
    )

    mse = mean_squared_error(
        y_real,
        y_pred,
    )

    rmse = np.sqrt(mse)

    mascara = y_real != 0

    if not mascara.any():
        raise ValueError(
            "MAPE indefinido: todos os valores reais sao zero."
        )

    mape = (
        np.mean(
            np.abs(
                (
                    y_real[mascara]
                    - y_pred[mascara]
                )
                / y_real[mascara]
            )
        )
        * 100
    )

    return {
        "MAE": float(mae),
        "RMSE": float(rmse),
        "MAPE": float(mape),
    }


def comparar_modelos(teste):
    """Compara baseline e ARIMA no mesmo horizonte."""

    metrica_baseline = calcular_metrica(
        teste["demanda"],
        teste["previsao_baseline"],
    )

    metrica_arima = calcular_metrica(
        teste["demanda"],
        teste["previsao_arima"],
    )

    df_metricas_arima = pd.DataFrame([
        {
            "modelo": "Baseline",
            **metrica_baseline,
        },
        {
            "modelo": "ARIMA(1,1,1)",
            **metrica_arima,
        },
    ])

    return df_metricas_arima


def calcular_residuos(teste):
    """Residuo positivo indica subestimativa do ARIMA."""

    resultado = teste[
        ["data_hora", "demanda", "previsao_arima"]
    ].copy()

    resultado["residuo_arima"] = (
        resultado["demanda"]
        - resultado["previsao_arima"]
    )

    resultado["erro_absoluto"] = (
        resultado["residuo_arima"].abs()
    )

    return resultado


def grafico_metricas(df_metricas):
    """Compara MAE, RMSE e MAPE em tres paineis."""

    from plotly.subplots import make_subplots

    fig = make_subplots(
        rows=1,
        cols=3,
        subplot_titles=("MAE", "RMSE", "MAPE (%)"),
    )

    for i, metrica in enumerate(
        ("MAE", "RMSE", "MAPE"),
        start=1,
    ):
        fig.add_trace(
            go.Bar(
                x=df_metricas["modelo"],
                y=df_metricas[metrica],
                name=metrica,
                text=df_metricas[metrica].round(2),
                textposition="auto",
                showlegend=False,
            ),
            row=1,
            col=i,
        )

        fig.update_yaxes(
            title_text=(
                "Percentual (%)"
                if metrica == "MAPE"
                else "Bicicletas"
            ),
            row=1,
            col=i,
        )

    fig.update_layout(
        title="Baseline versus ARIMA - metricas de erro",
        template="plotly_white",
        height=510,
    )

    return fig


def grafico_residuos(residuos):
    """Exibe residuos do ARIMA durante o teste."""

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=residuos["data_hora"],
            y=residuos["residuo_arima"],
            mode="lines+markers",
            name="Residuo ARIMA",
            line=dict(color="#2f4b7c"),
            marker=dict(size=5),
        )
    )

    fig.add_hline(
        y=0,
        line_dash="dash",
        line_color="#d45087",
    )

    fig.update_layout(
        title="Residuos do ARIMA no periodo de teste",
        xaxis_title="Data",
        yaxis_title="Demanda real - previsao",
        template="plotly_white",
        height=520,
    )

    return fig


def executar_aula():
    """Calcula, registra e audita resultados da avaliacao."""

    teste = carregar_previsoes()

    df_metricas_arima = comparar_modelos(teste)

    residuos = calcular_residuos(teste)

    CSV_METRICAS.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    HTML_METRICAS.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    teste.to_csv(
        CSV_PREVISOES,
        index=False,
        encoding="utf-8-sig",
    )

    df_metricas_arima.to_csv(
        CSV_METRICAS,
        index=False,
        encoding="utf-8-sig",
    )

    residuos.to_csv(
        CSV_RESIDUOS,
        index=False,
        encoding="utf-8-sig",
    )

    grafico_metricas(
        df_metricas_arima
    ).write_html(
        str(HTML_METRICAS),
        include_plotlyjs=True,
    )

    grafico_residuos(
        residuos
    ).write_html(
        str(HTML_RESIDUOS),
        include_plotlyjs=True,
    )

    menor_mape = df_metricas_arima.sort_values(
        "MAPE",
        ascending=True,
    ).iloc[0]["modelo"]

    linha_baseline = (
        df_metricas_arima
        .set_index("modelo")
        .loc["Baseline"]
    )

    linha_arima = (
        df_metricas_arima
        .set_index("modelo")
        .loc["ARIMA(1,1,1)"]
    )

    arima_superou_baseline = bool(
        linha_arima["MAPE"]
        < linha_baseline["MAPE"]
    )

    convergencia = None

    if RELATORIO_AULA10.is_file():
        relatorio_anterior = json.loads(
            RELATORIO_AULA10.read_text(
                encoding="utf-8"
            )
        )

        convergencia = relatorio_anterior.get(
            "arima_convergiu"
        )

    relatorio = {
        "aula": 11,
        "titulo": "Avaliando metricas do modelo ARIMA",
        "modelos": [
            "Baseline",
            "ARIMA(1,1,1)",
        ],
        "observacoes_teste": len(teste),
        "metricas": df_metricas_arima.to_dict(
            orient="records"
        ),
        "melhor_modelo_por_mape": menor_mape,
        "arima_superou_baseline_por_mape": (
            arima_superou_baseline
        ),
        "convergencia_reportada_aula10": (
            convergencia
        ),
        "mape_ignora_valores_reais_zero": True,
        "residuo_definicao": (
            "demanda real - previsao ARIMA"
        ),
        "observacao": (
            "Resultados especificos deste projeto; "
            "nao assumir numeros da transcricao. "
            "A serie original possui lacunas "
            "de calendario."
        ),
        "novo_treinamento_arima": False,
    }

    JSON_RELATORIO.write_text(
        json.dumps(
            relatorio,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print("\n===== AULA 11 - AVALIACAO ARIMA =====")

    print("\nMETRICAS CALCULADAS:")
    print(
        df_metricas_arima.to_string(
            index=False,
            float_format=lambda x: f"{x:.4f}",
        )
    )

    print("\nMELHOR MODELO POR MAPE:")
    print(menor_mape)

    print("\nARIMA SUPEROU BASELINE POR MAPE?")
    print(arima_superou_baseline)

    print("\nCONVERGENCIA REPORTADA PELA AULA 10:")
    print(convergencia)

    if convergencia is False:
        print(
            "ATENCAO: convergencia do ARIMA "
            "nao confirmada."
        )

    print("\nPRIMEIROS RESIDUOS:")
    print(residuos.head().to_string(index=False))

    print("\nARQUIVOS SALVOS:")
    for arquivo in (
        CSV_PREVISOES,
        CSV_METRICAS,
        CSV_RESIDUOS,
        JSON_RELATORIO,
        HTML_METRICAS,
        HTML_RESIDUOS,
    ):
        print(arquivo)

    print("\nAULA 11 EXECUTADA COM SUCESSO")

    return relatorio


if __name__ == "__main__":
    executar_aula()
