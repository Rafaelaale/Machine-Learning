"""Aula 14 - Preparacao de variaveis exogenas para SARIMAX.

Esta aula agrega dados horarios em frequencia diaria,
codifica o dia da semana e separa y e X.
Nenhum modelo SARIMAX e treinado nesta etapa.
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from statsmodels.tsa.statespace.sarimax import SARIMAX


RAIZ = Path(__file__).resolve().parent.parent

BASE_TRATADA = RAIZ / "dados" / "bike_tratado.csv"
BASE_ORIGINAL = RAIZ / "dados" / "bike.csv"

TREINO_REFERENCIA = (
    RAIZ / "resultados" / "aula12_treino_sarima.csv"
)

TESTE_REFERENCIA = (
    RAIZ / "resultados" / "aula12_teste_sarima.csv"
)

RESULTADOS = RAIZ / "resultados"
GRAFICOS = RAIZ / "graficos"

CSV_BASE_DIARIA = (
    RESULTADOS / "aula14_base_diaria_exogenas.csv"
)

CSV_BASE_MODELAGEM = (
    RESULTADOS / "aula14_base_modelagem_sarimax.csv"
)

CSV_TREINO = (
    RESULTADOS / "aula14_treino_sarimax.csv"
)

CSV_TESTE = (
    RESULTADOS / "aula14_teste_sarimax.csv"
)

CSV_X_TREINO = (
    RESULTADOS / "aula14_X_treino.csv"
)

CSV_X_TESTE = (
    RESULTADOS / "aula14_X_teste.csv"
)

CSV_Y_TREINO = (
    RESULTADOS / "aula14_y_treino.csv"
)

CSV_Y_TESTE = (
    RESULTADOS / "aula14_y_teste.csv"
)

CSV_VALIDACAO_CALENDARIO = (
    RESULTADOS / "aula14_validacao_calendario.csv"
)

JSON_RELATORIO = (
    RESULTADOS / "aula14_preparacao_sarimax.json"
)

HTML_CLIMA = (
    GRAFICOS / "aula14_clima_demanda.html"
)

HTML_TREINO_TESTE = (
    GRAFICOS / "aula14_divisao_sarimax.html"
)

COLUNAS_CONTEXT0 = [
    "data_hora",
    "demanda",
    "temperatura",
    "sensacao_termica",
    "umidade",
    "velocidade_vento",
    "feriado",
    "dia_util",
    "dia_semana",
    "mes",
]

MAPA_ORIGINAL = {
    "datetime": "data_hora",
    "count": "demanda",
    "temp": "temperatura",
    "atemp": "sensacao_termica",
    "humidity": "umidade",
    "windspeed": "velocidade_vento",
    "holiday": "feriado",
    "workingday": "dia_util",
}

VARIAVEIS_CLIMA = [
    "temperatura_media",
    "sensacao_termica_media",
    "umidade_media",
    "velocidade_vento_media",
]

VARIAVEIS_CALENDARIO = [
    "feriado",
    "dia_util",
]

DUMMIES_ESPERADAS = [
    f"dia_semana_{dia}" for dia in range(1, 7)
]

VARIAVEIS_EXTERNAS = (
    VARIAVEIS_CLIMA
    + VARIAVEIS_CALENDARIO
    + DUMMIES_ESPERADAS
)

TAMANHO_TESTE = 60


def carregar_base_horaria():
    """Carrega a base preparada ou recupera a base original."""

    fonte = (
        BASE_TRATADA
        if BASE_TRATADA.is_file()
        else BASE_ORIGINAL
    )

    df = pd.read_csv(fonte)

    df = df.rename(columns=MAPA_ORIGINAL)

    if "data_hora" not in df.columns:
        raise ValueError("Coluna data_hora ausente.")

    df["data_hora"] = pd.to_datetime(
        df["data_hora"],
        errors="raise",
    )

    if "dia_semana" not in df.columns:
        df["dia_semana"] = (
            df["data_hora"].dt.dayofweek
        )

    if "mes" not in df.columns:
        df["mes"] = df["data_hora"].dt.month

    faltantes = [
        coluna
        for coluna in COLUNAS_CONTEXT0
        if coluna not in df.columns
    ]

    if faltantes:
        raise ValueError(
            f"Colunas de contexto ausentes: {faltantes}"
        )

    df = df[COLUNAS_CONTEXT0].copy()

    for coluna in COLUNAS_CONTEXT0[1:]:
        df[coluna] = pd.to_numeric(
            df[coluna],
            errors="raise",
        )

    if df.isna().any().any():
        raise ValueError(
            "Base horaria possui valores ausentes."
        )

    if not np.isfinite(
        df[COLUNAS_CONTEXT0[1:]]
        .to_numpy(dtype=float)
    ).all():
        raise ValueError(
            "Base horaria possui valores nao finitos."
        )

    df = (
        df.sort_values("data_hora")
        .reset_index(drop=True)
    )

    if df["data_hora"].duplicated().any():
        raise ValueError(
            "Registros horarios duplicados."
        )

    if not df["dia_semana"].between(0, 6).all():
        raise ValueError(
            "Dia da semana invalido."
        )

    if not df["mes"].between(1, 12).all():
        raise ValueError("Mes invalido.")

    # Confere as colunas derivadas com as datas reais.
    if not (
        df["dia_semana"]
        == df["data_hora"].dt.dayofweek
    ).all():
        raise ValueError(
            "Dia da semana inconsistente com a data."
        )

    if not (
        df["mes"]
        == df["data_hora"].dt.month
    ).all():
        raise ValueError(
            "Mes inconsistente com a data."
        )

    for coluna in ("feriado", "dia_util"):
        if not df[coluna].isin([0, 1]).all():
            raise ValueError(
                f"Coluna binaria invalida: {coluna}"
            )

    return df


def validar_calendario(df):
    """Confere constancia das categorias dentro de cada dia."""

    validacao_calendario = (
        df.assign(
            data=df["data_hora"].dt.floor("D")
        )
        .groupby("data")
        .agg({
            "feriado": "nunique",
            "dia_util": "nunique",
            "dia_semana": "nunique",
            "mes": "nunique",
        })
    )

    if not (
        validacao_calendario == 1
    ).all().all():
        raise ValueError(
            "Informacao de calendario muda "
            "dentro de um mesmo dia."
        )

    return validacao_calendario


def agregar_base_diaria(df):
    """Soma demanda, tira medias climaticas e preserva calendario."""

    validar_calendario(df)

    base_diaria = (
        df.assign(
            data=df["data_hora"].dt.floor("D")
        )
        .groupby("data", as_index=False)
        .agg(
            demanda=("demanda", "sum"),
            temperatura_media=("temperatura", "mean"),
            sensacao_termica_media=(
                "sensacao_termica", "mean"
            ),
            umidade_media=("umidade", "mean"),
            velocidade_vento_media=(
                "velocidade_vento", "mean"
            ),
            feriado=("feriado", "max"),
            dia_util=("dia_util", "max"),
            dia_semana=("dia_semana", "first"),
            mes=("mes", "first"),
        )
        .rename(columns={"data": "data_hora"})
        .sort_values("data_hora")
        .reset_index(drop=True)
    )

    if len(base_diaria) != 456:
        raise ValueError(
            "Esperados 456 dias observados "
            "conforme a base das aulas anteriores."
        )

    if not np.isclose(
        base_diaria["demanda"].sum(),
        df["demanda"].sum(),
    ):
        raise ValueError(
            "Soma diaria nao preservou a demanda."
        )

    return base_diaria


def preparar_base_modelagem(base_diaria):
    """Codifica dia da semana em dummies numericas."""

    categorias = pd.Categorical(
        base_diaria["dia_semana"],
        categories=list(range(7)),
        ordered=False,
    )

    dummies_dia_da_semana = pd.get_dummies(
        categorias,
        prefix="dia_semana",
        drop_first=True,
        dtype=float,
    )

    dummies_dia_da_semana.index = (
        base_diaria.index
    )

    if dummies_dia_da_semana.columns.tolist() != (
        DUMMIES_ESPERADAS
    ):
        raise ValueError(
            "Colunas dummy inesperadas."
        )

    base_modelagem = pd.concat(
        [base_diaria, dummies_dia_da_semana],
        axis=1,
    )

    if base_modelagem.isna().any().any():
        raise ValueError(
            "Base de modelagem possui valores nulos."
        )

    return (
        base_modelagem,
        dummies_dia_da_semana,
        list(VARIAVEIS_EXTERNAS),
    )


def separar_dados(base_modelagem, variaveis_externas):
    """Divide cronologicamente e separa X e y."""

    if len(base_modelagem) <= TAMANHO_TESTE:
        raise ValueError(
            "Base pequena para treino e teste."
        )

    treino = (
        base_modelagem
        .iloc[:-TAMANHO_TESTE]
        .copy()
    )

    teste = (
        base_modelagem
        .iloc[-TAMANHO_TESTE:]
        .copy()
    )

    y_treino = treino["demanda"].astype(float)
    y_teste = teste["demanda"].astype(float)

    X_treino = treino[
        variaveis_externas
    ].astype(float)

    X_teste = teste[
        variaveis_externas
    ].astype(float)

    if len(treino) != 396 or len(teste) != 60:
        raise ValueError(
            "Divisao temporal diferente da Aula 12."
        )

    if treino["data_hora"].max() >= teste["data_hora"].min():
        raise ValueError(
            "Treino e teste se sobrepoem."
        )

    if not X_treino.columns.equals(X_teste.columns):
        raise ValueError(
            "Colunas externas diferentes entre "
            "treino e teste."
        )

    for nome, valores in [
        ("y_treino", y_treino),
        ("y_teste", y_teste),
        ("X_treino", X_treino),
        ("X_teste", X_teste),
    ]:
        if not np.isfinite(
            valores.to_numpy(dtype=float)
        ).all():
            raise ValueError(
                f"Valores invalidos em {nome}"
            )

    return (
        treino,
        teste,
        y_treino,
        y_teste,
        X_treino,
        X_teste,
    )


def verificar_compatibilidade(treino, teste):
    """Garante o mesmo alvo e periodo das aulas anteriores."""

    treino_referencia = pd.read_csv(
        TREINO_REFERENCIA,
        parse_dates=["data_hora"],
    )

    teste_referencia = pd.read_csv(
        TESTE_REFERENCIA,
        parse_dates=["data_hora"],
    )

    for nome, atual, referencia in [
        ("treino", treino, treino_referencia),
        ("teste", teste, teste_referencia),
    ]:
        pd.testing.assert_series_equal(
            atual["data_hora"].reset_index(drop=True),
            referencia["data_hora"].reset_index(drop=True),
            check_names=False,
        )

        np.testing.assert_allclose(
            atual["demanda"].to_numpy(dtype=float),
            referencia["demanda"].to_numpy(dtype=float),
        )

    return True


def diagnosticar_calendario(base_diaria):
    """Conta dias nao observados na serie."""

    datas = pd.DatetimeIndex(
        base_diaria["data_hora"]
    )

    calendario = pd.date_range(
        datas.min(),
        datas.max(),
        freq="D",
    )

    ausentes = calendario.difference(datas)

    return {
        "observacoes_diarias": int(
            len(base_diaria)
        ),
        "dias_ausentes": int(len(ausentes)),
        "indice_diario_regular": bool(
            len(ausentes) == 0
        ),
        "nota": (
            "Datas ausentes nao foram preenchidas. "
            "O ciclo s=7 dos modelos anteriores "
            "representa sete observacoes, nao "
            "necessariamente sete dias de calendario."
        ),
    }


def grafico_clima(base_diaria):
    """Visualiza a demanda e a temperatura media diaria."""

    from plotly.subplots import make_subplots

    fig = make_subplots(
        specs=[[{"secondary_y": True}]]
    )

    fig.add_trace(
        go.Scatter(
            x=base_diaria["data_hora"],
            y=base_diaria["demanda"],
            mode="lines",
            name="Demanda diaria",
            line=dict(color="#003f5c"),
        ),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(
            x=base_diaria["data_hora"],
            y=base_diaria["temperatura_media"],
            mode="lines",
            name="Temperatura media",
            line=dict(color="#d45087"),
        ),
        secondary_y=True,
    )

    fig.update_yaxes(
        title_text="Bicicletas",
        secondary_y=False,
    )

    fig.update_yaxes(
        title_text="Temperatura (escala original da base)",
        secondary_y=True,
    )

    fig.update_layout(
        title="Demanda e temperatura media observada",
        xaxis_title="Data",
        template="plotly_white",
        height=550,
    )

    return fig


def grafico_divisao(treino, teste):
    """Mostra divisao temporal do novo conjunto."""

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=treino["data_hora"],
            y=treino["demanda"],
            mode="lines",
            name="Treino SARIMAX",
            line=dict(color="#003f5c"),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=teste["data_hora"],
            y=teste["demanda"],
            mode="lines",
            name="Teste SARIMAX",
            line=dict(color="#7a9ec2"),
        )
    )

    fig.update_layout(
        title="SARIMAX - separacao temporal",
        xaxis_title="Data",
        yaxis_title="Demanda diaria",
        template="plotly_white",
        height=530,
    )

    return fig


def executar_aula():
    """Prepara e salva os dados para o futuro SARIMAX."""

    df = carregar_base_horaria()

    validacao_calendario = validar_calendario(df)

    base_diaria = agregar_base_diaria(df)

    (
        base_modelagem,
        dummies_dia_da_semana,
        variaveis_externas,
    ) = preparar_base_modelagem(base_diaria)

    (
        treino,
        teste,
        y_treino,
        y_teste,
        X_treino,
        X_teste,
    ) = separar_dados(
        base_modelagem,
        variaveis_externas,
    )

    verificar_compatibilidade(
        treino,
        teste,
    )

    calendario = diagnosticar_calendario(
        base_diaria
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
        (base_diaria, CSV_BASE_DIARIA),
        (base_modelagem, CSV_BASE_MODELAGEM),
        (treino, CSV_TREINO),
        (teste, CSV_TESTE),
        (X_treino, CSV_X_TREINO),
        (X_teste, CSV_X_TESTE),
        (y_treino.to_frame("demanda"), CSV_Y_TREINO),
        (y_teste.to_frame("demanda"), CSV_Y_TESTE),
        (
            validacao_calendario.reset_index(),
            CSV_VALIDACAO_CALENDARIO,
        ),
    ]

    for tabela, caminho in tabelas:
        tabela.to_csv(
            caminho,
            index=False,
            encoding="utf-8-sig",
        )

    grafico_clima(
        base_diaria
    ).write_html(
        str(HTML_CLIMA),
        include_plotlyjs=True,
    )

    grafico_divisao(
        treino,
        teste,
    ).write_html(
        str(HTML_TREINO_TESTE),
        include_plotlyjs=True,
    )

    relatorio = {
        "aula": 14,
        "titulo": (
            "Incorporando variaveis exogenas no SARIMAX"
        ),
        "linhas_horarias": int(len(df)),
        "dias_observados": int(len(base_diaria)),
        "treino": int(len(treino)),
        "teste": int(len(teste)),
        "variaveis_externas": variaveis_externas,
        "quantidade_variaveis_externas": (
            len(variaveis_externas)
        ),
        "colunas_dummy": (
            dummies_dia_da_semana.columns.tolist()
        ),
        "agregacoes": {
            "demanda": "sum",
            "temperatura": "mean",
            "sensacao_termica": "mean",
            "umidade": "mean",
            "velocidade_vento": "mean",
            "feriado": "max",
            "dia_util": "max",
            "dia_semana": "first",
            "mes": "first",
        },
        "divisao_compativel_aula12": True,
        "calendario": calendario,
        "variaveis_climaticas_teste": (
            "Valores historicos observados. "
            "Uma previsao futura real dependera "
            "de informacoes meteorologicas "
            "disponiveis no momento da previsao."
        ),
        "sarimax_treinado": False,
        "previsoes_sarimax_geradas": False,
        "proxima_aula": (
            "Treinar SARIMAX com variaveis externas"
        ),
    }

    JSON_RELATORIO.write_text(
        json.dumps(
            relatorio,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print("\n===== AULA 14 - PREPARACAO SARIMAX =====")

    print("\nBASE HORARIA:")
    print("Registros:", len(df))
    print("Colunas de contexto:", len(df.columns))
    print(df.head(3).to_string(index=False))

    print("\nBASE DIARIA:")
    print("Dias observados:", len(base_diaria))
    print(base_diaria.head().to_string(index=False))

    print("\nVALIDACAO DE CALENDARIO:")
    print(
        (validacao_calendario == 1)
        .all()
        .to_string()
    )

    print("\nVARIAVEIS EXTERNAS:")
    for nome in variaveis_externas:
        print(" -", nome)

    print("\nDIVISAO TEMPORAL:")
    print("Treino:", len(treino))
    print("Teste:", len(teste))
    print(
        "Periodo treino:",
        treino["data_hora"].min(),
        "ate",
        treino["data_hora"].max(),
    )
    print(
        "Periodo teste:",
        teste["data_hora"].min(),
        "ate",
        teste["data_hora"].max(),
    )

    print("\nFORMATO DE X E y:")
    print("X_treino:", X_treino.shape)
    print("X_teste:", X_teste.shape)
    print("y_treino:", y_treino.shape)
    print("y_teste:", y_teste.shape)

    print("\nDIAS AUSENTES:", calendario["dias_ausentes"])
    print("DIVISAO IDENTICA A AULA 12: SIM")
    print("SARIMAX TREINADO: NAO")

    print("\nAULA 14 EXECUTADA COM SUCESSO")

    return relatorio


if __name__ == "__main__":
    executar_aula()
