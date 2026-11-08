"""Aula 03 - Ambiente, dataset e baseline de risco de credito.

Gera dados sinteticos, analisa distribuicoes,
separa treino e teste e prepara o pipeline.

O modelo ainda NAO e treinado nesta etapa.
"""

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


RAIZ = Path(__file__).resolve().parent.parent

DADOS = RAIZ / "dados"
RESULTADOS = RAIZ / "resultados"
GRAFICOS = RAIZ / "graficos"

RANDOM_STATE = 42
TARGET = "inadimplente"

NUM_COLS = [
    "idade",
    "renda_mensal",
    "tempo_emprego_anos",
    "score_interno",
    "valor_solicitado",
    "num_parcelas",
]

CAT_COLS = [
    "tipo_renda",
    "possui_restricao",
]

FEATURES = NUM_COLS + CAT_COLS

COLUNAS = FEATURES + [TARGET]


def gerar_base_credito(
    n_amostras: int = 5000,
    random_state: int = RANDOM_STATE,
) -> pd.DataFrame:
    """Reproduz a geracao sintetica apresentada na aula."""

    if n_amostras < 10:
        raise ValueError("Numero insuficiente de registros.")

    rng = np.random.default_rng(random_state)
    n = n_amostras

    idade = rng.integers(22, 66, size=n)

    renda_mensal = rng.lognormal(
        mean=np.log(3500),
        sigma=0.45,
        size=n,
    ).round(2)

    tempo_emprego_anos = rng.exponential(
        scale=4,
        size=n,
    ).clip(0, 35).round(1)

    score_interno = rng.normal(
        loc=650,
        scale=125,
        size=n,
    ).clip(300, 900).astype(int)

    valor_solicitado = rng.lognormal(
        mean=np.log(8000),
        sigma=0.6,
        size=n,
    ).round(2)

    num_parcelas = rng.choice(
        [6, 12, 18, 24, 36, 48, 60],
        size=n,
    )

    tipo_renda = rng.choice(
        ["CLT", "autonomo", "aposentado"],
        size=n,
        p=[0.65, 0.22, 0.13],
    )

    possui_restricao = rng.choice(
        ["sim", "nao"],
        size=n,
        p=[0.12, 0.88],
    )

    z = (
        3.2
        - 0.025 * (score_interno - 650)
        - 0.15 * tempo_emprego_anos
        + 0.0002 * valor_solicitado
        - 0.0003 * renda_mensal
    )

    z = np.asarray(z, dtype=float)

    z += np.where(
        possui_restricao == "sim",
        0.85,
        0,
    )

    z += np.where(
        tipo_renda == "autonomo",
        0.35,
        0,
    )

    z += rng.normal(0, 0.75, size=n)

    p_default = 1 / (1 + np.exp(-z))

    inadimplente = rng.binomial(
        1,
        p_default,
    )

    return pd.DataFrame({
        "idade": idade,
        "renda_mensal": renda_mensal,
        "tempo_emprego_anos": tempo_emprego_anos,
        "score_interno": score_interno,
        "valor_solicitado": valor_solicitado,
        "num_parcelas": num_parcelas,
        "tipo_renda": tipo_renda,
        "possui_restricao": possui_restricao,
        "inadimplente": inadimplente,
    })


def preparar_divisao(df):
    """Separa features e target com estratificacao."""

    if df.columns.tolist() != COLUNAS:
        raise ValueError("Colunas do dataset incorretas.")

    if df[TARGET].nunique() != 2:
        raise ValueError("A variavel alvo precisa ter duas classes.")

    X = df[FEATURES]
    y = df[TARGET]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.25,
        stratify=y,
        random_state=RANDOM_STATE,
    )

    return X_train, X_test, y_train, y_test


def construir_pipeline():
    """Constroi pre-processamento e baseline nao treinado."""

    numeric_pipe = Pipeline(
        steps=[
            (
                "imputer",
                SimpleImputer(strategy="median"),
            ),
            (
                "scaler",
                StandardScaler(),
            ),
        ]
    )

    categorical_pipe = Pipeline(
        steps=[
            (
                "imputer",
                SimpleImputer(strategy="most_frequent"),
            ),
            (
                "onehot",
                OneHotEncoder(handle_unknown="ignore"),
            ),
        ]
    )

    preprocess = ColumnTransformer(
        transformers=[
            ("num", numeric_pipe, NUM_COLS),
            ("cat", categorical_pipe, CAT_COLS),
        ]
    )

    clf = LogisticRegression(
        max_iter=2000,
        class_weight="balanced",
        random_state=RANDOM_STATE,
    )

    model_pipe = Pipeline(
        steps=[
            ("prep", preprocess),
            ("model", clf),
        ]
    )

    return model_pipe


def salvar_se_nao_existir(df, caminho):
    """Preserva arquivos gerados anteriormente."""

    if caminho.is_file():
        existente = pd.read_csv(caminho)

        pd.testing.assert_frame_equal(
            existente.reset_index(drop=True),
            df.reset_index(drop=True),
            check_dtype=False,
            check_exact=False,
            rtol=1e-8,
            atol=1e-8,
        )

        print("PRESERVADO E VALIDADO:", caminho.name)
    else:
        df.to_csv(
            caminho,
            index=False,
            encoding="utf-8-sig",
        )
        print("CRIADO:", caminho.name)


def criar_graficos(df):
    """Exploracao: score, renda e classe alvo."""

    GRAFICOS.mkdir(parents=True, exist_ok=True)

    grafico_1 = GRAFICOS / "aula03_distribuicao_classes.png"
    grafico_2 = GRAFICOS / "aula03_score_por_classe.png"
    grafico_3 = GRAFICOS / "aula03_renda_por_classe.png"

    distribuicao = (
        df[TARGET].value_counts()
        .sort_index()
    )

    if not grafico_1.exists():
        fig, ax = plt.subplots(figsize=(8, 5))

        ax.bar(
            ["Adimplente (0)", "Inadimplente (1)"],
            [distribuicao.get(0, 0), distribuicao.get(1, 0)],
        )

        ax.set_title("Distribuicao do risco de credito")
        ax.set_ylabel("Quantidade de registros")

        fig.tight_layout()
        fig.savefig(grafico_1, dpi=140)
        plt.close(fig)

    for coluna, titulo, caminho in (
        (
            "score_interno",
            "Score interno por classe",
            grafico_2,
        ),
        (
            "renda_mensal",
            "Renda mensal por classe",
            grafico_3,
        ),
    ):
        if caminho.exists():
            continue

        grupo_0 = df.loc[
            df[TARGET] == 0,
            coluna,
        ]

        grupo_1 = df.loc[
            df[TARGET] == 1,
            coluna,
        ]

        fig, ax = plt.subplots(figsize=(8, 5))

        ax.boxplot(
            [grupo_0, grupo_1],
            tick_labels=["Adimplente", "Inadimplente"],
            showfliers=False,
        )

        ax.set_title(titulo)
        ax.set_ylabel(coluna)

        fig.tight_layout()
        fig.savefig(caminho, dpi=140)
        plt.close(fig)

    return [grafico_1, grafico_2, grafico_3]


def executar_aula():
    """Salva dataset, divisao, graficos e relatorio."""

    DADOS.mkdir(parents=True, exist_ok=True)
    RESULTADOS.mkdir(parents=True, exist_ok=True)

    df = gerar_base_credito(
        n_amostras=6000,
        random_state=RANDOM_STATE,
    )

    X_train, X_test, y_train, y_test = (
        preparar_divisao(df)
    )

    model_pipe = construir_pipeline()

    # O classificador nao deve possuir coeficientes
    # antes do primeiro treinamento.
    if hasattr(model_pipe.named_steps["model"], "coef_"):
        raise RuntimeError(
            "O baseline nao deveria estar treinado."
        )

    treino = X_train.copy()
    treino[TARGET] = y_train

    teste = X_test.copy()
    teste[TARGET] = y_test

    caminhos = [
        (df, DADOS / "aula03_base_credito_sintetica.csv"),
        (treino, DADOS / "aula03_treino_credito.csv"),
        (teste, DADOS / "aula03_teste_credito.csv"),
    ]

    for tabela, caminho in caminhos:
        salvar_se_nao_existir(
            tabela,
            caminho,
        )

    graficos = criar_graficos(df)

    contagem = (
        df[TARGET]
        .value_counts()
        .sort_index()
    )

    percentual = (
        df[TARGET]
        .value_counts(normalize=True)
        .sort_index()
        .mul(100)
    )

    relatorio = {
        "aula": 3,
        "tema": "Ambiente e dataset",
        "origem_dados": "Sinteticos, conforme transcricao Alura",
        "random_state": RANDOM_STATE,
        "target": TARGET,
        "features": FEATURES,
        "colunas_numericas": NUM_COLS,
        "colunas_categoricas": CAT_COLS,
        "registros_total": len(df),
        "registros_treino": len(X_train),
        "registros_teste": len(X_test),
        "quantidade_adimplentes": int(contagem.get(0, 0)),
        "quantidade_inadimplentes": int(contagem.get(1, 0)),
        "percentual_inadimplentes": float(
            percentual.get(1, 0.0)
        ),
        "baseline": "LogisticRegression",
        "max_iter": 2000,
        "class_weight": "balanced",
        "pipeline_preparado": True,
        "modelo_treinado": False,
        "mlflow_run_criada": False,
        "graficos": [
            str(p.relative_to(RAIZ))
            for p in graficos
        ],
    }

    arquivo_relatorio = (
        RESULTADOS / "aula03_ambiente_dataset.json"
    )

    if not arquivo_relatorio.exists():
        arquivo_relatorio.write_text(
            json.dumps(
                relatorio,
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

    print("\n===== AULA 03 - AMBIENTE E DATASET =====")
    print("\nPRIMEIROS CINCO REGISTROS:")
    print(df.head().to_string(index=False))

    print("\nULTIMOS CINCO REGISTROS:")
    print(df.tail().to_string(index=False))

    print("\nDISTRIBUICAO DA CLASSE:")
    print(contagem.to_string())

    print("\nPERCENTUAIS:")
    print(percentual.round(2).to_string())

    print("\nSHAPES:")
    print("BASE:", df.shape)
    print("X_TRAIN:", X_train.shape)
    print("X_TEST:", X_test.shape)
    print("Y_TRAIN:", y_train.shape)
    print("Y_TEST:", y_test.shape)

    print("\nPIPELINE:")
    print(model_pipe)

    print("\nGRAFICOS:", len(graficos))
    print("BASELINE CONFIGURADO: SIM")
    print("BASELINE TREINADO: NAO")
    print("RUN MLFLOW CRIADA: NAO")
    print("AULA 03 EXECUTADA COM SUCESSO")

    return relatorio


if __name__ == "__main__":
    executar_aula()
