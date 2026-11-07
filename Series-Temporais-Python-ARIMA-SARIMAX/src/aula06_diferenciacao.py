"""Aula 06 - Diferenciacao de primeira ordem e novo teste ADF."""

import json
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.aula04_decomposicao import carregar_serie_diaria
from src.aula05_adf import (
    teste_adf,
    extrair_metrica,
    interpretar_adf,
)

RAIZ = Path(__file__).resolve().parent.parent

CSV_DIFERENCIADA = (
    RAIZ / "resultados" / "aula06_serie_diferenciada.csv"
)
CSV_ADF_DIFERENCIADO = (
    RAIZ / "resultados" / "aula06_adf_diferenciado.csv"
)
CSV_COMPARACAO = (
    RAIZ / "resultados" / "aula06_comparacao_adf.csv"
)
JSON_RELATORIO = (
    RAIZ / "resultados" / "aula06_diferenciacao.json"
)
HTML_GRAFICO = (
    RAIZ / "graficos" / "aula06_original_vs_diferenciada.html"
)


def aplicar_diferenciacao(serie_diaria):
    """Calcula a variacao entre observacoes sucessivas."""

    df = serie_diaria[
        ["data_hora", "demanda"]
    ].copy()

    df["data_hora"] = pd.to_datetime(
        df["data_hora"],
        errors="raise",
    )

    df = df.sort_values(
        "data_hora"
    ).reset_index(drop=True)

    if df["data_hora"].duplicated().any():
        raise ValueError("Existem datas duplicadas.")

    if df["demanda"].isna().any():
        raise ValueError("Existem valores de demanda ausentes.")

    df["intervalo_dias"] = (
        df["data_hora"].diff().dt.days
    )

    df["demanda_diff"] = (
        df["demanda"].diff()
    )

    serie_diferenciada = (
        df.dropna(subset=["demanda_diff"])
        .copy()
    )

    return df, serie_diferenciada


def executar_comparacao_adf(original, diferenciada):
    """Reutiliza a funcao ADF da Aula 05."""

    adf_original = teste_adf(
        original["demanda"]
    )

    adf_diferenciado = teste_adf(
        diferenciada["demanda_diff"]
    )

    resultados = []

    for nome, tabela in [
        ("Original", adf_original),
        ("Diferenciada (d=1)", adf_diferenciado),
    ]:
        interpretacao = interpretar_adf(
            tabela,
            alfa=0.05,
        )

        resultados.append({
            "serie": nome,
            "estatistica_adf": extrair_metrica(
                tabela, "estatistica_adf"
            ),
            "p_valor": extrair_metrica(
                tabela, "p_valor"
            ),
            "lags_utilizados": int(
                extrair_metrica(
                    tabela, "lags_utilizados"
                )
            ),
            "observacoes_teste": int(
                extrair_metrica(
                    tabela, "observacoes"
                )
            ),
            "decisao": interpretacao["decisao"],
        })

    return (
        adf_original,
        adf_diferenciado,
        pd.DataFrame(resultados),
    )


def criar_grafico(original):
    """Mostra original e primeira diferenca."""

    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.12,
        subplot_titles=(
            "Demanda diária original",
            "Primeira diferença da demanda",
        ),
    )

    fig.add_trace(
        go.Scatter(
            x=original["data_hora"],
            y=original["demanda"],
            mode="lines",
            name="Demanda original",
            line=dict(color="#2f4b7c"),
        ),
        row=1,
        col=1,
    )

    fig.add_trace(
        go.Scatter(
            x=original["data_hora"],
            y=original["demanda_diff"],
            mode="lines",
            name="Demanda diferenciada",
            line=dict(color="#d45087"),
        ),
        row=2,
        col=1,
    )

    fig.add_hline(
        y=0,
        line_dash="dash",
        line_color="#555555",
        row=2,
        col=1,
    )

    fig.update_layout(
        title="Série original e diferenciada (d=1)",
        template="plotly_white",
        height=750,
        hovermode="x unified",
    )

    fig.update_yaxes(
        title_text="Bicicletas",
        row=1,
        col=1,
    )

    fig.update_yaxes(
        title_text="Variação",
        row=2,
        col=1,
    )

    fig.update_xaxes(
        title_text="Data",
        row=2,
        col=1,
    )

    return fig


def executar_aula():
    """Executa diferenciacao e compara dois testes ADF."""

    serie = carregar_serie_diaria()

    original, diferenciada = aplicar_diferenciacao(
        serie
    )

    adf_original, adf_diff, comparacao = (
        executar_comparacao_adf(
            original,
            diferenciada,
        )
    )

    CSV_DIFERENCIADA.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    HTML_GRAFICO.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    diferenciada.to_csv(
        CSV_DIFERENCIADA,
        index=False,
        encoding="utf-8-sig",
    )

    adf_diff.to_csv(
        CSV_ADF_DIFERENCIADO,
        index=False,
        encoding="utf-8-sig",
    )

    comparacao.to_csv(
        CSV_COMPARACAO,
        index=False,
        encoding="utf-8-sig",
    )

    criar_grafico(original).write_html(
        str(HTML_GRAFICO),
        include_plotlyjs=True,
    )

    intervalos_maiores = int(
        (diferenciada["intervalo_dias"] > 1).sum()
    )

    p_original = float(
        comparacao.iloc[0]["p_valor"]
    )

    p_diferenciado = float(
        comparacao.iloc[1]["p_valor"]
    )

    relatorio = {
        "aula": 6,
        "tema": "Diferenciacao e estacionariedade",
        "ordem_diferenciacao": 1,
        "linhas_originais": int(len(original)),
        "linhas_diferenciadas": int(len(diferenciada)),
        "intervalos_maiores_que_um_dia": intervalos_maiores,
        "p_valor_original": p_original,
        "p_valor_diferenciado": p_diferenciado,
        "nivel_significancia": 0.05,
        "rejeita_h0_original": bool(
            p_original <= 0.05
        ),
        "rejeita_h0_diferenciado": bool(
            p_diferenciado <= 0.05
        ),
        "alerta_calendario": (
            "diff() subtrai observacoes consecutivas "
            "na tabela. Se houver dias faltantes, "
            "algumas diferencas abrangem mais de um dia."
        ),
        "modelo_treinado": False,
    }

    JSON_RELATORIO.write_text(
        json.dumps(
            relatorio,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print("\n===== AULA 06 - DIFERENCIACAO =====")

    print("Linhas originais:", len(original))
    print("Linhas diferenciadas:", len(diferenciada))

    print("\nPRIMEIROS REGISTROS:")
    print(
        original[
            ["data_hora", "demanda", "demanda_diff"]
        ].head(10).to_string(index=False)
    )

    print("\nCOMPARACAO ADF:")
    print(comparacao.to_string(index=False))

    print("\nP-VALORES:")
    print(f"Original: {p_original:.6g}")
    print(f"Diferenciada: {p_diferenciado:.6g}")
    print(f"Diferenciada em notacao cientifica: {p_diferenciado:.4e}")

    if p_diferenciado <= 0.05:
        print(
            "RESULTADO: Ha evidencia contra a "
            "hipotese de raiz unitaria apos diferenciar."
        )
    else:
        print(
            "RESULTADO: Nao ha evidencia suficiente "
            "para rejeitar a hipotese de raiz unitaria."
        )

    print("\nINTERVALOS MAIORES QUE UM DIA:")
    print(intervalos_maiores)

    if intervalos_maiores:
        print(
            "ATENCAO: Algumas diferencas nao "
            "representam exatamente ontem versus hoje."
        )

    print("\nARQUIVOS:")
    for arquivo in [
        CSV_DIFERENCIADA,
        CSV_ADF_DIFERENCIADO,
        CSV_COMPARACAO,
        JSON_RELATORIO,
        HTML_GRAFICO,
    ]:
        print(arquivo)

    print("\nAULA 06 EXECUTADA COM SUCESSO")
    return relatorio


if __name__ == "__main__":
    executar_aula()
