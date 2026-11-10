import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import yaml

raiz = Path(sys.argv[1])
repo = raiz / "docker-automation"
app = repo / "burguer-app"
workflow = repo / ".github" / "workflows" / "test-microservices.yml"
python = sys.executable

servicos = (
    "auth-service",
    "order-service",
    "product-service",
    "user-service",
)

relatorio = raiz / "aulas" / (
    "resultado-ci-local-"
    + datetime.now().strftime("%Y%m%d-%H%M%S")
    + ".txt"
)

linhas = [
    "VALIDACAO LOCAL - NAO EXECUTADO NO GITHUB ACTIONS",
    "Data: " + datetime.now().isoformat(timespec="seconds"),
]
resultados = []

print("===== VALIDANDO YAML =====", flush=True)

try:
    dados = yaml.load(
        workflow.read_text(encoding="utf-8-sig"),
        Loader=yaml.BaseLoader,
    )

    job = dados["jobs"]["test-microservices"]
    matriz = job["strategy"]["matrix"]["service"]

    if set(matriz) != set(servicos) or len(matriz) != len(servicos):
        raise ValueError("Matriz de microservicos incorreta.")

    if "mongodb" not in job.get("services", {}):
        raise ValueError("MongoDB ausente do workflow.")

    print("YAML: OK", flush=True)
    linhas.append("YAML: OK")

except Exception as erro:
    print("YAML: FALHA -", erro, flush=True)
    linhas.append("YAML: FALHA - " + str(erro))
    relatorio.parent.mkdir(parents=True, exist_ok=True)
    relatorio.write_text("\n".join(linhas), encoding="utf-8")
    sys.exit(1)

ambiente = os.environ.copy()
ambiente["MONGO_URI"] = (
    "mongodb://127.0.0.1:27019/?directConnection=true"
)
ambiente["SECRET_KEY"] = "chave-local-apenas-testes"
ambiente["JWT_SECRET"] = "jwt-local-apenas-testes"
ambiente["PYTHONDONTWRITEBYTECODE"] = "1"
ambiente["COVERAGE_FILE"] = str(
    raiz / "aulas" / ".coverage-ci-local"
)

for servico in servicos:
    pasta = app / servico

    print("\n===== " + servico.upper() + " =====", flush=True)

    if not pasta.is_dir():
        print("PASTA AUSENTE", flush=True)
        linhas.append(servico + ": pasta ausente")
        resultados.append(False)
        continue

    tarefas = [
        (
            "PYTEST E COBERTURA",
            [
                python, "-m", "pytest", "-q",
                "-o", "addopts=",
                "-p", "no:cacheprovider",
                "--cov=models",
                "--cov=services",
                "--cov=config",
                "--cov=controllers",
                "--cov-report=term-missing",
            ],
        ),
        (
            "RADON",
            [python, "-m", "radon", "cc", "models", "-s"],
        ),
    ]

    sucesso = True

    for nome, comando in tarefas:
        try:
            processo = subprocess.run(
                comando,
                cwd=pasta,
                env=ambiente,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=90,
            )

            saida = (
                (processo.stdout or "")
                + "\n"
                + (processo.stderr or "")
            ).strip()

            aprovado = processo.returncode == 0

            print(
                nome + ": " + ("OK" if aprovado else "FALHA"),
                flush=True,
            )

            print(
                saida[-1800:] if aprovado else saida[-4000:],
                flush=True,
            )

            linhas.extend([
                "",
                servico + " - " + nome,
                "Codigo de saida: " + str(processo.returncode),
                saida,
            ])

            if not aprovado:
                sucesso = False

        except subprocess.TimeoutExpired:
            print(nome + ": TIMEOUT DE 90 SEGUNDOS", flush=True)
            linhas.append(servico + " - " + nome + ": TIMEOUT")
            sucesso = False

    resultados.append(sucesso)

relatorio.parent.mkdir(parents=True, exist_ok=True)
relatorio.write_text(
    "\n".join(linhas) + "\n",
    encoding="utf-8",
)

print("\n===== RESULTADO FINAL =====", flush=True)
print(
    str(sum(resultados)) + "/4 servicos sem falhas locais.",
    flush=True,
)
print("RELATORIO:", relatorio, flush=True)

sys.exit(
    0 if len(resultados) == 4 and all(resultados) else 1
)