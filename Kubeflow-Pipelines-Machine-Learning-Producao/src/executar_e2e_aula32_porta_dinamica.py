import sys
from pathlib import Path
from datetime import datetime
import kfp

porta = int(sys.argv[1])
url = f"http://127.0.0.1:{porta}"

registro = Path("anotacoes/aula32-run-id.txt")

if registro.exists() and registro.read_text(encoding="utf-8").strip():
    raise RuntimeError("RUN_ID ja registrado. Submissao cancelada.")

client = kfp.Client(host=url)

client.list_experiments(page_size=1)

print("CONEXAO KFP VALIDADA!", flush=True)
print(f"ENDPOINT: {url}", flush=True)

pipeline = Path("trainer/pipeline-e2e-aula32.yaml")

if not pipeline.is_file():
    raise FileNotFoundError(pipeline)

nome = "fraude-e2e-" + datetime.now().strftime("%Y%m%d-%H%M%S")

print("SUBMETENDO PIPELINE...", flush=True)

run = client.create_run_from_pipeline_package(
    pipeline_file=str(pipeline),
    run_name=nome,
    experiment_name="fraude pipeline",
    namespace="kubeflow",
    service_account="pipeline-runner",
    arguments={
        "eta": 0.2430296138044891,
        "max_depth": 5,
        "n_estimators": 194,
        "threshold": 0.70
    },
    enable_caching=False
)

if not run.run_id:
    raise RuntimeError("KFP nao retornou RUN_ID.")

registro.write_text(str(run.run_id), encoding="utf-8")

print("PIPELINE SUBMETIDA!", flush=True)
print(f"RUN_ID: {run.run_id}", flush=True)
print("STATUS: aguardando execucao no KFP", flush=True)
