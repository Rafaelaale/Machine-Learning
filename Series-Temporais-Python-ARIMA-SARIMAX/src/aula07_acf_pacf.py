"""Aula 07 - ACF e PACF da demanda diferenciada."""

import json
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from statsmodels.tsa.stattools import acf, pacf

from src.aula04_decomposicao import carregar_serie_diaria
from src.aula06_diferenciacao import aplicar_diferenciacao


RAIZ = Path(__file__).resolve().parent.parent

CSV_ACF = RAIZ / "resultados" / "aula07_acf.csv"
CSV_PACF = RAIZ / "resultados" / "aula07_pacf.csv"
CSV_COMPARACAO = RAIZ / "resultados" / "aula07_comparacao_lags.csv"

JSON_RELATORIO = (
    RAIZ / "resultados" / "aula07_acf_pacf.json"
)

HTML_ACF = RAIZ / "graficos" / "aula07_acf.html"
HTML_PACF = RAIZ / "graficos" / "aula07_pacf.html"
HTML_COMPARACAO = RAIZ / "graficos" / "aula07_acf_pacf_comparacao.html"

NUMERO_LAGS = 30


def carregar_serie_diferenciada():
    """Recupera a serie da Aula 06."""

    original = carregar_serie_diaria()

    _, diferenciada = aplicar_diferenciacao(original)

    return diferenciada


def calcular_acf_pacf(serie, nlags=NUMERO_LAGS):
    """Calcula ACF e PACF por Yule-Walker modificado."""

    valores = pd.to_numeric(
        pd.Series(serie),
        errors="raise",
    ).dropna()

    if not np.isfinite(valores.to_numpy()).all():
        raise ValueError("A serie possui valores nao finitos.")

    if valores.nunique() < 2:
        raise ValueError("A serie e constante.")

    if nlags < 1:
        raise ValueError("Numero de lags invalido.")

    if nlags >= len(valores) // 2:
        raise ValueError(
            "PACF exige numero de lags menor "
            "que metade do tamanho da amostra."
        )

    valores_acf = acf(
        valores,
        nlags=nlags,
        fft=True,
    )

    valores_pacf = pacf(
        valores,
        nlags=nlags,
        method="ywm",
    )

    # Referencia aproximada para leitura exploratoria.
    # Nao substitui testes formais de significancia.
    limite = 1.96 / np.sqrt(len(valores))

    tabela = pd.DataFrame({
        "lag": np.arange(nlags + 1),
        "acf": valores_acf,
        "pacf": valores_pacf,
    })

    tabela["fora_faixa_acf"] = (
        tabela["acf"].abs() > limite
    )

    tabela["fora_faixa_pacf"] = (
        tabela["pacf"].abs() > limite
    )

    # Lag zero e igual a um por definicao.
    # Nao deve ser tratado como indicio de memoria.
    tabela.loc[
        tabela["lag"] == 0,
        ["fora_faixa_acf", "fora_faixa_pacf"],
    ] = False

    return tabela, float(limite)


def grafico_lags(tabela, coluna, titulo, limite):
    """Mostra coeficientes por lag e linhas de referencia."""

    if coluna not in ("acf", "pacf"):
        raise ValueError("Coluna deve ser acf ou pacf.")

    cor = "#2f4b7c" if coluna == "acf" else "#d45087"

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=tabela["lag"],
            y=tabela[coluna],
            name=coluna.upper(),
            marker_color=cor,
        )
    )

    for y in (limite, -limite):
        fig.add_hline(
            y=y,
            line_dash="dash",
            line_color="#f95d6a",
            annotation_text=(
                "Limite aproximado"
                if y > 0 else None
            ),
        )

    fig.add_hline(
        y=0,
        line_color="#555555",
        line_width=1,
    )

    fig.update_layout(
        title=titulo,
        xaxis_title="Lag (observações anteriores)",
        yaxis_title="Correlação",
        template="plotly_white",
        height=520,
        bargap=0.3,
        xaxis=dict(dtick=1),
    )

    return fig


def grafico_comparacao(tabela, limite):
    """Exibe ACF e PACF em uma mesma visualizacao."""

    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.12,
        subplot_titles=(
            "ACF - Autocorrelação",
            "PACF - Autocorrelação parcial",
        ),
    )

    for linha, coluna, cor in [
        (1, "acf", "#2f4b7c"),
        (2, "pacf", "#d45087"),
    ]:
        fig.add_trace(
            go.Bar(
                x=tabela["lag"],
                y=tabela[coluna],
                name=coluna.upper(),
                marker_color=cor,
            ),
            row=linha,
            col=1,
        )

        for y in (limite, -limite):
            fig.add_hline(
                y=y,
                line_dash="dash",
                line_color="#f95d6a",
                row=linha,
                col=1,
            )

    fig.update_layout(
        title="Comparação ACF e PACF - série diferenciada",
        template="plotly_white",
        height=850,
        bargap=0.3,
    )

    fig.update_xaxes(
        title_text="Lag (observações)",
        dtick=1,
        row=2,
        col=1,
    )

    return fig


def executar_aula():
    """Executa calculos, graficos e salva resultados."""

    serie_diferenciada = carregar_serie_diferenciada()

    tabela, limite = calcular_acf_pacf(
        serie_diferenciada["demanda_diff"],
        nlags=NUMERO_LAGS,
    )

    CSV_ACF.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    HTML_ACF.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    tabela[["lag", "acf", "fora_faixa_acf"]].to_csv(
        CSV_ACF,
        index=False,
        encoding="utf-8-sig",
    )

    tabela[["lag", "pacf", "fora_faixa_pacf"]].to_csv(
        CSV_PACF,
        index=False,
        encoding="utf-8-sig",
    )

    tabela.to_csv(
        CSV_COMPARACAO,
        index=False,
        encoding="utf-8-sig",
    )

    grafico_lags(
        tabela,
        "acf",
        "ACF da demanda diferenciada",
        limite,
    ).write_html(
        str(HTML_ACF),
        include_plotlyjs=True,
    )

    grafico_lags(
        tabela,
        "pacf",
        "PACF da demanda diferenciada",
        limite,
    ).write_html(
        str(HTML_PACF),
        include_plotlyjs=True,
    )

    grafico_comparacao(
        tabela,
        limite,
    ).write_html(
        str(HTML_COMPARACAO),
        include_plotlyjs=True,
    )

    lags_acf = tabela.loc[
        tabela["fora_faixa_acf"],
        "lag",
    ].astype(int).tolist()

    lags_pacf = tabela.loc[
        tabela["fora_faixa_pacf"],
        "lag",
    ].astype(int).tolist()

    intervalos_irregulares = int(
        (serie_diferenciada["intervalo_dias"] > 1).sum()
    )

    relatorio = {
        "aula": 7,
        "tema": "ACF e PACF",
        "serie": "demanda_diff",
        "observacoes": int(len(serie_diferenciada)),
        "numero_lags": NUMERO_LAGS,
        "metodo_pacf": "ywm",
        "limite_referencia_aproximado": limite,
        "lags_acf_fora_faixa": lags_acf,
        "lags_pacf_fora_faixa": lags_pacf,
        "intervalos_maiores_que_um_dia": (
            intervalos_irregulares
        ),
        "observacoes_metodologicas": [
            "Lag zero nao deve ser usado na selecao de parametros.",
            "A faixa de referencia 1.96/sqrt(n) e aproximada.",
            "Lags significam observacoes anteriores.",
            "Lacunas no calendario podem comprometer a leitura em dias.",
            "ACF e PACF geram hipoteses de p e q, nao escolhem o melhor modelo.",
        ],
        "modelo_arima_treinado": False,
    }

    JSON_RELATORIO.write_text(
        json.dumps(
            relatorio,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print("\n===== AULA 07 - ACF E PACF =====")
    print("Observacoes:", len(serie_diferenciada))
    print("Lags analisados:", NUMERO_LAGS)
    print("Metodo PACF: ywm")
    print("Limite aproximado: +/-", round(limite, 5))

    print("\nVALORES ACF E PACF:")
    print(
        tabela[["lag", "acf", "pacf"]]
        .to_string(index=False)
    )

    print("\nLAGS ACF FORA DA FAIXA:")
    print(lags_acf)

    print("\nLAGS PACF FORA DA FAIXA:")
    print(lags_pacf)

    print("\nINTERVALOS MAIORES QUE UM DIA:")
    print(intervalos_irregulares)

    if intervalos_irregulares:
        print(
            "ATENCAO: Lags representam observacoes, "
            "nao necessariamente dias consecutivos."
        )

    print("\nARQUIVOS GERADOS:")
    for caminho in [
        CSV_ACF,
        CSV_PACF,
        CSV_COMPARACAO,
        JSON_RELATORIO,
        HTML_ACF,
        HTML_PACF,
        HTML_COMPARACAO,
    ]:
        print(caminho)

    print("\nAULA 07 EXECUTADA COM SUCESSO")

    return relatorio


if __name__ == "__main__":
    executar_aula()
