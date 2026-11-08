"""Aula 18: pipeline MLflow prepare -> train -> evaluate."""

import argparse
import json
import uuid
from pathlib import Path

import mlflow
from mlflow.tracking import MlflowClient

from src.aula04_primeira_run_mlflow import RAIZ
from src.aula17_prepare_data import EXPERIMENTO


PASTA = RAIZ / "resultados" / "aula18_pipeline"
NOME_PADRAO = "risco_credito_project_model"


def encontrar_versao(client, nome, run_id):
    versoes = client.search_model_versions(
        f"name='{nome}'"
    )
    candidatas = [
        v for v in versoes
        if v.run_id == run_id
    ]
    if not candidatas:
        raise RuntimeError(
            "Modelo registrado nao encontrado para o run "
            f"{run_id}."
        )
    return max(candidatas, key=lambda v: int(v.version))


def executar(
    model_name="random_forest",
    n_samples=6000,
    test_size=0.25,
    random_state=42,
    threshold=0.5,
    registered_model_name=NOME_PADRAO,
):
    if model_name not in ("random_forest", "logistic_regression"):
        raise ValueError("Modelo nao suportado.")

    if n_samples < 100:
        raise ValueError("n_samples deve ser >= 100.")

    if not 0.05 <= test_size <= 0.5:
        raise ValueError("test_size invalido.")

    if not 0 <= threshold <= 1:
        raise ValueError("threshold invalido.")

    pipeline_id = "aula18_" + uuid.uuid4().hex[:12]
    data_dir = f"data/processed/{pipeline_id}"
    destino = PASTA / pipeline_id
    destino.mkdir(parents=True, exist_ok=False)

    mlflow.set_experiment(EXPERIMENTO)
    client = MlflowClient()

    parametros = {
        "pipeline_id": pipeline_id,
        "model_name": model_name,
        "n_samples": n_samples,
        "test_size": test_size,
        "random_state": random_state,
        "threshold": threshold,
        "registered_model_name": registered_model_name,
    }

    with mlflow.start_run(
        run_name=f"pipeline_{pipeline_id}"
    ) as parent:
        parent_id = parent.info.run_id

        mlflow.log_params(parametros)
        mlflow.set_tags({
            "project": "risco_credito",
            "course_lesson": "aula_18",
            "pipeline_step": "pipeline",
            "pipeline_id": pipeline_id,
        })

        print("PIPELINE_ID:", pipeline_id, flush=True)
        print("PARENT_RUN_ID:", parent_id, flush=True)

        def executar_etapa(entry_point, params):
            submitted = mlflow.run(
                uri=str(RAIZ),
                entry_point=entry_point,
                parameters=params,
                experiment_name=EXPERIMENTO,
                env_manager="local",
                synchronous=True,
            )

            project_run_id = submitted.run_id
            project_run = client.get_run(project_run_id)

            if project_run.info.status != "FINISHED":
                raise RuntimeError(
                    f"MLflow Project {entry_point} falhou: "
                    f"{project_run.info.status}"
                )

            arquivos = {
                "prepare": destino / "prepare.json",
                "train": destino / "train.json",
                "evaluate": destino / "evaluation.json",
            }

            arquivo_etapa = arquivos[entry_point]

            if not arquivo_etapa.is_file():
                raise RuntimeError(
                    f"Resultado da etapa ausente: {arquivo_etapa}"
                )

            dados_etapa = json.loads(
                arquivo_etapa.read_text(encoding="utf-8")
            )

            run_id = dados_etapa["run_id"]
            run = client.get_run(run_id)

            if run.info.status != "FINISHED":
                raise RuntimeError(
                    f"Run efetivo {entry_point} falhou: "
                    f"{run.info.status}"
                )

            if dados_etapa["pipeline_id"] != pipeline_id:
                raise RuntimeError(
                    "Run pertence a outro pipeline."
                )

            client.set_tag(
                run_id, "mlflow.parentRunId", parent_id
            )
            client.set_tag(
                run_id, "pipeline_id", pipeline_id
            )
            client.set_tag(
                run_id, "pipeline_step", entry_point
            )
            client.set_tag(
                run_id, "mlflow_project_run_id", project_run_id
            )

            print(
                "ETAPA VALIDADA:",
                entry_point,
                "PROJECT_RUN:",
                project_run_id,
                "MODEL_STEP_RUN:",
                run_id,
                flush=True,
            )

            return run_id

        prepare_run_id = executar_etapa(
            "prepare",
            {
                "n_samples": n_samples,
                "test_size": test_size,
                "random_state": random_state,
                "output_dir": "data/processed",
                "pipeline_id": pipeline_id,
            },
        )

        train_run_id = executar_etapa(
            "train",
            {
                "model_name": model_name,
                "data_dir": data_dir,
                "random_state": random_state,
                "registered_model_name": registered_model_name,
                "pipeline_id": pipeline_id,
            },
        )

        versao = encontrar_versao(
            client,
            registered_model_name,
            train_run_id,
        )

        model_uri = (
            f"models:/{registered_model_name}/{versao.version}"
        )

        evaluate_run_id = executar_etapa(
            "evaluate",
            {
                "model_uri": model_uri,
                "data_dir": data_dir,
                "threshold": threshold,
                "pipeline_id": pipeline_id,
            },
        )

        arquivo_eval = destino / "evaluation.json"

        if not arquivo_eval.is_file():
            raise RuntimeError(
                "Relatorio da avaliacao ausente."
            )

        avaliacao = json.loads(
            arquivo_eval.read_text(encoding="utf-8")
        )

        mlflow.log_metrics(
            {
                "pipeline_" + k: v
                for k, v in avaliacao["metrics"].items()
            }
        )

        mlflow.log_params({
            "trained_model_uri": model_uri,
            "registered_version": str(versao.version),
        })

        resumo = {
            "pipeline_id": pipeline_id,
            "parent_run_id": parent_id,
            "prepare_run_id": prepare_run_id,
            "train_run_id": train_run_id,
            "evaluate_run_id": evaluate_run_id,
            "model_name": model_name,
            "registered_model_name": registered_model_name,
            "registered_version": str(versao.version),
            "model_uri": model_uri,
            "data_dir": data_dir,
            "parameters": parametros,
            "metrics": avaliacao["metrics"],
            "confusion_matrix": avaliacao["confusion_matrix"],
            "status": "FINISHED",
        }

        arquivo_resumo = destino / "pipeline_summary.json"

        arquivo_resumo.write_text(
            json.dumps(resumo, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        mlflow.log_artifact(
            str(arquivo_resumo),
            artifact_path="pipeline",
        )

        mlflow.log_artifact(
            str(arquivo_eval),
            artifact_path="pipeline",
        )

        PASTA.mkdir(parents=True, exist_ok=True)

        (PASTA / "ultimo_pipeline_id.txt").write_text(
            pipeline_id,
            encoding="utf-8",
        )

        (RAIZ / "resultados" / "aula18_pipeline.json").write_text(
            json.dumps(resumo, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    print("\n===== PIPELINE REPRODUZIVEL CONCLUIDO =====")
    print("PIPELINE_ID:", pipeline_id)
    print("PARENT_RUN:", parent_id)
    print("PREPARE_RUN:", prepare_run_id)
    print("TRAIN_RUN:", train_run_id)
    print("EVALUATE_RUN:", evaluate_run_id)
    print("MODEL_URI:", model_uri)
    print("VERSAO:", versao.version)

    return resumo


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-name", default="random_forest")
    parser.add_argument("--n-samples", type=int, default=6000)
    parser.add_argument("--test-size", type=float, default=0.25)
    parser.add_argument("--random-state", type=int, default=42)
    parser.add_argument("--threshold", type=float, default=0.5)
    parser.add_argument(
        "--registered-model-name",
        default=NOME_PADRAO,
    )
    args = parser.parse_args()

    executar(
        model_name=args.model_name,
        n_samples=args.n_samples,
        test_size=args.test_size,
        random_state=args.random_state,
        threshold=args.threshold,
        registered_model_name=args.registered_model_name,
    )


if __name__ == "__main__":
    main()
