"""Aula 10 - Baseline e primeiro ARIMA(1,1,1).

O modelo usa somente o treino.
Nao calcula metricas comparativas nesta aula.
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from statsmodels.tsa.arima.model import ARIMA

from src.aula09_separacao_temporal import (
    preparar_serie,
    separar_treino_teste,
    diagnosticar_calendario,
)

RAIZ = Path(__file__).resolve().parent.parent

RESULTADOS = RAIZ / "resultados"
GRAFICOS = RAIZ / "graficos"

CSV_PREVISOES = (
    RESULTADOS / "aula10_previsoes_baseline_arima.csv"
)

JSON_RELATORIO = (
    RESULTADOS / "aula10_baseline_arima.json"
)

TXT_RESUMO = (
    RESULTADOS / "aula10_resumo_estatistico_arima.txt"
)

HTML_COMPARACAO = (
    GRAFICOS / "aula10_comparacao_previsoes.html"
)

HTML_HISTORICO = (
    GRAFICOS / "aula10_historico_e_previsoes.html"
)

ORDEM_ARIMA = (1, 1, 1)
TAMANHO_TESTE = 60


def carregar_divisao():
    """Reutiliza a separacao cronologica da Aula 09."""

    serie = preparar_serie()

    treino, teste = separar_treino_teste(
        serie,
        tamanho_teste=TAMANHO_TESTE,
    )

    return serie, treino, teste


def criar_baseline(treino, teste):
    """Repete o ultimo valor observado no treino."""

    if treino.empty or teste.empty:
        raise ValueError("Treino e teste precisam conter dados.")

    ultimo_valor_treino = float(
        treino["demanda"].iloc[-1]
    )

    resultado = teste.copy()

    resultado["previsao_baseline"] = (
        ultimo_valor_treino
    )

    return resultado, ultimo_valor_treino


def ajustar_arima(treino, ordem=ORDEM_ARIMA):
    """Treina ARIMA com observacoes exclusivamente do treino."""

    if len(treino) < 20:
        raise ValueError("Treino muito pequeno.")

    if len(ordem) != 3:
        raise ValueError("A ordem deve conter p, d e q.")

    valores_treino = (
        pd.to_numeric(
            treino["demanda"],
            errors="raise",
        )
        .astype(float)
        .reset_index(drop=True)
    )

    if not np.isfinite(valores_treino.to_numpy()).all():
        raise ValueError("Treino possui valores invalidos.")

    # RangeIndex explicito: as observacoes da base nao
    # possuem frequencia diaria regular garantida.
    modelo_arima = ARIMA(
        valores_treino,
        order=ordem,
    )

    resultado_arima = modelo_arima.fit()

    return resultado_arima


def gerar_previsoes(resultado_arima, teste):
    """Produz previsoes para o horizonte do conjunto de teste."""

    if teste.empty:
        raise ValueError("Conjunto de teste vazio.")

    previsao_arima = resultado_arima.forecast(
        steps=len(teste)
    )

    valores = np.asarray(
        previsao_arima,
        dtype=float,
    )

    if len(valores) != len(teste):
        raise ValueError(
            "Quantidade de previsoes diferente do teste."
        )

    if not np.isfinite(valores).all():
        raise ValueError(
            "Previsoes ARIMA possuem valores invalidos."
        )

    resultado = teste.copy()
    resultado["previsao_arima"] = valores

    return resultado


def grafico_comparacao(teste):
    """Compara demanda real, baseline e previsao ARIMA."""

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
            y=teste["previsao_baseline"],
            name="Baseline",
            mode="lines",
            line=dict(
                color="#ff7c43",
                width=2,
                dash="dash",
            ),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=teste["data_hora"],
            y=teste["previsao_arima"],
            name="ARIMA(1,1,1)",
            mode="lines",
            line=dict(
                color="#d45087",
                width=3,
            ),
        )
    )

    fig.update_layout(
        title="Demanda real x Baseline x ARIMA",
        xaxis_title="Data",
        yaxis_title="Demanda de bicicletas",
        template="plotly_white",
        height=550,
        hovermode="x unified",
        legend=dict(
            orientation="h",
            y=1.1,
        ),
    )

    return fig


def grafico_historico(treino, teste):
    """Exibe historico de treino e previsoes posteriores."""

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=treino["data_hora"],
            y=treino["demanda"],
            name="Treino",
            mode="lines",
            line=dict(
                color="#2f4b7c",
                width=2,
            ),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=teste["data_hora"],
            y=teste["demanda"],
            name="Teste real",
            mode="lines",
            line=dict(
                color="#003f5c",
                width=2,
            ),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=teste["data_hora"],
            y=teste["previsao_baseline"],
            name="Baseline",
            mode="lines",
            line=dict(
                color="#ff7c43",
                dash="dash",
                width=2,
            ),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=teste["data_hora"],
            y=teste["previsao_arima"],
            name="ARIMA(1,1,1)",
            mode="lines",
            line=dict(
                color="#d45087",
                width=2,
            ),
        )
    )

    fig.add_vline(
        x=teste["data_hora"].min(),
        line_dash="dot",
        line_color="#555555",
    )

    fig.update_layout(
        title="Histórico, treino, teste e previsões",
        xaxis_title="Data",
        yaxis_title="Demanda diária",
        template="plotly_white",
        height=600,
        hovermode="x unified",
    )

    return fig


def executar_aula():
    """Executa baseline, treinamento e previsao."""

    serie, treino, teste = carregar_divisao()

    teste_baseline, ultimo_valor = criar_baseline(
        treino,
        teste,
    )

    print("\n===== BASELINE =====")
    print("Ultimo valor do treino:", ultimo_valor)

    print(
        teste_baseline[
            ["data_hora", "demanda", "previsao_baseline"]
        ].head().to_string(index=False)
    )

    print("\n===== TREINANDO ARIMA(1,1,1) =====")

    resultado_arima = ajustar_arima(
        treino,
        ordem=ORDEM_ARIMA,
    )

    resumo_estatistico = str(
        resultado_arima.summary()
    )

    print("\n===== RESUMO ESTATISTICO =====")
    print(resumo_estatistico)

    teste_previsoes = gerar_previsoes(
        resultado_arima,
        teste_baseline,
    )

    print("\n===== PRIMEIRAS PREVISOES =====")

    print(
        teste_previsoes[
            [
                "data_hora",
                "demanda",
                "previsao_baseline",
                "previsao_arima",
            ]
        ].head().to_string(index=False)
    )

    RESULTADOS.mkdir(
        parents=True,
        exist_ok=True,
    )

    GRAFICOS.mkdir(
        parents=True,
        exist_ok=True,
    )

    teste_previsoes.to_csv(
        CSV_PREVISOES,
        index=False,
        encoding="utf-8-sig",
    )

    TXT_RESUMO.write_text(
        resumo_estatistico + "\n",
        encoding="utf-8",
    )

    grafico_comparacao(
        teste_previsoes
    ).write_html(
        str(HTML_COMPARACAO),
        include_plotlyjs=True,
    )

    grafico_historico(
        treino,
        teste_previsoes,
    ).write_html(
        str(HTML_HISTORICO),
        include_plotlyjs=True,
    )

    diagnostico = diagnosticar_calendario(
        serie,
        treino,
        teste,
    )

    convergiu = resultado_arima.mle_retvals.get(
        "converged"
    )

    relatorio = {
        "aula": 10,
        "titulo": "Criando baseline e treinando ARIMA",
        "modelo": "ARIMA",
        "ordem": list(ORDEM_ARIMA),
        "treinamento_realizado": True,
        "observacoes_treino": int(len(treino)),
        "observacoes_teste": int(len(teste)),
        "ultimo_valor_treino": ultimo_valor,
        "baseline": (
            "Repete o ultimo valor do treino em "
            "todo o periodo de teste."
        ),
        "previsoes_geradas": int(
            len(teste_previsoes)
        ),
        "arima_convergiu": (
            bool(convergiu)
            if convergiu is not None
            else None
        ),
        "aic": float(resultado_arima.aic),
        "bic": float(resultado_arima.bic),
        "diagnostico_calendario": diagnostico,
        "aviso": (
            "Como ha possiveis dias ausentes, "
            "o modelo usa a ordem das observacoes "
            "e nao uma frequencia diaria regular. "
            "As previsoes sao alinhadas as datas "
            "observadas no conjunto de teste."
        ),
        "metricas_de_erro_calculadas": False,
    }

    JSON_RELATORIO.write_text(
        json.dumps(
            relatorio,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print("\n===== RESULTADO DO TREINAMENTO =====")
    print("Treino:", len(treino))
    print("Teste:", len(teste))
    print("ARIMA:", ORDEM_ARIMA)
    print("Convergencia:", convergiu)
    print("Previsoes:", len(teste_previsoes))

    if convergiu is False:
        print(
            "AVISO: Otimizador nao confirmou convergencia. "
            "O resultado exige revisao na proxima etapa."
        )

    print("\n===== ARQUIVOS GERADOS =====")

    for caminho in [
        CSV_PREVISOES,
        JSON_RELATORIO,
        TXT_RESUMO,
        HTML_COMPARACAO,
        HTML_HISTORICO,
    ]:
        print(caminho)

    print("\nAULA 10 EXECUTADA COM SUCESSO")

    return relatorio


if __name__ == "__main__":
    executar_aula()
