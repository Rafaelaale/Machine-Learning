from pathlib import Path
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    ConfusionMatrixDisplay
)

BASE = Path(r"F:\AWS-CIENCIA-DE-DADOS-SEGURANCA-CUSTOS")
PROCESSED = BASE / "s3_local" / "hospital-dados" / "processed"
RESULTADOS = BASE / "resultados"
TARGET = "HeartDisease"


def carregar_dados():
    treino = pd.read_csv(
        PROCESSED / "heart_treino_processado.csv"
    )
    teste = pd.read_csv(
        PROCESSED / "heart_teste_processado.csv"
    )

    assert treino.shape[0] == 688
    assert teste.shape[0] == 230
    assert TARGET in treino.columns
    assert TARGET in teste.columns

    train_X = treino.drop(columns=[TARGET])
    test_X = teste.drop(columns=[TARGET])

    train_y = treino[TARGET]
    test_y = teste[TARGET]

    assert train_X.columns.tolist() == test_X.columns.tolist()
    assert not train_X.isna().any().any()
    assert not test_X.isna().any().any()
    assert set(train_y.unique()) <= {0, 1}
    assert set(test_y.unique()) <= {0, 1}

    return train_X, test_X, train_y, test_y


def avaliar(nome, modelo, train_X, train_y, test_X, test_y):
    print(f"\n===== MODELO: {nome} =====")

    modelo.fit(train_X, train_y)
    previsoes = modelo.predict(test_X)

    matriz = confusion_matrix(
        test_y, previsoes, labels=[0, 1]
    )

    tn, fp, fn, tp = matriz.ravel()

    metricas = {
        "acuracia": float(accuracy_score(test_y, previsoes)),
        "precisao": float(
            precision_score(test_y, previsoes, zero_division=0)
        ),
        "recall": float(
            recall_score(test_y, previsoes, zero_division=0)
        ),
        "f1_score": float(
            f1_score(test_y, previsoes, zero_division=0)
        ),
        "verdadeiros_negativos": int(tn),
        "falsos_positivos": int(fp),
        "falsos_negativos": int(fn),
        "verdadeiros_positivos": int(tp),
    }

    for chave in ("acuracia", "precisao", "recall", "f1_score"):
        print(f"{chave}: {metricas[chave]:.4f}")

    print("Matriz de confusao:")
    print(matriz)
    print("Falsos negativos:", fn)
    print("Falsos positivos:", fp)

    disp = ConfusionMatrixDisplay(
        confusion_matrix=matriz,
        display_labels=["Sem doenca", "Com doenca"]
    )

    disp.plot(cmap="Purples", values_format="d")
    plt.title(f"Matriz de confusao - {nome}")
    plt.tight_layout()

    nome_arquivo = (
        "regressao_logistica"
        if nome == "Regressao Logistica"
        else "knn"
    )

    grafico = RESULTADOS / (
        f"aula_13_matriz_{nome_arquivo}.png"
    )

    plt.savefig(grafico, dpi=150, bbox_inches="tight")
    plt.close()

    assert int(matriz.sum()) == 230
    assert 0 <= metricas["recall"] <= 1
    assert grafico.is_file()

    print("Grafico:", grafico)

    return metricas


def main():
    print("===== AULA 13 - MACHINE LEARNING =====")
    print("Ambiente: local, sem AWS")
    print("Objetivo: comparacao educativa de classificadores")

    RESULTADOS.mkdir(parents=True, exist_ok=True)

    train_X, test_X, train_y, test_y = carregar_dados()

    print("\n===== DADOS =====")
    print("Treinamento:", train_X.shape)
    print("Teste:", test_X.shape)
    print("Classes treino:", train_y.value_counts().to_dict())
    print("Classes teste:", test_y.value_counts().to_dict())

    modelos = {
        "Regressao Logistica": LogisticRegression(
            max_iter=1000,
            random_state=42
        ),
        "KNN": KNeighborsClassifier(
            n_neighbors=7
        )
    }

    resultados = {}

    for nome, modelo in modelos.items():
        resultados[nome] = avaliar(
            nome,
            modelo,
            train_X,
            train_y,
            test_X,
            test_y
        )

    print("\n===== COMPARACAO =====")

    for nome, metricas in resultados.items():
        print(
            f"{nome}: "
            f"acuracia={metricas['acuracia']:.4f}, "
            f"precisao={metricas['precisao']:.4f}, "
            f"recall={metricas['recall']:.4f}, "
            f"F1={metricas['f1_score']:.4f}, "
            f"FN={metricas['falsos_negativos']}"
        )

    relatorio = {
        "aula": 13,
        "objetivo": "classificacao educativa de doenca cardiaca",
        "treino": len(train_X),
        "teste": len(test_X),
        "features": train_X.columns.tolist(),
        "modelos": resultados,
        "observacao": (
            "Resultados de demonstracao em dataset historico. "
            "Nao utilizar para diagnostico ou triagem clinica."
        ),
        "modelos_salvos": False,
        "recursos_aws_criados": 0
    }

    caminho = RESULTADOS / "aula_13_comparacao_modelos.json"

    caminho.write_text(
        json.dumps(relatorio, indent=4, ensure_ascii=False),
        encoding="utf-8"
    )

    assert len(resultados) == 2
    assert all(
        m["verdadeiros_negativos"]
        + m["falsos_positivos"]
        + m["falsos_negativos"]
        + m["verdadeiros_positivos"] == 230
        for m in resultados.values()
    )
    assert caminho.is_file()

    print("\n===== VALIDACAO FINAL =====")
    print("TESTES: 6/6 APROVADOS")
    print("RELATORIO:", caminho)
    print("AULA 13 - MODELOS TREINADOS E AVALIADOS")


if __name__ == "__main__":
    main()
