"""MLflow Project - train: treinamento e registro isolado."""

import argparse
import json
from pathlib import Path

import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd

from mlflow.models import infer_signature
from mlflow.tracking import MlflowClient

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from src.aula04_primeira_run_mlflow import RAIZ
from src.aula17_prepare_data import FEATURES, ALVO, EXPERIMENTO


NUMERICAS = [
    "idade",
    "renda_mensal",
    "tempo_emprego_anos",
    "score_interno",
    "valor_solicitado",
    "num_parcelas",
]

CATEGORICAS = [
    "tipo_renda",
    "possui_restricao",
]


def make_preprocess():
    numerico = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ])

    categorico = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore")),
    ])

    return ColumnTransformer([
        ("num", numerico, NUMERICAS),
        ("cat", categorico, CATEGORICAS),
    ])


def build_estimator(model_name, random_state):
    if model_name == "logistic_regression":
        return LogisticRegression(
            max_iter=2000,
            class_weight="balanced",
            random_state=random_state,
        )

    if model_name == "random_forest":
        return RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_leaf=3,
            class_weight="balanced",
            random_state=random_state,
            n_jobs=1,
        )

    raise ValueError(f"Modelo nao suportado: {model_name}")


def treinar(
    model_name="random_forest",
    data_dir="data/processed/manual",
    random_state=42,
    registered_model_name="risco_credito_project_model",
    pipeline_id="manual",
):
    caminho = Path(data_dir)

    if not caminho.is_absolute():
        caminho = RAIZ / caminho

    caminho = caminho.resolve()

    manifest_path = caminho / "manifest.json"

    if not manifest_path.is_file():
        raise FileNotFoundError(
            f"Manifest nao encontrado: {manifest_path}"
        )

    manifest = json.loads(
        manifest_path.read_text(encoding="utf-8")
    )

    if manifest["pipeline_id"] != pipeline_id:
        raise ValueError("pipeline_id nao corresponde aos dados.")

    train_file = caminho / "train.csv"
    test_file = caminho / "test.csv"

    treino = pd.read_csv(train_file)
    teste = pd.read_csv(test_file)

    X_train = treino[FEATURES]
    y_train = treino[ALVO]
    X_test = teste[FEATURES]
    y_test = teste[ALVO]

    estimator = build_estimator(
        model_name,
        random_state,
    )

    modelo = Pipeline([
        ("prep", make_preprocess()),
        ("model", estimator),
    ])

    # Protege os modelos das aulas anteriores.
    proibidos = {
        "risco_credito_classifier",
        "risco_credito_classifier_pyfunc",
    }

    if registered_model_name in proibidos:
        raise ValueError(
            "Nome reservado por um modelo anterior."
        )

    mlflow.set_experiment(EXPERIMENTO)

    with mlflow.start_run() as run:
        mlflow.log_params({
            "step": "train",
            "model_name": model_name,
            "pipeline_id": pipeline_id,
            "random_state": random_state,
            "train_data_dir_resolved": str(caminho),
        })

        modelo.fit(X_train, y_train)

        pred = modelo.predict(X_test)
        proba = modelo.predict_proba(X_test)[:, 1]

        metricas = {
            "roc_auc_teste": float(roc_auc_score(y_test, proba)),
            "accuracy_teste": float(accuracy_score(y_test, pred)),
            "precision_inadimplente": float(
                precision_score(y_test, pred, zero_division=0)
            ),
            "recall_inadimplente": float(
                recall_score(y_test, pred, zero_division=0)
            ),
            "f1_inadimplente": float(
                f1_score(y_test, pred, zero_division=0)
            ),
        }

        mlflow.log_metrics(metricas)

        mlflow.set_tags({
            "project": "risco_credito",
            "course_lesson": "aula_17",
            "pipeline_step": "train",
            "pipeline_id": pipeline_id,
        })

        signature = infer_signature(
            X_test.head(5),
            modelo.predict(X_test.head(5)),
        )

        model_info = mlflow.sklearn.log_model(
            sk_model=modelo,
            name="project_model",
            registered_model_name=registered_model_name,
            signature=signature,
            input_example=X_train.head(5),
            serialization_format="cloudpickle",
        )

        run_id = run.info.run_id

    client = MlflowClient()

    versoes = client.search_model_versions(
        f"name='{registered_model_name}'"
    )

    correspondentes = [
        item for item in versoes
        if item.run_id == run_id
    ]

    if not correspondentes:
        raise RuntimeError(
            "Versao registrada nao encontrada para este run."
        )

    versao = max(
        correspondentes,
        key=lambda item: int(item.version),
    )

    resultado = {
        "pipeline_id": pipeline_id,
        "model_name": model_name,
        "registered_model_name": registered_model_name,
        "registered_version": str(versao.version),
        "run_id": run_id,
        "model_uri": model_info.model_uri,
        "registered_model_uri": (
            f"models:/{registered_model_name}/{versao.version}"
        ),
        "data_dir": str(caminho),
        "metrics": metricas,
    }

    if pipeline_id.startswith("aula18_"):
        relatorio = (
            RAIZ / "resultados" / "aula18_pipeline"
            / pipeline_id / "train.json"
        )
        relatorio.parent.mkdir(parents=True, exist_ok=True)
    else:
        relatorio = RAIZ / "resultados" / "aula17_train.json"

    relatorio.write_text(
        json.dumps(resultado, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print("TRAIN CONCLUIDO")
    print("MODELO:", model_name)
    print("REGISTRY:", registered_model_name)
    print("VERSAO:", versao.version)
    print("RUN_ID:", run_id)
    print("MODEL_URI:", model_info.model_uri)

    for nome, valor in metricas.items():
        print(nome.upper(), f"{valor:.4f}")

    return resultado


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model-name",
        default="random_forest",
    )
    parser.add_argument(
        "--data-dir",
        default="data/processed/manual",
    )
    parser.add_argument(
        "--random-state",
        type=int,
        default=42,
    )
    parser.add_argument(
        "--registered-model-name",
        default="risco_credito_project_model",
    )
    parser.add_argument(
        "--pipeline-id",
        default="manual",
    )

    args = parser.parse_args()

    treinar(
        model_name=args.model_name,
        data_dir=args.data_dir,
        random_state=args.random_state,
        registered_model_name=args.registered_model_name,
        pipeline_id=args.pipeline_id,
    )


if __name__ == "__main__":
    main()
