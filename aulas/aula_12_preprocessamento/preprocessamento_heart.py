from pathlib import Path
import json

import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

BASE = Path(r"F:\AWS-CIENCIA-DE-DADOS-SEGURANCA-CUSTOS")
SPLIT = BASE / "resultados" / "aula_11_split"
PROCESSED = BASE / "s3_local" / "hospital-dados" / "processed"
RESULTADOS = BASE / "resultados"

CONTINUAS = [
    "Age", "RestingBP", "Cholesterol", "MaxHR", "Oldpeak"
]

CATEGORICAS = [
    "ChestPainType", "Sex", "RestingECG", "ST_Slope"
]

TARGET = "HeartDisease"


def carregar():
    treino = pd.read_csv(SPLIT / "treino.csv")
    teste = pd.read_csv(SPLIT / "teste.csv")

    assert treino.shape == (688, 12)
    assert teste.shape == (230, 12)

    train_X = treino.drop(columns=[TARGET]).copy()
    test_X = teste.drop(columns=[TARGET]).copy()

    train_y = treino[TARGET].copy()
    test_y = teste[TARGET].copy()

    return train_X, test_X, train_y, test_y


def main():
    print("===== AULA 12 - PRE-PROCESSAMENTO =====")
    print("Modo: LOCAL - SEM AWS")

    PROCESSED.mkdir(parents=True, exist_ok=True)
    RESULTADOS.mkdir(parents=True, exist_ok=True)

    train_X, test_X, train_y, test_y = carregar()

    print("\n===== CONJUNTOS ORIGINAIS =====")
    print("Treino:", train_X.shape)
    print("Teste:", test_X.shape)

    print("\n===== DISTRIBUICAO DAS CLASSES =====")
    print("Treino:", train_y.value_counts().to_dict())
    print("Teste:", test_y.value_counts().to_dict())

    print("\n===== TRATANDO VALORES ZERO =====")

    # Calculamos as medianas somente com o treinamento.
    medianas = {}

    for coluna in ("Cholesterol", "RestingBP"):
        valores_validos = train_X.loc[
            train_X[coluna] > 0, coluna
        ]

        if valores_validos.empty:
            raise ValueError(
                f"Nenhum valor valido para {coluna}"
            )

        mediana = float(valores_validos.median())
        medianas[coluna] = mediana

        zeros_treino = int((train_X[coluna] == 0).sum())
        zeros_teste = int((test_X[coluna] == 0).sum())

        train_X[coluna] = train_X[coluna].replace(0, mediana)
        test_X[coluna] = test_X[coluna].replace(0, mediana)

        print(
            f"{coluna}: mediana={mediana}, "
            f"zeros treino={zeros_treino}, "
            f"zeros teste={zeros_teste}"
        )

    # Oldpeak igual a zero pode ser valido.
    # Nao realizamos substituicao nessa coluna.

    print("\n===== CODIFICANDO EXERCISEANGINA =====")

    mapa = {"N": 0, "Y": 1}

    train_X["ExerciseAngina"] = (
        train_X["ExerciseAngina"].map(mapa)
    )

    test_X["ExerciseAngina"] = (
        test_X["ExerciseAngina"].map(mapa)
    )

    assert train_X["ExerciseAngina"].notna().all()
    assert test_X["ExerciseAngina"].notna().all()

    print("ExerciseAngina: N=0, Y=1")

    print("\n===== ONE-HOT ENCODING =====")

    train_X = pd.get_dummies(
        train_X,
        columns=CATEGORICAS,
        drop_first=False,
        dtype=float
    )

    test_X = pd.get_dummies(
        test_X,
        columns=CATEGORICAS,
        drop_first=False,
        dtype=float
    )

    # As categorias sao definidas pelo conjunto de treino.
    # Categorias novas no teste nao criam colunas extras.
    colunas_antes_remocao = train_X.columns.tolist()

    test_X = test_X.reindex(
        columns=colunas_antes_remocao,
        fill_value=0.0
    )

    print("Colunas apos codificacao:", len(train_X.columns))

    print("\n===== REMOVENDO COLUNAS REDUNDANTES =====")

    remover = ["Sex_M", "ST_Slope_Flat"]
    removidas = [c for c in remover if c in train_X.columns]

    train_X = train_X.drop(columns=removidas)
    test_X = test_X.drop(columns=removidas)

    print("Colunas removidas:", removidas)

    train_X = train_X.astype(float)
    test_X = test_X.astype(float)

    print("\n===== NORMALIZANDO VARIAVEIS CONTINUAS =====")

    scaler = StandardScaler()

    train_X.loc[:, CONTINUAS] = scaler.fit_transform(
        train_X[CONTINUAS]
    )

    # Nao executar fit novamente no conjunto de teste.
    test_X.loc[:, CONTINUAS] = scaler.transform(
        test_X[CONTINUAS]
    )

    print("StandardScaler ajustado somente no treino.")

    print("\n===== VERIFICANDO DADOS PROCESSADOS =====")

    assert train_X.columns.tolist() == test_X.columns.tolist()
    assert not train_X.isna().any().any()
    assert not test_X.isna().any().any()

    assert np.isfinite(train_X.to_numpy()).all()
    assert np.isfinite(test_X.to_numpy()).all()

    assert len(train_X) == 688
    assert len(test_X) == 230

    # Apenas o treino deve apresentar media aproximada de zero.
    medias = train_X[CONTINUAS].mean().abs().max()
    assert medias < 1e-10

    print("Treino processado:", train_X.shape)
    print("Teste processado:", test_X.shape)
    print("Valores nulos: 0")
    print("Colunas identicas: SIM")

    print("\n===== SALVANDO DADOS =====")

    treino_final = train_X.copy()
    treino_final[TARGET] = train_y.to_numpy()

    teste_final = test_X.copy()
    teste_final[TARGET] = test_y.to_numpy()

    caminho_treino = PROCESSED / "heart_treino_processado.csv"
    caminho_teste = PROCESSED / "heart_teste_processado.csv"

    treino_final.to_csv(caminho_treino, index=False)
    teste_final.to_csv(caminho_teste, index=False)

    artefatos = {
        "scaler": scaler,
        "medianas": medianas,
        "mapa_exercise_angina": mapa,
        "categoricas": CATEGORICAS,
        "continuas": CONTINUAS,
        "colunas_antes_remocao": colunas_antes_remocao,
        "colunas_removidas": removidas,
        "colunas_finais": train_X.columns.tolist(),
    }

    caminho_artefatos = RESULTADOS / "aula_12_preprocessador.joblib"
    joblib.dump(artefatos, caminho_artefatos)

    print("Treino:", caminho_treino)
    print("Teste:", caminho_teste)
    print("Transformacoes:", caminho_artefatos)

    print("\n===== MATRIZ DE CORRELACAO =====")

    correlacoes = treino_final.corr(numeric_only=True)

    fig, ax = plt.subplots(figsize=(15, 13))

    imagem = ax.imshow(
        correlacoes.to_numpy(),
        cmap="coolwarm",
        vmin=-1,
        vmax=1
    )

    ax.set_xticks(range(len(correlacoes.columns)))
    ax.set_yticks(range(len(correlacoes.columns)))

    ax.set_xticklabels(
        correlacoes.columns,
        rotation=90,
        fontsize=8
    )

    ax.set_yticklabels(
        correlacoes.columns,
        fontsize=8
    )

    fig.colorbar(imagem, ax=ax)
    ax.set_title("Correlacoes - conjunto de treino")
    fig.tight_layout()

    caminho_grafico = RESULTADOS / "aula_12_correlacoes.png"
    fig.savefig(caminho_grafico, dpi=140)
    plt.close(fig)

    print("Grafico:", caminho_grafico)

    relatorio = {
        "aula": 12,
        "modo": "local",
        "treino": len(train_X),
        "teste": len(test_X),
        "colunas_features": len(train_X.columns),
        "medianas_aprendidas_no_treino": medianas,
        "colunas_removidas": removidas,
        "escalonador_ajustado_somente_no_treino": True,
        "colunas_treino_teste_identicas": True,
        "custo_aws": 0
    }

    caminho_relatorio = RESULTADOS / "aula_12_preprocessamento.json"

    caminho_relatorio.write_text(
        json.dumps(relatorio, indent=4, ensure_ascii=False),
        encoding="utf-8"
    )

    assert caminho_treino.exists()
    assert caminho_teste.exists()
    assert caminho_artefatos.exists()
    assert caminho_grafico.exists()
    assert caminho_relatorio.exists()

    print("\n===== VALIDACAO FINAL =====")
    print("TESTES: 10/10 APROVADOS")
    print("RELATORIO:", caminho_relatorio)
    print("AULA 12 - PRE-PROCESSAMENTO CONCLUIDO")


if __name__ == "__main__":
    main()
