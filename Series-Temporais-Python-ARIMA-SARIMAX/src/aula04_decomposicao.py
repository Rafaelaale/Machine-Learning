"""Aula 04 - Tendencia, sazonalidade, residuo e media movel."""

import json
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from statsmodels.tsa.seasonal import seasonal_decompose


RAIZ = Path(__file__).resolve().parent.parent

CSV_ORIGINAL = RAIZ / "dados" / "bike.csv"
CSV_DIARIO = RAIZ / "resultados" / "serie_diaria_bike.csv"

CSV_COMPONENTES = (
    RAIZ / "resultados" / "aula04_componentes.csv"
)

CSV_MEDIA_MOVEL = (
    RAIZ / "resultados" / "aula04_media_movel.csv"
)

RELATORIO = (
    RAIZ / "resultados" / "aula04_decomposicao.json"
)

GRAFICO_MEDIA = (
    RAIZ / "graficos" / "aula04_media_movel.html"
)

GRAFICO_DECOMPOSICAO = (
    RAIZ / "graficos" / "aula04_decomposicao.html"
)


def carregar_serie_diaria():
    """Le a serie anterior ou agrega diretamente o CSV original."""

    if CSV_DIARIO.is_file():
        df = pd.read_csv(CSV_DIARIO)

        if "demanda_diaria" in df.columns:
            df = df.rename(
                columns={"demanda_diaria": "demanda"}
            )

        if "data_hora" not in df.columns:
            if "data" in df.columns:
                df = df.rename(
                    columns={"data": "data_hora"}
                )
            else:
                raise ValueError("Coluna de data ausente.")

        if "demanda" not in df.columns:
            raise ValueError("Coluna demanda ausente.")

        df = df[["data_hora", "demanda"]].copy()

    else:
        df = pd.read_csv(CSV_ORIGINAL)

        if not {"datetime", "count"}.issubset(df.columns):
            raise ValueError(
                "CSV original precisa de datetime e count."
            )

        df["datetime"] = pd.to_datetime(
            df["datetime"],
            errors="raise",
        )

        df = (
            df.assign(
                data_hora=df["datetime"].dt.floor("D")
            )
            .groupby("data_hora", as_index=False)
            .agg(demanda=("count", "sum"))
        )

        CSV_DIARIO.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        df.rename(
            columns={"demanda": "demanda_diaria"}
        ).to_csv(
            CSV_DIARIO,
            index=False,
            encoding="utf-8-sig",
        )

    df["data_hora"] = pd.to_datetime(
        df["data_hora"],
        errors="raise",
    )

    df["demanda"] = pd.to_numeric(
        df["demanda"],
        errors="raise",
    )

    df = df.sort_values(
        "data_hora"
    ).reset_index(drop=True)

    if df.empty:
        raise ValueError("Serie diaria vazia.")

    if df[["data_hora", "demanda"]].isna().any().any():
        raise ValueError("Datas ou demandas ausentes.")

    if df["data_hora"].duplicated().any():
        raise ValueError("Datas diarias duplicadas.")

    if (df["demanda"] < 0).any():
        raise ValueError("Demanda negativa.")

    return df


def calcular_media_movel(df, janela=7):
    """Media das ultimas 7 observacoes, incluindo a atual."""

    if janela < 1:
        raise ValueError("Janela invalida.")

    resultado = df.copy()

    resultado["media_movel_7"] = (
        resultado["demanda"]
        .rolling(
            window=janela,
            min_periods=janela,
        )
        .mean()
    )

    return resultado


def verificar_calendario(df):
    """Contabiliza dias ausentes no intervalo observado."""

    datas = pd.DatetimeIndex(df["data_hora"])

    calendario = pd.date_range(
        datas.min(),
        datas.max(),
        freq="D",
    )

    ausentes = calendario.difference(datas)

    return {
        "dias_observados": int(len(datas)),
        "dias_no_calendario": int(len(calendario)),
        "dias_sem_observacao": int(len(ausentes)),
        "primeiro_dia": str(datas.min().date()),
        "ultimo_dia": str(datas.max().date()),
        "calendario_diario_completo": len(ausentes) == 0,
    }


def decompor_serie(df, periodo=7):
    """Decomposicao aditiva de 7 observacoes.

    Se houver dias ausentes, o periodo representa
    7 observacoes consecutivas na tabela, nao
    necessariamente 7 dias consecutivos no calendario.
    """

    if len(df) < 2 * periodo:
        raise ValueError(
            "Pelo menos dois ciclos sao necessarios."
        )

    serie = pd.Series(
        df["demanda"].to_numpy(dtype=float),
        index=pd.DatetimeIndex(df["data_hora"]),
        name="demanda",
    )

    resultado = seasonal_decompose(
        serie,
        model="additive",
        period=periodo,
    )

    componentes = pd.DataFrame({
        "data": serie.index,
        "observado": np.asarray(resultado.observed),
        "tendencia": np.asarray(resultado.trend),
        "sazonalidade": np.asarray(resultado.seasonal),
        "residuo": np.asarray(resultado.resid),
    }).reset_index(drop=True)

    return componentes


def grafico_media_movel(df):
    """Compara demanda original e media suavizada."""

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df["data_hora"],
            y=df["demanda"],
            mode="lines",
            name="Demanda observada",
            line=dict(color="#2f4b7c", width=1),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df["data_hora"],
            y=df["media_movel_7"],
            mode="lines",
            name="Média móvel (7 observações)",
            line=dict(color="#d45087", width=3),
        )
    )

    fig.update_layout(
        title="Demanda diária e média móvel",
        xaxis_title="Data",
        yaxis_title="Demanda",
        template="plotly_white",
        height=500,
        hovermode="x unified",
    )

    return fig


def grafico_componentes(componentes):
    """Exibe os quatro componentes da decomposicao."""

    fig = make_subplots(
        rows=4,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.07,
        subplot_titles=(
            "Demanda observada",
            "Tendência",
            "Sazonalidade",
            "Resíduo",
        ),
    )

    colunas = [
        ("observado", "#2f4b7c"),
        ("tendencia", "#d45087"),
        ("sazonalidade", "#ff7c43"),
        ("residuo", "#665191"),
    ]

    for i, (coluna, cor) in enumerate(
        colunas,
        start=1,
    ):
        fig.add_trace(
            go.Scatter(
                x=componentes["data"],
                y=componentes[coluna],
                mode="lines",
                name=coluna,
                line=dict(color=cor, width=2),
            ),
            row=i,
            col=1,
        )

    fig.update_layout(
        title="Decomposição aditiva — período 7",
        template="plotly_white",
        height=1000,
        showlegend=False,
    )

    fig.update_xaxes(
        title_text="Data",
        row=4,
        col=1,
    )

    return fig


def executar_aula():
    """Produz tabelas, graficos e relatorio da Aula 04."""

    df = carregar_serie_diaria()

    calendario = verificar_calendario(df)

    suavizada = calcular_media_movel(df)

    componentes = decompor_serie(df, periodo=7)

    CSV_COMPONENTES.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    GRAFICO_MEDIA.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    suavizada.to_csv(
        CSV_MEDIA_MOVEL,
        index=False,
        encoding="utf-8-sig",
    )

    componentes.to_csv(
        CSV_COMPONENTES,
        index=False,
        encoding="utf-8-sig",
    )

    grafico_media_movel(suavizada).write_html(
        GRAFICO_MEDIA,
        include_plotlyjs=True,
    )

    grafico_componentes(componentes).write_html(
        GRAFICO_DECOMPOSICAO,
        include_plotlyjs=True,
    )

    validos = componentes.dropna(
        subset=["tendencia", "residuo"]
    )

    erro_reconstrucao = (
        validos["observado"]
        - validos["tendencia"]
        - validos["sazonalidade"]
        - validos["residuo"]
    ).abs().max()

    resumo = {
        "aula": 4,
        "assunto": "Tendencia, sazonalidade e ruido",
        "periodo": 7,
        "modelo_decomposicao": "aditivo",
        "calendario": calendario,
        "primeiras_medias_ausentes": int(
            suavizada["media_movel_7"].isna().sum()
        ),
        "tendencia_ausente": int(
            componentes["tendencia"].isna().sum()
        ),
        "residuo_ausente": int(
            componentes["residuo"].isna().sum()
        ),
        "erro_maximo_reconstrucao": float(
            erro_reconstrucao
        ),
        "observacao": (
            "Com lacunas no calendario, period=7 "
            "representa sete observacoes, nao "
            "uma sazonalidade semanal validada."
        ),
        "modelo_preditivo_treinado": False,
    }

    RELATORIO.write_text(
        json.dumps(
            resumo,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print("\n===== AULA 04 =====")
    print("Dias observados:", calendario["dias_observados"])
    print(
        "Dias sem observacao:",
        calendario["dias_sem_observacao"]
    )
    print("\nMEDIA MOVEL:")
    print(suavizada.head(10).to_string(index=False))

    print("\nCOMPONENTES:")
    print(componentes.head(10).to_string(index=False))

    print("\nARQUIVOS GERADOS:")
    for arquivo in [
        CSV_DIARIO,
        CSV_MEDIA_MOVEL,
        CSV_COMPONENTES,
        GRAFICO_MEDIA,
        GRAFICO_DECOMPOSICAO,
        RELATORIO,
    ]:
        print(arquivo)

    print("\nAULA 04 EXECUTADA COM SUCESSO")

    return resumo


if __name__ == "__main__":
    executar_aula()
