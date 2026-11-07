"""Aula 16 - Preparando arquivos para aplicacao Streamlit.

Le os resultados anteriores, valida consistencia
e exporta quatro CSVs para o futuro app.py.

Nenhum modelo e treinado nesta aula.
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from src.aula11_metricas_arima import calcular_metrica


RAIZ = Path(__file__).resolve().parent.parent

RESULTADOS = RAIZ / "resultados"
GRAFICOS = RAIZ / "graficos"
SAIDA_APP = RAIZ / "outputs" / "tabelas"

ORIGEM_HISTORICO = (
    RESULTADOS / "aula12_serie_diaria.csv"
)

ORIGEM_METRICAS = (
    RESULTADOS / "aula15_comparacao_final_modelos.csv"
)

ORIGEM_PREVISOES = (
    RESULTADOS / "aula15_previsoes_consolidadas.csv"
)

ORIGEM_RELATORIO = (
    RESULTADOS / "aula15_relatorio_sarimax.json"
)

ARQUIVO_HISTORICO = (
    SAIDA_APP / "serie_historica.csv"
)

ARQUIVO_METRICAS = (
    SAIDA_APP / "metricas.csv"
)

ARQUIVO_PREVISOES = (
    SAIDA_APP / "previsoes.csv"
)

ARQUIVO_RESUMO = (
    SAIDA_APP / "resumo_projeto.csv"
)

ARQUIVO_RELATORIO = (
    RESULTADOS / "aula16_preparacao_streamlit.json"
)

GRAFICO_HISTORICO = (
    GRAFICOS / "aula16_serie_historica.html"
)

GRAFICO_MODELOS = (
    GRAFICOS / "aula16_previsoes_modelos.html"
)

COLUNAS_PREVISOES = [
    "data_hora",
    "demanda",
    "previsao_baseline",
    "previsao_arima",
    "previsao_sarima",
    "previsao_sarimax",
]


def carregar_arquivos():
    """Carrega historico, metricas e previsoes."""

    for arquivo in (
        ORIGEM_HISTORICO,
        ORIGEM_METRICAS,
        ORIGEM_PREVISOES,
        ORIGEM_RELATORIO,
    ):
        if not arquivo.is_file():
            raise FileNotFoundError(str(arquivo))

    serie_historica = pd.read_csv(
        ORIGEM_HISTORICO,
        parse_dates=["data_hora"],
    )

    metricas = pd.read_csv(
        ORIGEM_METRICAS
    )

    previsoes_teste = pd.read_csv(
        ORIGEM_PREVISOES,
        parse_dates=["data_hora"],
    )

    relatorio_anterior = json.loads(
        ORIGEM_RELATORIO.read_text(
            encoding="utf-8"
        )
    )

    return (
        serie_historica,
        metricas,
        previsoes_teste,
        relatorio_anterior,
    )


def validar_dados(
    serie_historica,
    metricas,
    previsoes_teste,
):
    """Valida os tres conjuntos antes da exportacao."""

    if serie_historica.columns.tolist() != [
        "data_hora", "demanda"
    ]:
        raise ValueError(
            "Colunas da serie historica incorretas."
        )

    if len(serie_historica) != 456:
        raise ValueError(
            "Historico deve conter 456 observacoes."
        )

    colunas_metricas = [
        "modelo", "MAE", "RMSE", "MAPE"
    ]

    if not set(colunas_metricas).issubset(
        metricas.columns
    ):
        raise ValueError(
            "Metricas devem possuir modelo, "
            "MAE, RMSE e MAPE."
        )

    if len(metricas) != 4:
        raise ValueError(
            "Esperados quatro modelos."
        )

    nomes = metricas["modelo"].astype(str).tolist()

    categorias = [
        "Baseline",
        "ARIMA",
        "SARIMA",
        "SARIMAX",
    ]

    for categoria in categorias:
        encontrados = [
            nome for nome in nomes
            if (
                nome == "Baseline"
                if categoria == "Baseline"
                else (
                    nome.startswith(categoria + "(")
                    or nome == categoria
                )
            )
        ]

        if len(encontrados) != 1:
            raise ValueError(
                f"Modelo ausente ou repetido: {categoria}"
            )

    if previsoes_teste.columns.tolist() != (
        COLUNAS_PREVISOES
    ):
        raise ValueError(
            "Colunas das previsoes incorretas."
        )

    if len(previsoes_teste) != 60:
        raise ValueError(
            "Esperadas 60 previsoes de teste."
        )

    for nome, tabela in (
        ("historico", serie_historica),
        ("teste", previsoes_teste),
    ):
        if not tabela["data_hora"].is_unique:
            raise ValueError(
                f"Datas duplicadas: {nome}"
            )

        if not tabela[
            "data_hora"
        ].is_monotonic_increasing:
            raise ValueError(
                f"Datas fora de ordem: {nome}"
            )

    for nome, tabela in (
        ("historico", serie_historica),
        ("metricas", metricas),
        ("previsoes", previsoes_teste),
    ):
        if tabela.isna().any().any():
            raise ValueError(
                f"Valores ausentes em {nome}."
            )

    for tabela, colunas in (
        (
            serie_historica,
            ["demanda"],
        ),
        (
            metricas,
            ["MAE", "RMSE", "MAPE"],
        ),
        (
            previsoes_teste,
            COLUNAS_PREVISOES[1:],
        ),
    ):
        valores = tabela[
            colunas
        ].to_numpy(dtype=float)

        if not np.isfinite(valores).all():
            raise ValueError(
                "Valores numericos nao finitos."
            )

    historico_teste = (
        serie_historica
        .tail(len(previsoes_teste))
        .reset_index(drop=True)
    )

    pd.testing.assert_series_equal(
        historico_teste["data_hora"],
        previsoes_teste["data_hora"].reset_index(
            drop=True
        ),
        check_names=False,
    )

    np.testing.assert_allclose(
        historico_teste["demanda"].to_numpy(dtype=float),
        previsoes_teste["demanda"].to_numpy(dtype=float),
    )

    # Confere que as metricas publicadas correspondem
    # as previsoes efetivamente salvas.
    correspondencias = {
        "Baseline": "previsao_baseline",
        "ARIMA": "previsao_arima",
        "SARIMA": "previsao_sarima",
        "SARIMAX": "previsao_sarimax",
    }

    for categoria, coluna in correspondencias.items():
        esperado = calcular_metrica(
            previsoes_teste["demanda"],
            previsoes_teste[coluna],
        )

        linha = metricas[
            metricas["modelo"].apply(
                lambda nome: (
                    nome == "Baseline"
                    if categoria == "Baseline"
                    else (
                        str(nome).startswith(
                            categoria + "("
                        )
                        or nome == categoria
                    )
                )
            )
        ].iloc[0]

        for metrica in ("MAE", "RMSE", "MAPE"):
            if not np.isclose(
                float(linha[metrica]),
                float(esperado[metrica]),
                rtol=1e-5,
                atol=1e-3,
            ):
                raise ValueError(
                    "Metrica incompativel com as "
                    f"previsoes: {categoria}/{metrica}"
                )

    return True


def selecionar_melhor_modelo(metricas):
    """Seleciona o modelo com menor MAPE real."""

    return (
        metricas.sort_values(
            "MAPE",
            ascending=True,
            kind="stable",
        )
        .iloc[0]
    )


def criar_resumo(
    serie_historica,
    metricas,
    previsoes_teste,
):
    """Gera o resumo de uma linha para o aplicativo."""

    melhor_modelo = selecionar_melhor_modelo(
        metricas
    )

    resumo_projeto = pd.DataFrame([
        {
            "modelo_final": str(
                melhor_modelo["modelo"]
            ),
            "MAE": float(
                melhor_modelo["MAE"]
            ),
            "RMSE": float(
                melhor_modelo["RMSE"]
            ),
            "MAPE": float(
                melhor_modelo["MAPE"]
            ),
            "inicio_historico": (
                serie_historica[
                    "data_hora"
                ].min().date().isoformat()
            ),
            "fim_historico": (
                serie_historica[
                    "data_hora"
                ].max().date().isoformat()
            ),
            "dias_historico": int(
                len(serie_historica)
            ),
            "dias_teste": int(
                len(previsoes_teste)
            ),
        }
    ])

    return resumo_projeto


def grafico_historico(serie_historica):
    """Grafico da demanda diaria observada."""

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=serie_historica["data_hora"],
            y=serie_historica["demanda"],
            name="Demanda diaria",
            mode="lines",
            line=dict(color="#17365d"),
        )
    )

    fig.update_layout(
        title="Historico de demanda de bicicletas",
        xaxis_title="Data",
        yaxis_title="Quantidade de bicicletas",
        template="plotly_white",
        height=530,
    )

    return fig


def grafico_previsoes(previsoes_teste):
    """Grafico comparativo dos quatro modelos."""

    configuracoes = [
        (
            "demanda",
            "Demanda real",
            "#142c4e",
            "solid",
        ),
        (
            "previsao_baseline",
            "Baseline",
            "#999999",
            "dash",
        ),
        (
            "previsao_arima",
            "ARIMA",
            "#377eb8",
            "solid",
        ),
        (
            "previsao_sarima",
            "SARIMA",
            "#ff7f00",
            "solid",
        ),
        (
            "previsao_sarimax",
            "SARIMAX",
            "#25966b",
            "solid",
        ),
    ]

    fig = go.Figure()

    for coluna, nome, cor, traco in configuracoes:
        fig.add_trace(
            go.Scatter(
                x=previsoes_teste["data_hora"],
                y=previsoes_teste[coluna],
                name=nome,
                mode="lines",
                line=dict(
                    color=cor,
                    dash=traco,
                    width=3 if nome == "Demanda real" else 2,
                ),
            )
        )

    fig.update_layout(
        title="Demanda real e previsoes dos modelos",
        xaxis_title="Data",
        yaxis_title="Quantidade de bicicletas",
        template="plotly_white",
        height=580,
        hovermode="x unified",
    )

    return fig


def executar_aula():
    """Prepara os quatro CSVs utilizados pelo app."""

    (
        serie_historica,
        metricas,
        previsoes_teste,
        relatorio_anterior,
    ) = carregar_arquivos()

    validar_dados(
        serie_historica,
        metricas,
        previsoes_teste,
    )

    # Mantem o nome do campo aceito pelo curso.
    metricas = (
        metricas[
            ["modelo", "MAE", "RMSE", "MAPE"]
        ]
        .copy()
        .sort_values("MAPE")
        .reset_index(drop=True)
    )

    resumo_projeto = criar_resumo(
        serie_historica,
        metricas,
        previsoes_teste,
    )

    SAIDA_APP.mkdir(
        parents=True,
        exist_ok=True,
    )

    RESULTADOS.mkdir(
        parents=True,
        exist_ok=True,
    )

    GRAFICOS.mkdir(
        parents=True,
        exist_ok=True,
    )

    tabelas = [
        (
            serie_historica,
            ARQUIVO_HISTORICO,
        ),
        (
            metricas,
            ARQUIVO_METRICAS,
        ),
        (
            previsoes_teste,
            ARQUIVO_PREVISOES,
        ),
        (
            resumo_projeto,
            ARQUIVO_RESUMO,
        ),
    ]

    for tabela, arquivo in tabelas:
        tabela.to_csv(
            arquivo,
            index=False,
            encoding="utf-8-sig",
        )

    grafico_historico(
        serie_historica
    ).write_html(
        str(GRAFICO_HISTORICO),
        include_plotlyjs=True,
    )

    grafico_previsoes(
        previsoes_teste
    ).write_html(
        str(GRAFICO_MODELOS),
        include_plotlyjs=True,
    )

    datas = pd.DatetimeIndex(
        serie_historica["data_hora"]
    )

    calendario = pd.date_range(
        datas.min(),
        datas.max(),
        freq="D",
    )

    dias_ausentes = int(
        len(calendario.difference(datas))
    )

    if dias_ausentes != 263:
        raise ValueError(
            "Quantidade de dias ausentes mudou: "
            f"{dias_ausentes}."
        )

    relatorio = {
        "aula": 16,
        "titulo": (
            "Preparando dados para aplicacao Streamlit"
        ),
        "arquivos_aplicacao": {
            "historico": str(ARQUIVO_HISTORICO),
            "metricas": str(ARQUIVO_METRICAS),
            "previsoes": str(ARQUIVO_PREVISOES),
            "resumo": str(ARQUIVO_RESUMO),
        },
        "melhor_modelo_por_mape": str(
            resumo_projeto.iloc[0]["modelo_final"]
        ),
        "mae_melhor_modelo": float(
            resumo_projeto.iloc[0]["MAE"]
        ),
        "rmse_melhor_modelo": float(
            resumo_projeto.iloc[0]["RMSE"]
        ),
        "mape_melhor_modelo": float(
            resumo_projeto.iloc[0]["MAPE"]
        ),
        "observacoes_historico": int(
            len(serie_historica)
        ),
        "observacoes_teste": int(
            len(previsoes_teste)
        ),
        "dias_calendario_ausentes": dias_ausentes,
        "sarimax_convergiu": (
            relatorio_anterior.get("convergiu")
        ),
        "modelos_treinados_novamente": False,
        "limitacao": (
            "A avaliacao SARIMAX utilizou clima "
            "historico observado durante o teste. "
            "Previsoes futuras exigem dados exogenos "
            "futuros disponiveis."
        ),
        "proxima_aula": (
            "Construir app.py com Streamlit"
        ),
    }

    ARQUIVO_RELATORIO.write_text(
        json.dumps(
            relatorio,
            ensure_ascii=False,
            indent=2,
            allow_nan=False,
        ),
        encoding="utf-8",
    )

    print("\n===== AULA 16 - DADOS PARA STREAMLIT =====")

    print("\nMETRICAS DOS QUATRO MODELOS:")
    print(
        metricas.to_string(
            index=False,
            float_format=lambda n: f"{n:.4f}",
        )
    )

    print("\nRESUMO DO PROJETO:")
    print(
        resumo_projeto.to_string(index=False)
    )

    print("\nPRIMEIRAS PREVISOES:")
    print(
        previsoes_teste.head().to_string(index=False)
    )

    print("\nARQUIVOS PARA O APP:")
    for arquivo in (
        ARQUIVO_HISTORICO,
        ARQUIVO_METRICAS,
        ARQUIVO_PREVISOES,
        ARQUIVO_RESUMO,
    ):
        print(
            arquivo,
            "| EXISTE:",
            arquivo.is_file(),
        )

    print("\nMODELO ESCOLHIDO:")
    print(
        resumo_projeto.iloc[0]["modelo_final"]
    )

    print("\nDIAS OBSERVADOS:", len(serie_historica))
    print("DIAS AUSENTES:", dias_ausentes)
    print("NOVO TREINAMENTO: NAO")

    print("\nAULA 16 EXECUTADA COM SUCESSO")

    return relatorio


if __name__ == "__main__":
    executar_aula()
