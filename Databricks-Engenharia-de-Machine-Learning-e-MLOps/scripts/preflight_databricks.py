from pathlib import Path
import ast
import csv
import json
import re
import sys
from datetime import datetime

source = Path(sys.argv[1]).resolve()
reports = Path(sys.argv[2]).resolve()
reports.mkdir(parents=True, exist_ok=True)

issues = []
summary = {
    "files": 0,
    "notebooks": 0,
    "cells": 0,
    "code_cells": 0,
    "python_scripts": 0,
    "csv_files": 0,
    "data_rows": 0,
}


def issue(level, where, message):
    issues.append({
        "level": level,
        "file": where,
        "message": message,
    })


def rel(p):
    return p.relative_to(source).as_posix()


if not (source / "databricks.yml").is_file():
    raise SystemExit("Repositorio incompleto. Nenhuma tarefa remota foi executada.")

files = [
    p for p in source.rglob("*")
    if p.is_file() and ".git" not in p.parts
]

summary["files"] = len(files)

print("\n===== 1. INVENTARIO COMPLETO =====")

for p in files:

    if p.suffix == ".ipynb":
        try:
            notebook = json.loads(
                p.read_text(encoding="utf-8-sig")
            )

            cells = notebook.get("cells", [])

            summary["notebooks"] += 1
            summary["cells"] += len(cells)
            summary["code_cells"] += sum(
                c.get("cell_type") == "code"
                for c in cells
            )

        except (OSError, ValueError) as exc:
            issue(
                "ERRO", rel(p),
                "Notebook invalido: " + type(exc).__name__
            )

    elif p.suffix == ".csv":
        try:
            with p.open(encoding="utf-8-sig", newline="") as f:

                sample = f.read(8192)
                f.seek(0)

                try:
                    delimiter = csv.Sniffer().sniff(
                        sample, delimiters=",;\t"
                    ).delimiter
                except csv.Error:
                    delimiter = (
                        ";" if sample.count(";") > sample.count(",")
                        else ","
                    )

                reader = csv.reader(f, delimiter=delimiter)
                header = next(reader, [])
                rows = sum(1 for _ in reader)

                summary["csv_files"] += 1
                summary["data_rows"] += rows

                issue(
                    "INFO", rel(p),
                    f"CSV: {rows} linhas, "
                    f"separador {delimiter!r}, "
                    f"{len(header)} colunas"
                )

        except (OSError, UnicodeError, csv.Error) as exc:
            issue(
                "ERRO", rel(p),
                "CSV invalido: " + type(exc).__name__
            )

    elif p.suffix == ".py":
        summary["python_scripts"] += 1

        try:
            lines = p.read_text(
                encoding="utf-8-sig"
            ).splitlines()

            # Ignora comandos especiais do Databricks
            # durante a verificacao estatica de Python.
            code = "\n".join(
                "" if line.lstrip().startswith(("%", "!"))
                else line
                for line in lines
            )

            ast.parse(code, filename=str(p))

        except (SyntaxError, OSError, UnicodeError) as exc:
            issue(
                "REVISAR", rel(p),
                "Sintaxe ou magia Databricks: "
                + type(exc).__name__
            )

print("Inventario concluido.")

print("\n===== 2. VALIDANDO REFERENCIAS DO PIPELINE =====")

bundle = (source / "databricks.yml").read_text(
    encoding="utf-8-sig"
)

paths = re.findall(
    r"notebook_path:\s*['\"]?(\./[^\s'\"]+)",
    bundle
)

for notebook_path in paths:
    target = source / notebook_path[2:]

    if not target.is_file():
        issue(
            "ERRO",
            "databricks.yml",
            "Task aponta para arquivo inexistente: "
            + notebook_path
        )

if "dbc-0b9b6719-6175.cloud.databricks.com" in bundle:
    issue(
        "ATENCAO",
        "databricks.yml",
        "Workspace do instrutor identificado. "
        "Substituir pelo seu antes de qualquer deploy."
    )

workflow = (
    source / ".github" / "workflows" / "deploy.yml"
)

if workflow.is_file():
    issue(
        "ATENCAO",
        rel(workflow),
        "Workflow com deploy automatico. "
        "Manter desativado no projeto de estudo."
    )

print("\n===== 3. CONFERINDO INGESTAO =====")

ingest = (
    source / "aula_6" / "pipeline"
    / "01_ingestao_dados.py"
)

if ingest.is_file():

    text = ingest.read_text(encoding="utf-8-sig")

    if (
        "FROM workspace.silver.tabela_eventos_silver" in text
        or "workspace.default.dim_produtos" in text
    ):
        issue(
            "ATENCAO",
            rel(ingest),
            "A consulta Gold usa tabelas fixas "
            "diferentes das variaveis de ambiente."
        )

    if "/Volumes/workspace/bronze/raw/" in text:
        issue(
            "PREPARAR",
            rel(ingest),
            "Carregar CSVs em um Volume do seu workspace "
            "antes de executar a ingestao."
        )

print("\n===== 4. CONFERINDO MONITORAMENTO DE DRIFT =====")

monitor = (
    source / "aula_6" / "pipeline"
    / "05_monitoramento_drift.py"
)

if monitor.is_file():

    text = monitor.read_text(encoding="utf-8-sig")

    if (
        'taskKey="task_geracao_dados"' in text
        and "task_key: dados_prod" in bundle
    ):
        issue(
            "ATENCAO",
            rel(monitor),
            "taskKey divergente: o codigo usa "
            "task_geracao_dados e o Job usa dados_prod."
        )

print("\n===== 5. CONFERINDO MODELO E INFERENCIA =====")

scoring = (
    source / "aula_6" / "pipeline"
    / "07_deploy_modelo.py"
)

if scoring.is_file():

    text = scoring.read_text(encoding="utf-8-sig")

    if "modelo_local.predict(df_features)" in text:
        issue(
            "REVISAR",
            rel(scoring),
            "Predict de classificador normalmente retorna "
            "classe. Conferir se o resultado desejado "
            "e probabilidade."
        )

issue(
    "INFO",
    "Databricks Free Edition",
    "Antes da execucao confirmar Unity Catalog, "
    "permissoes, serverless, Jobs e MLflow."
)

issue(
    "INFO",
    "Seguranca",
    "Nao foram executados deploys, workflows "
    "ou modificacoes nos arquivos da Alura."
)

print("\n===== 6. GERANDO RELATORIOS =====")

result = {
    "date": datetime.now().isoformat(timespec="seconds"),
    "repository": str(source),
    "summary": summary,
    "findings": issues,
}

json_path = reports / "preflight_databricks.json"
txt_path = reports / "preflight_databricks.txt"

json_path.write_text(
    json.dumps(
        result,
        indent=2,
        ensure_ascii=False
    ),
    encoding="utf-8"
)

lines = [
    "PRE-FLIGHT DATABRICKS FREE EDITION",
    "",
    "RESUMO",
]

lines.extend(
    f"{key}: {value}"
    for key, value in summary.items()
)

lines.append("")
lines.append("ACHADOS E ACOES FUTURAS")

for item in issues:
    lines.append(
        f"[{item['level']}] "
        f"{item['file']}: "
        f"{item['message']}"
    )

lines.extend([
    "",
    "LIMITACOES",
    "Auditoria estatica, sem executar Spark ou Databricks.",
    "Sintaxe YAML e permissões remotas ainda nao testadas.",
    "Arquivos originais da Alura preservados.",
    "Nenhum deploy ou publicacao realizada.",
])

txt_path.write_text(
    "\n".join(lines) + "\n",
    encoding="utf-8"
)

print("\n===== RESULTADO DA ANALISE =====")

for key, value in summary.items():
    print(f"{key}: {value}")

print("\nPONTOS PARA PREPARAR OU CORRIGIR:")

for item in issues:
    print(
        f"[{item['level']}] "
        f"{item['file']}: {item['message']}"
    )

print("\nRELATORIO:", txt_path)
print("NENHUM DEPLOY OU PUBLICACAO EXECUTADO.")
