"""Aula 15: SARIMAX com clima e calendario."""

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

ORDEM = (1, 1, 1)
ORDEM_SAZONAL = (1, 0, 1, 7)
NOME = "SARIMAX(1,1,1)x(1,0,1,7)"

VARIAVEIS = [
    "temperatura_media",
    "sensacao_termica_media",
    "umidade_media",
    "velocidade_vento_media",
    "feriado",
    "dia_util",
] + [f"dia_semana_{i}" for i in range(1, 7)]


def carregar_dados():
    """Recupera as entradas preparadas na Aula 14."""

    X_treino = pd.read_csv(
        RESULTADOS / "aula14_X_treino.csv"
    ).astype(float)

    X_teste = pd.read_csv(
        RESULTADOS / "aula14_X_teste.csv"
    ).astype(float)

    y_treino = pd.read_csv(
        RESULTADOS / "aula14_y_treino.csv"
    )["demanda"].astype(float)

    y_teste = pd.read_csv(
        RESULTADOS / "aula14_y_teste.csv"
    )["demanda"].astype(float)

    teste = pd.read_csv(
        RESULTADOS / "aula14_teste_sarimax.csv",
        parse_dates=["data_hora"],
    )

    if X_treino.shape != (396, 12):
        raise ValueError("Formato incorreto de X_treino.")

    if X_teste.shape != (60, 12):
        raise ValueError("Formato incorreto de X_teste.")

    if len(y_treino) != 396 or len(y_teste) != 60:
        raise ValueError("Tamanho incorreto dos alvos.")

    if len(teste) != 60:
        raise ValueError("Conjunto de teste incorreto.")

    if X_treino.columns.tolist() != VARIAVEIS:
        raise ValueError("Variaveis X_treino incorretas.")

    if X_teste.columns.tolist() != VARIAVEIS:
        raise ValueError("Variaveis X_teste incorretas.")

    for valores in (X_treino, X_teste, y_treino, y_teste):
        if not np.isfinite(
            valores.to_numpy(dtype=float)
        ).all():
            raise ValueError("Dados nao finitos.")

    np.testing.assert_allclose(
        y_teste.to_numpy(),
        teste["demanda"].to_numpy(dtype=float),
    )

    np.testing.assert_allclose(
        X_teste.to_numpy(),
        teste[VARIAVEIS].to_numpy(dtype=float),
    )

    if not teste["data_hora"].is_monotonic_increasing:
        raise ValueError("Datas do teste fora de ordem.")

    return X_treino, X_teste, y_treino, y_teste, teste


def treinar_modelo(y_treino, X_treino):
    """Treina apenas com dados do periodo de treino."""

    modelo = SARIMAX(
        y_treino.reset_index(drop=True),
        exog=X_treino.reset_index(drop=True),
        order=ORDEM,
        seasonal_order=ORDEM_SAZONAL,
        enforce_stationarity=False,
        enforce_invertibility=False,
    )

    with warnings.catch_warnings(record=True) as avisos:
        warnings.simplefilter("always")
        resultado = modelo.fit(
            disp=False,
            maxiter=200,
        )

    mensagens = [str(a.message) for a in avisos]
    return resultado, mensagens


def gerar_previsoes(resultado, X_teste, teste):
    """Gera previsoes com exogenas historicas do teste."""

    valores = np.asarray(
        resultado.forecast(
            steps=len(teste),
            exog=X_teste,
        ),
        dtype=float,
    )

    if len(valores) != 60 or not np.isfinite(valores).all():
        raise ValueError("Previsoes invalidas.")

    saida = teste[["data_hora", "demanda"]].copy()
    saida["previsao_sarimax"] = valores

    return saida


def calcular_resultados(previsoes):
    """Avalia SARIMAX e compara os quatro modelos."""

    metricas = calcular_metrica(
        previsoes["demanda"],
        previsoes["previsao_sarimax"],
    )

    df_metricas = pd.DataFrame([
        {"modelo": NOME, **metricas}
    ])

    anteriores = pd.read_csv(
        RESULTADOS / "aula13_comparacao_modelos.csv"
    )[["modelo", "MAE", "RMSE", "MAPE"]]

    if len(anteriores) != 3:
        raise ValueError("Esperados tres modelos anteriores.")

    comparacao = pd.concat(
        [anteriores, df_metricas],
        ignore_index=True,
    ).sort_values("MAPE").reset_index(drop=True)

    if comparacao["modelo"].nunique() != 4:
        raise ValueError("Esperados quatro modelos diferentes.")

    residuos = previsoes.copy()
    residuos["residuo_sarimax"] = (
        residuos["demanda"] - residuos["previsao_sarimax"]
    )

    return df_metricas, comparacao, residuos


def consolidar_previsoes(previsoes):
    """Alinha as previsoes dos quatro modelos por data."""

    arima = pd.read_csv(
        RESULTADOS / "aula11_previsoes_arima.csv",
        parse_dates=["data_hora"],
    )

    sarima = pd.read_csv(
        RESULTADOS / "aula13_previsoes_sarima.csv",
        parse_dates=["data_hora"],
    )

    base = arima[
        [
            "data_hora",
            "demanda",
            "previsao_baseline",
            "previsao_arima",
        ]
    ].copy()

    for outra in (sarima, previsoes):
        pd.testing.assert_series_equal(
            base["data_hora"].reset_index(drop=True),
            outra["data_hora"].reset_index(drop=True),
            check_names=False,
        )
        np.testing.assert_allclose(
            base["demanda"],
            outra["demanda"],
        )

    base["previsao_sarima"] = (
        sarima["previsao_sarima"].to_numpy()
    )

    base["previsao_sarimax"] = (
        previsoes["previsao_sarimax"].to_numpy()
    )

    return base


def criar_graficos(previsoes, comparacao, residuos, consolidado):
    """Salva graficos interativos em HTML."""

    GRAFICOS.mkdir(parents=True, exist_ok=True)

    fig1 = go.Figure()

    for coluna, nome in (
        ("demanda", "Demanda real"),
        ("previsao_sarimax", "SARIMAX"),
    ):
        fig1.add_trace(go.Scatter(
            x=previsoes["data_hora"],
            y=previsoes[coluna],
            name=nome,
            mode="lines",
        ))

    fig1.update_layout(
        title="Real versus SARIMAX",
        xaxis_title="Data",
        yaxis_title="Demanda",
        template="plotly_white",
    )

    fig1.write_html(
        str(GRAFICOS / "aula15_real_vs_sarimax.html"),
        include_plotlyjs=True,
    )

    fig2 = go.Figure(go.Bar(
        x=comparacao["modelo"],
        y=comparacao["MAPE"],
        text=comparacao["MAPE"].round(2),
        textposition="auto",
    ))

    fig2.update_layout(
        title="MAPE: quatro modelos",
        yaxis_title="MAPE (%)",
        template="plotly_white",
    )

    fig2.write_html(
        str(GRAFICOS / "aula15_comparacao_mape.html"),
        include_plotlyjs=True,
    )

    fig3 = go.Figure(go.Scatter(
        x=residuos["data_hora"],
        y=residuos["residuo_sarimax"],
        mode="lines+markers",
        name="Residuo",
    ))

    fig3.add_hline(y=0, line_dash="dash")

    fig3.update_layout(
        title="Residuos SARIMAX",
        xaxis_title="Data",
        yaxis_title="Real - previsto",
        template="plotly_white",
    )

    fig3.write_html(
        str(GRAFICOS / "aula15_residuos_sarimax.html"),
        include_plotlyjs=True,
    )

    fig4 = go.Figure()

    for coluna in consolidado.columns[1:]:
        fig4.add_trace(go.Scatter(
            x=consolidado["data_hora"],
            y=consolidado[coluna],
            mode="lines",
            name=coluna,
        ))

    fig4.update_layout(
        title="Comparacao: real e quatro modelos",
        xaxis_title="Data",
        yaxis_title="Demanda",
        template="plotly_white",
    )

    fig4.write_html(
        str(GRAFICOS / "aula15_quatro_modelos.html"),
        include_plotlyjs=True,
    )


def executar_aula():
    """Executa e registra a modelagem completa."""

    (
        X_treino,
        X_teste,
        y_treino,
        y_teste,
        teste,
    ) = carregar_dados()

    print("\n===== TREINANDO SARIMAX =====")
    print("X_treino:", X_treino.shape)
    print("X_teste:", X_teste.shape)
    print("Ordem:", ORDEM)
    print("Ordem sazonal:", ORDEM_SAZONAL)

    resultado, avisos = treinar_modelo(
        y_treino,
        X_treino,
    )

    resumo = str(resultado.summary())
    print(resumo)

    previsoes = gerar_previsoes(
        resultado,
        X_teste,
        teste,
    )

    metricas, comparacao, residuos = (
        calcular_resultados(previsoes)
    )

    consolidado = consolidar_previsoes(
        previsoes
    )

    RESULTADOS.mkdir(parents=True, exist_ok=True)
    MODELOS.mkdir(parents=True, exist_ok=True)

    tabelas = {
        "aula15_previsoes_sarimax.csv": previsoes,
        "aula15_metricas_sarimax.csv": metricas,
        "aula15_comparacao_final_modelos.csv": comparacao,
        "aula15_residuos_sarimax.csv": residuos,
        "aula15_previsoes_consolidadas.csv": consolidado,
    }

    for nome, tabela in tabelas.items():
        tabela.to_csv(
            RESULTADOS / nome,
            index=False,
            encoding="utf-8-sig",
        )

    (RESULTADOS / "aula15_resumo_estatistico.txt").write_text(
        resumo,
        encoding="utf-8",
    )

    resultado.save(
        str(MODELOS / "aula15_sarimax_111_1017.pkl")
    )

    criar_graficos(
        previsoes,
        comparacao,
        residuos,
        consolidado,
    )

    convergiu = bool(
        resultado.mle_retvals.get("converged", False)
    )

    mape_sarimax = float(metricas.iloc[0]["MAPE"])

    mape_baseline = float(
        comparacao.loc[
            comparacao["modelo"] == "Baseline",
            "MAPE",
        ].iloc[0]
    )

    reducao = (
        (mape_baseline - mape_sarimax)
        / mape_baseline
        * 100
    )

    relatorio = {
        "aula": 15,
        "modelo": NOME,
        "ordem": list(ORDEM),
        "ordem_sazonal": list(ORDEM_SAZONAL),
        "variaveis_externas": VARIAVEIS,
        "treino": len(y_treino),
        "teste": len(y_teste),
        "convergiu": convergiu,
        "avisos": avisos,
        "mape_sarimax": mape_sarimax,
        "mape_baseline": mape_baseline,
        "reducao_relativa_mape_vs_baseline_pct": reducao,
        "melhor_modelo_por_mape": str(
            comparacao.iloc[0]["modelo"]
        ),
        "dias_ausentes": 263,
        "observacao_calendario": (
            "s=7 corresponde a sete observacoes, "
            "nao necessariamente sete dias."
        ),
        "limitacao": (
            "Clima do teste historico ja conhecido. "
            "Previsao operacional depende de dados "
            "climaticos futuros disponiveis."
        ),
    }

    (RESULTADOS / "aula15_relatorio_sarimax.json").write_text(
        json.dumps(
            relatorio,
            indent=2,
            ensure_ascii=False,
            allow_nan=False,
        ),
        encoding="utf-8",
    )

    print("\n===== COMPARACAO FINAL =====")
    print(
        comparacao.to_string(
            index=False,
            float_format=lambda n: f"{n:.4f}",
        )
    )

    print("\nMELHOR MODELO:", relatorio["melhor_modelo_por_mape"])
    print("SARIMAX CONVERGIU:", convergiu)
    print("REDUCAO RELATIVA DO MAPE:", round(reducao, 2), "%")

    if not convergiu:
        print(
            "ATENCAO: convergencia nao confirmada."
        )

    return relatorio


if __name__ == "__main__":
    executar_aula()
