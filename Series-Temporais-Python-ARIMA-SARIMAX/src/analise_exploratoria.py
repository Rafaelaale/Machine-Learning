"""Aula 03: exploracao visual da demanda de bicicletas."""

from pathlib import Path
import json

import pandas as pd

from src.visual_utils import (
    grafico_linha_padrao,
    grafico_barra_padrao,
)
from src.preparacao_bikes import (
    carregar_base,
    preparar_base,
)

RAIZ = Path(__file__).resolve().parent.parent
TRATADA = RAIZ / "dados" / "bike_tratado.csv"
SERIE_DIARIA = RAIZ / "resultados" / "serie_diaria_bike.csv"
RELATORIO = RAIZ / "resultados" / "aula03_analise_exploratoria.json"
PASTA_GRAFICOS = RAIZ / "graficos"

ORDEM_DIAS = [
    "segunda-feira",
    "terça-feira",
    "quarta-feira",
    "quinta-feira",
    "sexta-feira",
    "sábado",
    "domingo",
]


def carregar_dados():
    if TRATADA.is_file():
        df = pd.read_csv(TRATADA)
    else:
        df = preparar_base(carregar_base()).reset_index()

    df["data_hora"] = pd.to_datetime(
        df["data_hora"], errors="raise"
    )

    return df.sort_values("data_hora").reset_index(drop=True)


def agregar_dados(df):
    diaria = (
        df.assign(data=df["data_hora"].dt.floor("D"))
        .groupby("data", as_index=False)
        .agg(demanda_diaria=("demanda", "sum"))
        .rename(columns={"data": "data_hora"})
    )

    por_hora = (
        df.groupby("hora", as_index=False)
        .agg(demanda_media=("demanda", "mean"))
    )

    por_dia = (
        df.groupby("nome_dia_semana", as_index=False)
        .agg(demanda_media=("demanda", "mean"))
    )

    por_dia["nome_dia_semana"] = pd.Categorical(
        por_dia["nome_dia_semana"],
        categories=ORDEM_DIAS,
        ordered=True,
    )

    por_dia = por_dia.sort_values("nome_dia_semana")

    por_mes = (
        df.groupby("mes", as_index=False)
        .agg(demanda_media=("demanda", "mean"))
        .sort_values("mes")
    )

    return diaria, por_hora, por_dia, por_mes


def gerar_graficos(df, diaria, hora, dia, mes):
    graficos = {
        "01_demanda_horaria": grafico_linha_padrao(
            df, "data_hora", "demanda",
            titulo="Demanda horaria",
            label_x="Data e hora",
            label_y="Demanda",
        ),
        "02_demanda_diaria": grafico_linha_padrao(
            diaria, "data_hora", "demanda_diaria",
            titulo="Demanda diaria",
            label_x="Data",
            label_y="Demanda diaria",
        ),
        "03_media_por_hora": grafico_barra_padrao(
            hora, "hora", "demanda_media",
            titulo="Demanda media por hora",
        ),
        "04_media_por_dia_semana": grafico_barra_padrao(
            dia, "nome_dia_semana", "demanda_media",
            titulo="Demanda media por dia da semana",
        ),
        "05_media_por_mes": grafico_barra_padrao(
            mes, "mes", "demanda_media",
            titulo="Demanda media por mes",
        ),
    }

    graficos["04_media_por_dia_semana"].update_xaxes(
        categoryorder="array",
        categoryarray=ORDEM_DIAS,
    )

    PASTA_GRAFICOS.mkdir(parents=True, exist_ok=True)

    for nome, fig in graficos.items():
        fig.write_html(
            str(PASTA_GRAFICOS / f"{nome}.html"),
            include_plotlyjs=True,
        )

    return graficos


def executar():
    df = carregar_dados()
    diaria, hora, dia, mes = agregar_dados(df)

    SERIE_DIARIA.parent.mkdir(
        parents=True, exist_ok=True
    )

    diaria.to_csv(
        SERIE_DIARIA,
        index=False,
        encoding="utf-8-sig",
    )

    graficos = gerar_graficos(
        df, diaria, hora, dia, mes
    )

    resumo = {
        "aula": 3,
        "observacoes_horarias": len(df),
        "dias_observados": len(diaria),
        "demanda_total_original": int(df["demanda"].sum()),
        "demanda_total_diaria": int(
            diaria["demanda_diaria"].sum()
        ),
        "graficos_gerados": list(graficos),
        "modelo_treinado": False,
    }

    RELATORIO.write_text(
        json.dumps(resumo, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print("AULA 03 EXECUTADA")
    print("Dias observados:", len(diaria))
    print("Graficos gerados:", len(graficos))
    print("Serie diaria:", SERIE_DIARIA)

    return resumo


if __name__ == "__main__":
    executar()
