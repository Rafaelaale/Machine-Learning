from pathlib import Path
import hashlib
import json

import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix
)

BASE = Path(r"F:\AWS-CIENCIA-DE-DADOS-SEGURANCA-CUSTOS")

PROCESSED = BASE / "s3_local" / "hospital-dados" / "processed"
PREDICTIONS = BASE / "s3_local" / "hospital-dados" / "predictions"
RESULTADOS = BASE / "resultados"

TARGET = "HeartDisease"


def hash_arquivo(caminho):
    digest = hashlib.sha256()

    with caminho.open("rb") as arquivo:
        for bloco in iter(
            lambda: arquivo.read(1024 * 1024), b""
        ):
            digest.update(bloco)

    return digest.hexdigest()


def main():
    print("===== AULA 14 - PERSISTENCIA DE MODELO =====")
    print("Ambiente: LOCAL - SEM CONEXAO AWS")

    PREDICTIONS.mkdir(parents=True, exist_ok=True)
    RESULTADOS.mkdir(parents=True, exist_ok=True)

    treino_path = PROCESSED / "heart_treino_processado.csv"
    teste_path = PROCESSED / "heart_teste_processado.csv"
    preprocessador_path = (
        RESULTADOS / "aula_12_preprocessador.joblib"
    )

    for caminho in (
        treino_path,
        teste_path,
        preprocessador_path
    ):
        if not caminho.is_file():
            raise FileNotFoundError(
                f"Arquivo necessario ausente: {caminho}"
            )

    print("\n===== CARREGANDO DADOS PROCESSADOS =====")

    treino = pd.read_csv(treino_path)
    teste = pd.read_csv(teste_path)

    train_X = treino.drop(columns=[TARGET])
    train_y = treino[TARGET]

    test_X = teste.drop(columns=[TARGET])
    test_y = teste[TARGET]

    assert train_X.shape == (688, 17)
    assert test_X.shape == (230, 17)
    assert train_X.columns.tolist() == test_X.columns.tolist()

    # O artefato de pre-processamento e confiavel
    # porque foi criado por este proprio projeto.
    preprocessador = joblib.load(preprocessador_path)

    assert (
        preprocessador["colunas_finais"]
        == train_X.columns.tolist()
    )

    print("Treinamento:", train_X.shape)
    print("Teste:", test_X.shape)
    print("Pre-processador da Aula 12: validado")

    print("\n===== TREINANDO REGRESSAO LOGISTICA =====")

    modelo = LogisticRegression(
        max_iter=1000,
        random_state=42
    )

    modelo.fit(train_X, train_y)

    previsoes = modelo.predict(test_X)

    metricas = {
        "acuracia": float(
            accuracy_score(test_y, previsoes)
        ),
        "precisao": float(
            precision_score(test_y, previsoes)
        ),
        "recall": float(
            recall_score(test_y, previsoes)
        ),
        "f1_score": float(
            f1_score(test_y, previsoes)
        )
    }

    matriz = confusion_matrix(
        test_y, previsoes, labels=[0, 1]
    )

    tn, fp, fn, tp = matriz.ravel()

    print("Acuracia:", f"{metricas['acuracia']:.4f}")
    print("Precisao:", f"{metricas['precisao']:.4f}")
    print("Recall:", f"{metricas['recall']:.4f}")
    print("F1:", f"{metricas['f1_score']:.4f}")

    print("\n===== SALVANDO PREVISOES =====")

    df_test_pred = test_X.copy()

    df_test_pred["HeartDisease_real"] = (
        test_y.to_numpy()
    )

    df_test_pred["HeartDisease_pred"] = previsoes

    arquivo_csv = (
        PREDICTIONS / "test_predictions.csv"
    )

    df_test_pred.to_csv(
        arquivo_csv,
        index=False
    )

    print(df_test_pred.head().to_string(index=False))
    print("CSV salvo:", arquivo_csv)

    print("\n===== SALVANDO MODELO COM JOBLIB =====")

    modelo_path = (
        PREDICTIONS / "log_reg_model.pkl"
    )

    joblib.dump(modelo, modelo_path)

    if not modelo_path.is_file():
        raise RuntimeError(
            "O arquivo do modelo nao foi criado."
        )

    print("Modelo salvo:", modelo_path)

    print("\n===== RECARREGANDO MODELO =====")

    modelo_recarregado = joblib.load(modelo_path)

    previsoes_recarregadas = (
        modelo_recarregado.predict(test_X)
    )

    assert np.array_equal(
        previsoes,
        previsoes_recarregadas
    )

    print("Modelo carregado novamente: OK")
    print("Previsoes identicas: SIM")

    print("\n===== VALIDANDO CSV =====")

    csv_recarregado = pd.read_csv(arquivo_csv)

    assert len(csv_recarregado) == 230
    assert "HeartDisease_real" in csv_recarregado.columns
    assert "HeartDisease_pred" in csv_recarregado.columns

    assert np.array_equal(
        csv_recarregado["HeartDisease_pred"].to_numpy(),
        previsoes
    )

    print("230 previsoes verificadas.")

    print("\n===== SALVANDO METADADOS =====")

    manifesto = {
        "aula": 14,
        "projeto": "Heart Disease",
        "modo": "local",
        "bucket_simulado": "aws-alura-ds22-local",
        "prefixo": "predictions",
        "modelo": "LogisticRegression",
        "parametros": {
            "max_iter": 1000,
            "random_state": 42
        },
        "treinamento": len(train_X),
        "teste": len(test_X),
        "features": train_X.columns.tolist(),
        "metricas": metricas,
        "matriz_confusao": matriz.tolist(),
        "falsos_negativos": int(fn),
        "falsos_positivos": int(fp),
        "verdadeiros_negativos": int(tn),
        "verdadeiros_positivos": int(tp),
        "sklearn_version": sklearn.__version__,
        "modelo_sha256": hash_arquivo(modelo_path),
        "preprocessador_aula12": str(preprocessador_path),
        "preprocessador_sha256": hash_arquivo(
            preprocessador_path
        ),
        "modelo_inclui_preprocessamento": False,
        "recarregamento_validado": True,
        "recursos_aws_criados": 0,
        "uso_clinico_autorizado": False
    }

    manifesto_path = (
        PREDICTIONS / "modelo_manifesto.json"
    )

    manifesto_path.write_text(
        json.dumps(
            manifesto,
            indent=4,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )

    relatorio_path = (
        RESULTADOS / "aula_14_persistencia.json"
    )

    relatorio_path.write_text(
        json.dumps(
            manifesto,
            indent=4,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )

    print("\n===== VALIDACAO FINAL =====")

    assert arquivo_csv.is_file()
    assert modelo_path.is_file()
    assert manifesto_path.is_file()
    assert relatorio_path.is_file()

    assert len(previsoes_recarregadas) == 230

    print("TESTES: 7/7 APROVADOS")
    print("PREVISOES:", arquivo_csv)
    print("MODELO:", modelo_path)
    print("MANIFESTO:", manifesto_path)
    print("RELATORIO:", relatorio_path)
    print("CUSTO AWS: ZERO")
    print("AULA 14 - MODELO E PREVISOES SALVOS")


if __name__ == "__main__":
    main()
