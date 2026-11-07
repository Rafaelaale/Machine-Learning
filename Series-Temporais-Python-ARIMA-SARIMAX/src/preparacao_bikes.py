"""Aula 02: validacao e preparacao temporal."""

from pathlib import Path
import json

import pandas as pd

from src.visual_utils import grafico_linha_padrao

RAIZ = Path(__file__).resolve().parent.parent
ORIGEM = RAIZ / "dados" / "bike.csv"
SAIDA = RAIZ / "dados" / "bike_tratado.csv"
GRAFICO = RAIZ / "graficos" / "demanda_bicicletas.html"
RELATORIO = RAIZ / "resultados" / "aula02_validacao.json"

COLUNAS = {
    "datetime": "data_hora",
    "count": "demanda",
    "temp": "temperatura",
    "humidity": "umidade",
    "windspeed": "velocidade_vento",
    "season": "estacao",
    "holiday": "feriado",
    "workingday": "dia_util",
    "casual": "usuarios_casuais",
    "registered": "usuarios_registrados",
    "atemp": "sensacao_termica",
}

DIAS = {
    0: "segunda-feira",
    1: "terça-feira",
    2: "quarta-feira",
    3: "quinta-feira",
    4: "sexta-feira",
    5: "sábado",
    6: "domingo",
}


def carregar_base():
    df = pd.read_csv(ORIGEM)
    if not {"datetime", "count"}.issubset(df.columns):
        raise ValueError("Colunas obrigatorias ausentes.")
    return df


def preparar_base(df):
    df = df.copy().rename(columns=COLUNAS)

    df["data_hora"] = pd.to_datetime(
        df["data_hora"], errors="raise"
    )

    df = df.sort_values("data_hora").reset_index(drop=True)

    if df["data_hora"].duplicated().any():
        raise ValueError("Datas duplicadas.")

    if df["demanda"].isna().any():
        raise ValueError("Demanda com valores nulos.")

    df["ano"] = df["data_hora"].dt.year
    df["mes"] = df["data_hora"].dt.month
    df["dia"] = df["data_hora"].dt.day
    df["hora"] = df["data_hora"].dt.hour
    df["dia_semana"] = df["data_hora"].dt.dayofweek
    df["nome_dia_semana"] = df["dia_semana"].map(DIAS)

    return df.set_index("data_hora")


def executar():
    original = carregar_base()
    temporal = preparar_base(original)
    organizado = temporal.reset_index()

    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    GRAFICO.parent.mkdir(parents=True, exist_ok=True)
    RELATORIO.parent.mkdir(parents=True, exist_ok=True)

    organizado.to_csv(
        SAIDA, index=False, encoding="utf-8-sig"
    )

    fig = grafico_linha_padrao(
        organizado,
        x="data_hora",
        y="demanda",
        titulo="Demanda horaria de bicicletas",
        label_x="Data e hora",
        label_y="Demanda",
    )

    fig.write_html(str(GRAFICO), include_plotlyjs=True)

    resumo = {
        "aula": 2,
        "registros": len(organizado),
        "colunas": len(organizado.columns),
        "valores_ausentes": int(
            organizado.isna().sum().sum()
        ),
        "indice_ordenado": bool(
            temporal.index.is_monotonic_increasing
        ),
        "indice_unico": bool(temporal.index.is_unique),
    }

    RELATORIO.write_text(
        json.dumps(resumo, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print("AULA 02 EXECUTADA")
    print("Registros:", len(organizado))
    print("Base:", SAIDA)
    print("Grafico:", GRAFICO)
    return resumo


if __name__ == "__main__":
    executar()
