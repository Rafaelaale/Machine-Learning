import argparse
import socket
import subprocess
import sys
import time

from pathlib import Path

import kfp


ROOT = Path(__file__).resolve().parent.parent
PIPELINE = ROOT / "pipelines" / "pipeline.yaml"


def porta_disponivel():
    try:
        with socket.create_connection(
            ("127.0.0.1", 8080),
            timeout=1,
        ):
            return True
    except OSError:
        return False


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--eta", type=float, default=0.1)
    parser.add_argument("--max-depth", type=int, default=5)
    parser.add_argument("--n-estimators", type=int, default=200)
    parser.add_argument("--csv", default="/data/creditcard.csv")

    args = parser.parse_args()

    if not PIPELINE.exists():
        raise FileNotFoundError(PIPELINE)

    processo = None

    try:
        if not porta_disponivel():
            comando = [
                "kubectl",
                "--context=kubeflow",
                "-n",
                "kubeflow",
                "port-forward",
                "--address=127.0.0.1",
                "svc/ml-pipeline-ui",
                "8080:80",
            ]

            flags = getattr(
                subprocess,
                "CREATE_NO_WINDOW",
                0,
            )

            processo = subprocess.Popen(
                comando,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=flags,
            )

            for tentativa in range(30):
                if porta_disponivel():
                    break

                if processo.poll() is not None:
                    raise RuntimeError(
                        "Port-forward encerrou antes da conexao."
                    )

                time.sleep(1)
            else:
                raise RuntimeError(
                    "Nao foi possivel conectar ao KFP."
                )

        client = kfp.Client(
            host="http://127.0.0.1:8080"
        )

        run = client.create_run_from_pipeline_package(
            pipeline_file=str(PIPELINE),
            arguments={
                "csv_path": args.csv,
                "eta": args.eta,
                "max_depth": args.max_depth,
                "n_estimators": args.n_estimators,
            },
            experiment_name="fraude-pipeline",
        )

        print("PIPELINE ENVIADA AO KFP")
        print("RUN ID:", run.run_id)

        registro = ROOT / "anotacoes" / (
            f"aula14_run_{run.run_id}.txt"
        )

        registro.write_text(
            f"Run ID: {run.run_id}\n"
            "Pipeline: fraude-pipeline\n"
            "Segmentos: low, medium, high\n"
            "Status: submetida ao KFP\n"
            "O treinamento pode continuar no cluster.\n",
            encoding="utf-8",
        )

        print("REGISTRO:", registro)

    finally:
        if processo is not None:
            processo.terminate()

            try:
                processo.wait(timeout=5)
            except subprocess.TimeoutExpired:
                processo.kill()


if __name__ == "__main__":
    main()
