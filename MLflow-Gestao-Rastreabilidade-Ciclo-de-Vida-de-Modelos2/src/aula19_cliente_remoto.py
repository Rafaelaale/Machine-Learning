"""Aula 19: cliente HTTP conectado a um Tracking Server MLflow."""

import argparse
import json
from pathlib import Path

import mlflow
from mlflow.tracking import MlflowClient

from src.aula04_primeira_run_mlflow import RAIZ


EXPERIMENTO = "aula19_tracking_remoto"
URI_PADRAO = "http://127.0.0.1:5050"

BASE = RAIZ / "aula19_servidor_remoto"
RELATORIO = RAIZ / "resultados" / "aula19_servidor_remoto.json"


def executar(uri=URI_PADRAO):
    if not uri.startswith("http://127.0.0.1:"):
        raise ValueError(
            "Laboratorio restrito ao servidor local 127.0.0.1."
        )

    BASE.mkdir(parents=True, exist_ok=True)
    (BASE / "downloads").mkdir(parents=True, exist_ok=True)

    mlflow.set_tracking_uri(uri)
    mlflow.set_registry_uri(uri)
    mlflow.set_experiment(EXPERIMENTO)

    evidencia = BASE / "evidencia.txt"
    evidencia.write_text(
        "Aula 19: arquivo enviado ao servidor via HTTP.\n",
        encoding="utf-8",
    )

    with mlflow.start_run(run_name="cliente_http_aula19") as run:
        mlflow.log_params({
            "tipo_cliente": "python",
            "comunicacao": "http",
            "backend": "sqlite_isolado",
            "artifact_store": "local_proxy",
            "aula": "19",
        })

        mlflow.log_metrics({
            "roc_auc_exemplo": 0.8288,
            "accuracy_exemplo": 0.7627,
        })

        mlflow.set_tags({
            "project": "risco_credito",
            "course_lesson": "aula_19",
            "arquitetura": "cliente_servidor",
        })

        mlflow.log_artifact(str(evidencia))

        run_id = run.info.run_id
        experiment_id = run.info.experiment_id

    cliente = MlflowClient(tracking_uri=uri)
    registrado = cliente.get_run(run_id)

    caminho = cliente.download_artifacts(
        run_id,
        "evidencia.txt",
        str(BASE / "downloads"),
    )

    baixado = Path(caminho)

    if baixado.read_bytes() != evidencia.read_bytes():
        raise RuntimeError(
            "Artefato recebido nao corresponde ao enviado."
        )

    if registrado.info.status != "FINISHED":
        raise RuntimeError("Run remoto nao finalizado.")

    if registrado.data.params["comunicacao"] != "http":
        raise RuntimeError("Parametro remoto nao encontrado.")

    if abs(
        registrado.data.metrics["roc_auc_exemplo"] - 0.8288
    ) > 1e-9:
        raise RuntimeError("Metrica remota incorreta.")

    resultado = {
        "status": "FINISHED",
        "tracking_uri": uri,
        "experiment_name": EXPERIMENTO,
        "experiment_id": experiment_id,
        "run_id": run_id,
        "backend_store": str(BASE / "tracking.db"),
        "artifact_store": str(BASE / "artifacts"),
        "artifact_local": str(evidencia),
        "artifact_downloaded": str(baixado),
        "artifact_verified": True,
        "parameters": dict(registrado.data.params),
        "metrics": dict(registrado.data.metrics),
    }

    RELATORIO.parent.mkdir(parents=True, exist_ok=True)
    RELATORIO.write_text(
        json.dumps(resultado, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print("\n===== CLIENTE HTTP VALIDADO =====")
    print("TRACKING_URI:", uri)
    print("EXPERIMENTO:", EXPERIMENTO)
    print("RUN_ID:", run_id)
    print("STATUS:", resultado["status"])
    print("METRICAS:", resultado["metrics"])
    print("ARTEFATO ENVIADO E BAIXADO: OK")
    print("RELATORIO:", RELATORIO)

    return resultado


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--tracking-uri",
        default=URI_PADRAO,
    )
    args = parser.parse_args()
    executar(args.tracking_uri)


if __name__ == "__main__":
    main()
