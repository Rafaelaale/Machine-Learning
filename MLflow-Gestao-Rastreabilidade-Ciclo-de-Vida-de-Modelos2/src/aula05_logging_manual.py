"""Aula 05: logging manual de parametros e metricas.

Cria uma nova run no experimento da Aula 04.
Preserva o baseline e utiliza o mesmo dataset.

Nesta etapa nao registra artefatos nem tags
personalizadas.
"""

import json
from pathlib import Path

import mlflow
import numpy as np

from mlflow.tracking import MlflowClient

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

from src.aula04_primeira_run_mlflow import (
    RAIZ,
    RANDOM_STATE,
    TARGET,
    FEATURES,
    EXPERIMENTO,
    configurar_tracking,
    carregar_dados,
    construir_pipeline,
)


RUN_NAME = "aula03_lr_manual_v1"

RELATORIO = (
    RAIZ
    / "resultados"
    / "aula05_logging_manual.json"
)


def obter_run_existente():
    """Consulta uma run concluida anteriormente."""

    if not RELATORIO.is_file():
        return None

    registro = json.loads(
        RELATORIO.read_text(encoding="utf-8")
    )

    configurar_tracking()

    client = MlflowClient()
    run = client.get_run(registro["run_id"])

    experimento = client.get_experiment(
        run.info.experiment_id
    )

    assert run.info.status == "FINISHED"
    assert experimento.name == EXPERIMENTO
    assert run.data.tags["mlflow.runName"] == RUN_NAME

    assert len(run.data.params) == 18
    assert len(run.data.metrics) == 11

    print("\nRUN ANTERIOR VALIDADA")
    print("RUN ID:", run.info.run_id)
    print("NENHUMA NOVA RUN CRIADA")

    return registro


def preparar_parametros(df, X_train, X_test):
    """Documenta as configuracoes da execucao."""

    return {
        "modelo": "LogisticRegression",
        "max_iter": 2000,
        "class_weight": "balanced",
        "pipeline": "preprocesamento_sklearn",
        "numeric_imputer": "median",
        "numeric_scaler": "StandardScaler",
        "categorical_imputer": "most_frequent",
        "categorical_encoder": "OneHotEncoder",
        "handle_unknown": "ignore",
        "test_size": 0.25,
        "random_state": RANDOM_STATE,
        "cv_folds": 5,
        "cv_scoring": "roc_auc",
        "n_amostras": len(df),
        "n_features": len(FEATURES),
        "n_train": len(X_train),
        "n_test": len(X_test),
        "target": TARGET,
    }


def preparar_metricas(
    y_test,
    y_pred,
    y_proba,
    scores,
):
    """Calcula metricas e componentes da matriz."""

    cm = confusion_matrix(
        y_test,
        y_pred,
        labels=[0, 1],
    )

    tn, fp, fn, tp = cm.ravel()

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
                y_test,
                y_pred,
                zero_division=0,
            )
        ),
        "recall_inadimplente": float(
            recall_score(
                y_test,
                y_pred,
                zero_division=0,
            )
        ),
        "f1_inadimplente": float(
            f1_score(
                y_test,
                y_pred,
                zero_division=0,
            )
        ),
        "tn": int(tn),
        "fp": int(fp),
        "fn": int(fn),
        "tp": int(tp),
    }


def executar():
    """Treina e registra a run manual."""

    configurar_tracking()

    anterior = obter_run_existente()

    if anterior is not None:
        return anterior

    if mlflow.active_run() is not None:
        raise RuntimeError(
            "Existe uma run MLflow ativa. "
            "Encerre-a antes de iniciar esta aula."
        )

    (
        df,
        X_train,
        X_test,
        y_train,
        y_test,
    ) = carregar_dados()

    model_pipe = construir_pipeline()

    params = preparar_parametros(
        df,
        X_train,
        X_test,
    )

    print("\n===== INICIANDO LOGGING MANUAL =====")
    print("EXPERIMENTO:", EXPERIMENTO)
    print("RUN:", RUN_NAME)

    with mlflow.start_run(
        run_name=RUN_NAME
    ) as run:

        model_pipe.fit(X_train, y_train)

        y_proba = model_pipe.predict_proba(
            X_test
        )[:, 1]

        y_pred = model_pipe.predict(
            X_test
        )

        cv = StratifiedKFold(
            n_splits=5,
            shuffle=True,
            random_state=RANDOM_STATE,
        )

        scores = cross_val_score(
            construir_pipeline(),
            X_train,
            y_train,
            cv=cv,
            scoring="roc_auc",
            n_jobs=1,
        )

        metrics = preparar_metricas(
            y_test,
            y_pred,
            y_proba,
            scores,
        )

        mlflow.log_params(params)
        mlflow.log_metrics(metrics)

        run_id = run.info.run_id
        experiment_id = run.info.experiment_id

    relatorio = {
        "aula_local": 5,
        "aula_codigo_alura": 3,
        "experimento": EXPERIMENTO,
        "run_name": RUN_NAME,
        "run_id": run_id,
        "experiment_id": experiment_id,
        "params": params,
        "metrics": metrics,
        "modelo": "LogisticRegression",
        "logging": "manual",
        "artefatos_registrados": False,
        "tags_personalizadas": False,
    }

    RELATORIO.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    RELATORIO.write_text(
        json.dumps(
            relatorio,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print("\n===== RESULTADOS =====")
    print("RUN ID:", run_id)
    print("PARAMETROS:", len(params))
    print("METRICAS:", len(metrics))

    print("\nROC-AUC TESTE:")
    print(f"{metrics['roc_auc_teste']:.4f}")

    print("\nROC-AUC VALIDACAO CRUZADA:")
    print(
        f"{metrics['roc_auc_cv_media']:.4f}"
        f" +/- {metrics['roc_auc_cv_desvio']:.4f}"
    )

    print("\nMATRIZ DE CONFUSAO:")
    for nome in ("tn", "fp", "fn", "tp"):
        print(
            nome.upper(),
            metrics[nome],
        )

    print("\nCLASSIFICACAO:")
    for nome in (
        "accuracy_teste",
        "precision_inadimplente",
        "recall_inadimplente",
        "f1_inadimplente",
    ):
        print(
            nome,
            f"{metrics[nome]:.4f}",
        )

    print("\nLOGGING MANUAL: OK")

    return relatorio


if __name__ == "__main__":
    executar()
