"""Padronizacao de graficos Plotly - Alura."""

import plotly.express as px
import plotly.graph_objects as go

CORES = {
    "azul_escuro": "#003f5c",
    "azul_principal": "#2f4b7c",
    "azul_medio": "#665191",
    "azul_claro": "#a05195",
    "rosa": "#d45087",
    "laranja": "#f95d6a",
    "amarelo": "#ff7c43",
    "cinza_escuro": "#333333",
    "cinza_texto": "#555555",
    "cinza_claro": "#e0e0e0",
    "branco": "#ffffff",
    "fundo_claro": "#f7f7f7",
}

SEQUENCIA_CORES = [
    CORES["azul_principal"],
    CORES["azul_medio"],
    CORES["azul_claro"],
    CORES["rosa"],
    CORES["laranja"],
    CORES["amarelo"],
]

# Compatibilidade com os exemplos da transcricao.
cores = CORES


def aplicar_layout_padrao(
    fig,
    titulo=None,
    altura=500,
    mostrar_grade=True,
    legenda_horizontal=True,
):
    fig.update_layout(
        title=titulo,
        title_x=0.02,
        title_font=dict(
            size=18,
            color=CORES["azul_escuro"],
        ),
        height=altura,
        plot_bgcolor=CORES["fundo_claro"],
        paper_bgcolor=CORES["branco"],
        font=dict(color=CORES["cinza_texto"]),
        margin=dict(t=80, l=50, r=30, b=50),
    )

    eixo = dict(
        showgrid=mostrar_grade,
        gridcolor=CORES["cinza_claro"],
        linecolor=CORES["cinza_claro"],
        tickfont=dict(color=CORES["cinza_texto"]),
    )

    fig.update_xaxes(**eixo)
    fig.update_yaxes(**eixo)

    if legenda_horizontal:
        fig.update_layout(
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
            )
        )

    return fig


def grafico_linha_padrao(
    df,
    x,
    y,
    titulo=None,
    cor=None,
    label_x=None,
    label_y=None,
    altura=500,
    markers=False,
    xaxis=None,
    yaxis=None,
):
    fig = px.line(
        df,
        x=x,
        y=y,
        labels={
            x: xaxis or label_x or x,
            y: yaxis or label_y or y,
        },
        markers=markers,
    )

    fig.update_traces(
        line=dict(width=3),
        line_color=cor or CORES["azul_principal"],
    )

    return aplicar_layout_padrao(
        fig,
        titulo=titulo,
        altura=altura,
    )


def grafico_linha_multiplas_series_padrao(
    df,
    x,
    y,
    color_col,
    titulo=None,
    labels=None,
    altura=500,
):
    fig = px.line(
        df,
        x=x,
        y=y,
        color=color_col,
        labels=labels,
        color_discrete_sequence=SEQUENCIA_CORES,
    )

    fig.update_traces(line=dict(width=3))

    return aplicar_layout_padrao(
        fig,
        titulo=titulo,
        altura=altura,
    )


def grafico_barra_padrao(
    df,
    x,
    y,
    titulo,
    cor=None,
    label_x=None,
    label_y=None,
    altura=500,
    markers=False,
    labels=None,
):
    fig = px.bar(
        df,
        x=x,
        y=y,
        labels=labels or {
            x: label_x or x,
            y: label_y or y,
        },
    )

    fig.update_traces(
        marker_color=cor or CORES["azul_principal"]
    )

    return aplicar_layout_padrao(
        fig,
        titulo=titulo,
        altura=altura,
    )
