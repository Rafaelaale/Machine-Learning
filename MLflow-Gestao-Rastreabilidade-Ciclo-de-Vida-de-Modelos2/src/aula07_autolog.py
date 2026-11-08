"""Aula 07 - Autolog e comparacao de modelos no MLflow."""

import json
from pathlib import Path

import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd

from mlflow.tracking import MlflowClient

from sklearn.base import clone
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import (
    StratifiedKFold,
    cross_val_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import (
    OneHotEncoder,
    StandardScaler,
)
from sklearn.tree import DecisionTreeClassifier

from src.aula04_primeira_run_mlflow import (
    RAIZ,
    RANDOM_STATE,
    carregar_dados,
    configurar_tracking,
)
from src.aula03_ambiente_dataset import NUM_COLS, CAT_COLS


EXPERIMENT_NAME = "risco_credito_comparacao_modelos"
CV_FOLDS = 3

RESULTADOS = RAIZ / "resultados"

ARQUIVO_CSV = (
    RESULTADOS / "aula07_comparacao_autolog.csv"
)

ARQUIVO_JSON = (
    RESULTADOS / "aula07_comparacao_autolog.json"
)

METRICAS_PADRONIZADAS = (
    "roc_auc_teste",
    "roc_auc_cv_media",
    "roc_auc_cv_desvio",
    "accuracy_teste",
    "precision_inadimplente",
    "recall_inadimplente",
    "f1_inadimplente",
    "tn",
    "fp",
    "fn",
    "tp",
)


def make_preprocess():
    """Cria pre-processador novo para cada modelo."""

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

    return ColumnTransformer(
        transformers=[
            ("num", numeric_pipe, NUM_COLS),
            ("cat", categorical_pipe, CAT_COLS),
        ]
    )


def make_candidates():
    """Tres algoritmos com configuracoes da Alura."""

    return {
        "logistic_regression": LogisticRegression(
            max_iter=2000,
            class_weight="balanced",
            random_state=RANDOM_STATE,
        ),
        "decision_tree": DecisionTreeClassifier(
            max_depth=5,
            min_samples_leaf=50,
            class_weight="balanced",
            random_state=RANDOM_STATE,
        ),
        "random_forest": RandomForestClassifier(
            n_estimators=100,
            max_depth=8,
            min_samples_leaf=20,
            class_weight="balanced",
            n_jobs=-1,
            random_state=RANDOM_STATE,
        ),
    }


def make_pipeline(estimator):
    """Retorna um pipeline ainda nao ajustado."""

    return Pipeline(
        steps=[
            ("prep", make_preprocess()),
            ("model", clone(estimator)),
        ]
    )


def calcular_metricas(y_test, y_pred, y_proba, scores):
    """Metricas padronizadas para comparar candidatos."""

    tn, fp, fn, tp = confusion_matrix(
        y_test,
        y_pred,
        labels=[0, 1],
    ).ravel()

    return {
        "roc_auc_teste": float(
            roc_auc_score(y_test, y_proba)
        ),
        "roc_auc_cv_media": float(scores.mean()),
        "roc_auc_cv_desvio": float(scores.std()),
        "accuracy_teste": float(
            accuracy_score(y_test, y_pred)
        ),
        "precision_inadimplente": float(
            precision_score(
                y_test, y_pred, zero_division=0
            )
        ),
        "recall_inadimplente": float(
            recall_score(
                y_test, y_pred, zero_division=0
            )
        ),
        "f1_inadimplente": float(
            f1_score(
                y_test, y_pred, zero_division=0
            )
        ),
        "tn": int(tn),
        "fp": int(fp),
        "fn": int(fn),
        "tp": int(tp),
    }


def configurar_experimento():
    """Mantem o banco SQLite do projeto anterior."""

    tracking_uri = configurar_tracking()

    mlflow.set_experiment(EXPERIMENT_NAME)

    client = MlflowClient()

    experiment = client.get_experiment_by_name(
        EXPERIMENT_NAME
    )

    if experiment is None:
        raise RuntimeError(
            "Experimento de comparacao nao criado."
        )

    return client, experiment, tracking_uri


def buscar_run_concluida(client, experiment_id, nome):
    """Evita duplicar runs ja concluidas e verificadas."""

    runs = client.search_runs(
        experiment_ids=[experiment_id],
        max_results=1000,
    )

    for run in runs:
        if (
            run.info.status == "FINISHED"
            and run.data.tags.get("mlflow.runName") == nome
            and run.data.tags.get("tracking_type") == "hybrid_autolog"
            and all(
                chave in run.data.metrics
                for chave in METRICAS_PADRONIZADAS
            )
        ):
            return run

    return None


def linha_comparacao(model_name, run):
    """Converte uma run real em linha comparavel."""

    resultado = {
        "modelo": model_name,
        "run_name": run.data.tags.get(
            "mlflow.runName", ""
        ),
        "run_id": run.info.run_id,
        "status": run.info.status,
        "parametros_automaticos_e_manuais": len(
            run.data.params
        ),
    }

    for chave in METRICAS_PADRONIZADAS:
        resultado[chave] = float(
            run.data.metrics[chave]
        )

    return resultado


def executar():
    """Treina tres modelos com autolog e registro manual."""

    client, experiment, tracking_uri = (
        configurar_experimento()
    )

    if mlflow.active_run() is not None:
        raise RuntimeError(
            "Existe uma run ativa. "
            "Encerre-a antes de executar a Aula 07."
        )

    (
        df,
        X_train,
        X_test,
        y_train,
        y_test,
    ) = carregar_dados()

    resultados = []

    print("\n===== AULA 07 - AUTOLOG =====")
    print("EXPERIMENTO:", EXPERIMENT_NAME)
    print("TRACKING:", tracking_uri)
    print("TRAIN:", len(X_train))
    print("TEST:", len(X_test))
    print("CV FOLDS:", CV_FOLDS)

    try:
        for model_name, estimator in make_candidates().items():

            run_name = f"aula04_autolog_{model_name}"

            anterior = buscar_run_concluida(
                client,
                experiment.experiment_id,
                run_name,
            )

            if anterior is not None:
                print(
                    "\nRUN PRESERVADA:",
                    run_name,
                    anterior.info.run_id,
                )

                resultados.append(
                    linha_comparacao(model_name, anterior)
                )
                continue

            print("\nTREINANDO:", model_name)

            pipe = make_pipeline(estimator)

            # Fora da run e com autolog desativado.
            # Cada fold usa clones independentes.
            mlflow.sklearn.autolog(disable=True)

            cv = StratifiedKFold(
                n_splits=CV_FOLDS,
                shuffle=True,
                random_state=RANDOM_STATE,
            )

            scores = cross_val_score(
                pipe,
                X_train,
                y_train,
                cv=cv,
                scoring="roc_auc",
                n_jobs=1,
            )

            # Criamos uma unica run para o ajuste final.
            with mlflow.start_run(
                experiment_id=experiment.experiment_id,
                run_name=run_name,
            ) as run:

                try:
                    mlflow.sklearn.autolog(
                        disable=False,
                        exclusive=False,
                        log_models=True,
                        log_datasets=False,
                        log_post_training_metrics=False,
                        silent=False,
                    )

                    pipe.fit(X_train, y_train)

                    # Desliga antes das previsoes e metricas
                    # calculadas explicitamente.
                    mlflow.sklearn.autolog(disable=True)

                    y_pred = pipe.predict(X_test)

                    y_proba = pipe.predict_proba(
                        X_test
                    )[:, 1]

                    metricas = calcular_metricas(
                        y_test,
                        y_pred,
                        y_proba,
                        scores,
                    )

                    mlflow.log_params({
                        "candidate_name": model_name,
                        "cv_folds": CV_FOLDS,
                        "cv_scoring": "roc_auc",
                        "dataset_version": "synthetic_credit_v1",
                    })

                    mlflow.log_metrics(metricas)

                    mlflow.set_tags({
                        "project": "risco_credito",
                        "task": "binary_classification",
                        "dataset_version": "synthetic_credit_v1",
                        "tracking_type": "hybrid_autolog",
                        "course_lesson": "aula_04",
                        "candidate": model_name,
                    })

                    run_id = run.info.run_id

                finally:
                    # Nao deixa autolog ativo depois da run.
                    mlflow.sklearn.autolog(disable=True)

            registrada = client.get_run(run_id)

            if registrada.info.status != "FINISHED":
                raise RuntimeError(
                    f"Run nao concluida: {model_name}"
                )

            if not all(
                chave in registrada.data.metrics
                for chave in METRICAS_PADRONIZADAS
            ):
                raise RuntimeError(
                    f"Metricas incompletas: {model_name}"
                )

            resultados.append(
                linha_comparacao(
                    model_name,
                    registrada,
                )
            )

            print("RUN ID:", run_id)
            print(
                "ROC-AUC TESTE:",
                f"{metricas['roc_auc_teste']:.4f}",
            )
            print(
                "ROC-AUC CV:",
                f"{metricas['roc_auc_cv_media']:.4f}",
            )
            print(
                "PARAMETROS REGISTRADOS:",
                len(registrada.data.params),
            )

    finally:
        mlflow.sklearn.autolog(disable=True)

    tabela = (
        pd.DataFrame(resultados)
        .sort_values(
            "roc_auc_teste",
            ascending=False,
        )
        .reset_index(drop=True)
    )

    if len(tabela) != 3:
        raise RuntimeError(
            "Comparacao incompleta: esperadas 3 runs."
        )

    RESULTADOS.mkdir(
        parents=True,
        exist_ok=True,
    )

    tabela.to_csv(
        ARQUIVO_CSV,
        index=False,
        encoding="utf-8-sig",
    )

    resumo = {
        "aula_local": 7,
        "experimento": EXPERIMENT_NAME,
        "experiment_id": experiment.experiment_id,
        "tracking_uri": tracking_uri,
        "cv_folds": CV_FOLDS,
        "n_total": len(df),
        "n_train": len(X_train),
        "n_test": len(X_test),
        "total_runs": len(resultados),
        "ranking": tabela.to_dict(orient="records"),
        "melhor_roc_auc_teste": str(
            tabela.iloc[0]["modelo"]
        ),
        "campeao_definitivo_selecionado": False,
    }

    ARQUIVO_JSON.write_text(
        json.dumps(
            resumo,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print("\n===== COMPARACAO DOS MODELOS =====")

    colunas = [
        "modelo",
        "roc_auc_teste",
        "roc_auc_cv_media",
        "roc_auc_cv_desvio",
        "precision_inadimplente",
        "recall_inadimplente",
        "f1_inadimplente",
    ]

    print(
        tabela[colunas].round(4).to_string(
            index=False
        )
    )

    print("\nRANKING INICIAL POR ROC-AUC:")
    print(resumo["melhor_roc_auc_teste"])
    print("RUNS COMPARADAS:", len(resultados))
    print("ARQUIVO CSV:", ARQUIVO_CSV)
    print("ARQUIVO JSON:", ARQUIVO_JSON)
    print("AUTOLOG FINAL: DESATIVADO")

    return resumo


if __name__ == "__main__":
    executar()
