"""Prepara o modelo MLflow registrado para Docker."""

import json
import shutil
from pathlib import Path

import mlflow
import mlflow.artifacts
from mlflow.tracking import MlflowClient

from src.aula04_primeira_run_mlflow import RAIZ

MODEL_NAME = "risco_credito_classifier_pyfunc"
ALIAS = "servingCandidate"
MODEL_URI = f"models:/{MODEL_NAME}@{ALIAS}"

PASTA = RAIZ / "resultados" / "aula16_docker"
DESTINO = PASTA / "modelo_empacotado"

PASTA.mkdir(parents=True, exist_ok=True)

db = (RAIZ / "mlflow.db").resolve().as_posix()
uri = f"sqlite:///{db}"

mlflow.set_tracking_uri(uri)
mlflow.set_registry_uri(uri)

client = MlflowClient()

version = client.get_model_version_by_alias(
    MODEL_NAME,
    ALIAS,
)

aula14 = json.loads(
    (
        RAIZ / "resultados"
        / "aula14_pyfunc_personalizado.json"
    ).read_text(encoding="utf-8")
)

assert version.run_id == aula14["run_id"], (
    "Run do Registry diferente da Aula 14."
)

assert str(version.version) == str(aula14["version"]), (
    "Versao registrada diferente da Aula 14."
)

print("MODELO:", MODEL_NAME)
print("ALIAS:", ALIAS)
print("VERSAO:", version.version)

if (DESTINO / "MLmodel").is_file():
    print("PACOTE EXISTENTE VALIDADO:", DESTINO)

else:
    caminho = Path(
        mlflow.artifacts.download_artifacts(
            artifact_uri=MODEL_URI,
        )
    ).resolve()

    print("CAMINHO RETORNADO PELO MLFLOW:", caminho)

    if not (caminho / "MLmodel").is_file():
        raise RuntimeError(
            "O caminho retornado nao contem MLmodel: "
            f"{caminho}"
        )

    # Preserva eventuais arquivos parciais anteriores.
    if DESTINO.exists():
        import datetime

        sufixo = datetime.datetime.now().strftime(
            "%Y%m%d_%H%M%S_%f"
        )

        backup = PASTA / (
            "modelo_empacotado_backup_" + sufixo
        )

        DESTINO.rename(backup)

        print("PACOTE PARCIAL PRESERVADO:", backup)

    shutil.copytree(
        caminho,
        DESTINO,
    )

    print("PACOTE COPIADO:", DESTINO)

assert (DESTINO / "MLmodel").is_file()

print("MLMODEL: ENCONTRADO")
print("MODELO PRONTO PARA DOCKER")
