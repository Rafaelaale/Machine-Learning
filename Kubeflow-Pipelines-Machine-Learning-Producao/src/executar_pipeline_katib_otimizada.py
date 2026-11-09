import json
import socket
import subprocess
import time
from datetime import datetime
from pathlib import Path

import kfp
import yaml


ROOT = Path.cwd()
PIPELINE = ROOT / "pipelines" / "pipeline_unica.yaml"
NOTAS = ROOT / "anotacoes"
NOTAS.mkdir(exist_ok=True)

REGISTRO = NOTAS / "aula22_execucao_katib_otimizada.json"
RESULTADO = NOTAS / "aula22_resultado_pipeline_otimizada.json"

PARAMETROS = {
    "csv_path": "/data/creditcard.csv",
    "eta": 0.2430296138044891,
    "max_depth": 5,
    "n_estimators": 194,
}

documentos = list(
    yaml.safe_load_all(
        PIPELINE.read_text(encoding="utf-8-sig")
    )
)

tarefas = {}

for documento in documentos:
    if isinstance(documento, dict):
        tarefas = documento.get("root", {}).get("dag", {}).get("tasks", {})
        if tarefas:
            break

if len(tarefas) != 3:
    raise RuntimeError(
        f"Pipeline incorreta: esperadas 3 etapas, encontradas {len(tarefas)}."
    )

print("PIPELINE UNICA VALIDADA")
print("ETAPAS:", ", ".join(tarefas))
print("PARAMETROS:", PARAMETROS)

with socket.socket() as sock:
    sock.bind(("127.0.0.1", 0))
    porta = sock.getsockname()[1]

host = f"http://127.0.0.1:{porta}"

stdout_log = (NOTAS / "aula22_portforward_stdout.log").open("ab")
stderr_log = (NOTAS / "aula22_portforward_stderr.log").open("ab")

comando = [
    "kubectl",
    "--context=kubeflow",
    "-n", "kubeflow",
    "port-forward",
    "--address=127.0.0.1",
    "svc/ml-pipeline",
    f"{porta}:8888",
]

processo = None

try:
    processo = subprocess.Popen(
        comando,
        stdout=stdout_log,
        stderr=stderr_log,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )

    conectado = False

    for _ in range(60):
        if processo.poll() is not None:
            raise RuntimeError("Port-forward do KFP foi encerrado.")

        try:
            with socket.create_connection(
                ("127.0.0.1", porta),
                timeout=1,
            ):
                conectado = True
                break
        except OSError:
            time.sleep(0.5)

    if not conectado:
        raise RuntimeError("API KFP indisponivel.")

    client = kfp.Client(host=host)

    if REGISTRO.exists():
        registro = json.loads(
            REGISTRO.read_text(encoding="utf-8-sig")
        )

        if registro["parametros"] != PARAMETROS:
            raise RuntimeError("Registro anterior possui parametros diferentes.")

        run_id = registro["run_id"]
        print("RETOMANDO RUN EXISTENTE:", run_id)

    else:
        resposta = client.create_run_from_pipeline_package(
            pipeline_file=str(PIPELINE),
            arguments=PARAMETROS,
            experiment_name="fraude-pipeline-katib-otimizada",
            enable_caching=True,
        )

        run_id = resposta.run_id

        registro = {
            "run_id": run_id,
            "parametros": PARAMETROS,
            "pipeline": "pipelines/pipeline_unica.yaml",
            "criado_em": datetime.now().isoformat(),
        }

        with REGISTRO.open("x", encoding="utf-8") as f:
            json.dump(registro, f, indent=2, ensure_ascii=False)

        print("PIPELINE ENVIADA")
        print("RUN ID:", run_id)

    print("ACOMPANHANDO A EXECUCAO...")

    prazo = time.monotonic() + 1200
    estado_anterior = None

    while True:
        execucao = client.get_run(run_id)

        estado = str(execucao.state).upper()

        if estado != estado_anterior:
            print("ESTADO:", estado, flush=True)
            estado_anterior = estado

        if estado in (
            "SUCCEEDED", "SUCCESS",
            "FAILED", "ERROR",
            "CANCELED", "CANCELLED",
        ):
            break

        if time.monotonic() >= prazo:
            print("EXECUCAO AINDA EM ANDAMENTO")
            print("RUN PRESERVADO:", run_id)
            raise SystemExit(2)

        time.sleep(15)

    detalhes = execucao.to_dict()

    RESULTADO.write_text(
        json.dumps(
            {
                "run_id": run_id,
                "estado": estado,
                "parametros": PARAMETROS,
                "consultado_em": datetime.now().isoformat(),
                "resposta_kfp": detalhes,
            },
            indent=2,
            ensure_ascii=False,
            default=str,
        ),
        encoding="utf-8",
    )

    info = detalhes.get("run_details") or {}
    etapas = info.get("task_details") or []

    if etapas:
        print("\nETAPAS:")
        for etapa in etapas:
            nome = etapa.get("display_name") or etapa.get("task_name")
            status = etapa.get("state", "sem estado")
            print(f"{nome}: {status}")

            cache = etapa.get("cached")
            if cache is not None:
                print("  CACHE:", cache)
    else:
        print("Detalhes individuais nao fornecidos pela API.")

    print("\nRELATORIO:", RESULTADO)

    if estado != "SUCCEEDED":
        raise RuntimeError(
            f"Treinamento nao concluido com sucesso: {estado}"
        )

    print("\n===== TREINAMENTO OTIMIZADO CONCLUIDO =====")
    print("RUN ID:", run_id)
    print("ETA:", PARAMETROS["eta"])
    print("MAX DEPTH:", PARAMETROS["max_depth"])
    print("N ESTIMATORS:", PARAMETROS["n_estimators"])
    print("STATUS: SUCCEEDED")

finally:
    if processo is not None and processo.poll() is None:
        processo.terminate()
        try:
            processo.wait(timeout=5)
        except subprocess.TimeoutExpired:
            processo.kill()

    stdout_log.close()
    stderr_log.close()