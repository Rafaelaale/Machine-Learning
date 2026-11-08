"""Aula 18: avalia modelo registrado com threshold explicito."""

import argparse
import json
from pathlib import Path

import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd

from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

from src.aula04_primeira_run_mlflow import RAIZ
from src.aula17_prepare_data import (
    ALVO,
    FEATURES,
    EXPERIMENTO,
)


def avaliar(
    model_uri,
    data_dir,
    threshold=0.5,
    pipeline_id="manual",
):
    if not np.isfinite(threshold) or not 0 <= threshold <= 1:
        raise ValueError("Threshold deve estar entre 0 e 1.")

    pasta = Path(data_dir)
    if not pasta.is_absolute():
        pasta = RAIZ / pasta
    pasta = pasta.resolve()

    manifest = json.loads(
        (pasta / "manifest.json").read_text(encoding="utf-8")
    )

    if manifest["pipeline_id"] != pipeline_id:
        raise ValueError("pipeline_id nao corresponde ao dataset.")

    df = pd.read_csv(pasta / "test.csv")
    X_test = df[FEATURES]
    y_test = df[ALVO]

    model = mlflow.sklearn.load_model(model_uri)
    y_proba = model.predict_proba(X_test)[:, 1]
    y_pred = (y_proba >= threshold).astype(int)

    cm = confusion_matrix(y_test, y_pred, labels=[0, 1])
    tn, fp, fn, tp = (int(x) for x in cm.ravel())

    metricas = {
        "roc_auc_teste": float(roc_auc_score(y_test, y_proba)),
        "accuracy_teste": float(accuracy_score(y_test, y_pred)),
        "precision_inadimplente": float(
            precision_score(y_test, y_pred, zero_division=0)
        ),
        "recall_inadimplente": float(
            recall_score(y_test, y_pred, zero_division=0)
        ),
        "f1_inadimplente": float(
            f1_score(y_test, y_pred, zero_division=0)
        ),
    }

    report_dict = classification_report(
        y_test,
        y_pred,
        labels=[0, 1],
        target_names=["adimplente", "inadimplente"],
        output_dict=True,
        zero_division=0,
    )

    report_text = classification_report(
        y_test,
        y_pred,
        labels=[0, 1],
        target_names=["adimplente", "inadimplente"],
        zero_division=0,
    )

    destino = RAIZ / "resultados" / "aula18_pipeline" / pipeline_id
    destino.mkdir(parents=True, exist_ok=True)

    arquivo_txt = destino / "classification_report.txt"
    arquivo_json = destino / "classification_report.json"
    arquivo_cm = destino / "confusion_matrix.json"
    arquivo_resumo = destino / "evaluation.json"

    arquivo_txt.write_text(report_text, encoding="utf-8")
    arquivo_json.write_text(
        json.dumps(report_dict, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    arquivo_cm.write_text(
        json.dumps(
            {
                "tn": tn, "fp": fp,
                "fn": fn, "tp": tp,
                "matrix": cm.tolist(),
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    mlflow.set_experiment(EXPERIMENTO)

    with mlflow.start_run() as run:
        mlflow.log_params({
            "step": "evaluate",
            "model_uri": model_uri,
            "pipeline_id": pipeline_id,
            "threshold": threshold,
            "eval_data_dir_resolved": str(pasta),
        })

        mlflow.log_metrics(metricas)
        mlflow.log_metrics({
            "true_negative": tn,
            "false_positive": fp,
            "false_negative": fn,
            "true_positive": tp,
        })

        mlflow.set_tags({
            "project": "risco_credito",
            "course_lesson": "aula_18",
            "pipeline_step": "evaluate",
            "pipeline_id": pipeline_id,
        })

        for arquivo in (arquivo_txt, arquivo_json, arquivo_cm):
            mlflow.log_artifact(
                str(arquivo),
                artifact_path="evaluation",
            )

        run_id = run.info.run_id

    resultado = {
        "pipeline_id": pipeline_id,
        "run_id": run_id,
        "model_uri": model_uri,
        "threshold": threshold,
        "n_test": len(df),
        "metrics": metricas,
        "confusion_matrix": {
            "tn": tn,
            "fp": fp,
            "fn": fn,
            "tp": tp,
        },
    }

    arquivo_resumo.write_text(
        json.dumps(resultado, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print("EVALUATE CONCLUIDO")
    print("PIPELINE:", pipeline_id)
    print("MODEL_URI:", model_uri)
    print("THRESHOLD:", threshold)
    print("RUN_ID:", run_id)

    for nome, valor in metricas.items():
        print(nome.upper(), f"{valor:.4f}")

    print("MATRIZ DE CONFUSAO:", cm.tolist())
    return resultado


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-uri", required=True)
    parser.add_argument("--data-dir", required=True)
    parser.add_argument("--threshold", type=float, default=0.5)
    parser.add_argument("--pipeline-id", default="manual")
    args = parser.parse_args()

    avaliar(
        model_uri=args.model_uri,
        data_dir=args.data_dir,
        threshold=args.threshold,
        pipeline_id=args.pipeline_id,
    )


if __name__ == "__main__":
    main()
