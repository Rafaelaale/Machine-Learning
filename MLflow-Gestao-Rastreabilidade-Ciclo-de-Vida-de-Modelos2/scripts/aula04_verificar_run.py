"""Verifica a primeira run registrada no MLflow."""

import json

from mlflow.tracking import MlflowClient

from src.aula04_primeira_run_mlflow import (
    RAIZ,
    configurar_tracking,
)


def verificar():
    configurar_tracking()

    arquivo = (
        RAIZ
        / "resultados"
        / "aula04_primeira_run_mlflow.json"
    )

    if not arquivo.is_file():
        raise FileNotFoundError(
            "Relatorio da Aula 04 nao encontrado."
        )

    relatorio = json.loads(
        arquivo.read_text(encoding="utf-8")
    )

    client = MlflowClient()

    run = client.get_run(
        relatorio["run_id"]
    )

    assert run.info.status == "FINISHED"
    assert len(run.data.params) == 9
    assert len(run.data.metrics) == 7

    print("\n===== RUN VALIDADA =====")
    print("EXPERIMENTO:", relatorio["experimento"])
    print("RUN ID:", run.info.run_id)
    print("STATUS:", run.info.status)
    print("PARAMETROS:", len(run.data.params))
    print("METRICAS:", len(run.data.metrics))

    for nome, valor in run.data.metrics.items():
        print(f"{nome}: {valor:.6f}")

    probabilidade = relatorio[
        "simulacao_cliente"
    ]["probabilidade_inadimplencia"]

    print(
        "PROBABILIDADE CLIENTE:",
        f"{probabilidade:.2%}",
    )

    print("VALIDACAO MLFLOW: OK")


if __name__ == "__main__":
    verificar()