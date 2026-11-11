import argparse
import ast
import json
import sqlite3

from pathlib import Path

BASE = Path(__file__).resolve().parent
REPO = BASE.parents[1]

BRANCHES = {
    ("develop", "stage"),
    ("stage", "main")
}

AMBIENTES = {
    "dev": "dev",
    "stage": "stage",
    "prod": "prod"
}


def validar():
    try:
        import yaml
    except ImportError as erro:
        raise SystemExit(
            "PyYAML ausente no ambiente Python."
        ) from erro

    bundle = yaml.safe_load(
        (BASE / "databricks.yml").read_text(
            encoding="utf-8-sig"
        )
    )

    recursos = yaml.safe_load(
        (BASE / "resources/jobs.yml").read_text(
            encoding="utf-8-sig"
        )
    )

    nome_workflow = (
        BASE / "WORKFLOW_EM_USO.txt"
    ).read_text(encoding="utf-8-sig").strip()

    caminho_workflow = (
        REPO / ".github/workflows" / nome_workflow
    )

    workflow_texto = caminho_workflow.read_text(
        encoding="utf-8-sig"
    )

    workflow = yaml.safe_load(workflow_texto)

    assert bundle["bundle"]["name"] == "alura_pipeline_mlops_iac"
    assert bundle["include"] == ["resources/*.yml"]

    alvos = [
        (nome, config["variables"]["env_catalog"])
        for nome, config in bundle["targets"].items()
    ]

    assert alvos == list(AMBIENTES.items()), alvos

    job = recursos["resources"]["jobs"]["job_teste_catalog"]
    tarefas = job["tasks"]

    assert len(tarefas) == 1
    assert tarefas[0]["task_key"] == "criar_usuarios_bronze"

    notebook_path = tarefas[0]["notebook_task"]["notebook_path"]

    assert notebook_path == "../notebooks/ingestao_databricks.py"

    assert tarefas[0]["notebook_task"]["base_parameters"]["env_catalog"] == (
        "${var.env_catalog}"
    )

    notebook = BASE / "notebooks/ingestao_databricks.py"

    assert notebook.is_file()

    ast.parse(notebook.read_text(encoding="utf-8-sig"))

    # PyYAML pode interpretar "on" como True.
    assert "on" in workflow or True in workflow

    assert set(workflow["jobs"]) == {
        "simular-dev",
        "simular-stage",
        "validar-pr",
        "simular-prod"
    }

    assert "databricks bundle deploy" not in workflow_texto

    testes = [
        ("develop", "stage", True),
        ("stage", "main", True),
        ("develop", "main", False),
        ("feature/nova", "main", False),
        ("main", "stage", False)
    ]

    for origem, destino, esperado in testes:
        assert ((origem, destino) in BRANCHES) is esperado

    print("BUNDLE: YAML valido")
    print("WORKFLOW: quatro Jobs, sem deploy remoto")
    print("NOTEBOOK: sintaxe Python validada")
    print("BRANCHES: regras de promocao aprovadas")


def simular(ambiente):
    if ambiente not in AMBIENTES:
        raise ValueError("Ambiente invalido")

    pasta = BASE / "resultados"
    pasta.mkdir(parents=True, exist_ok=True)

    banco = pasta / "catalogos_simulados.sqlite"
    tabela = f"{ambiente}_default_usuarios_bronze"

    linhas = [
        (1, "1", "usuario1@exemplo.invalid", "cliente"),
        (2, "2", "usuario2@exemplo.invalid", "admin")
    ]

    with sqlite3.connect(banco) as conexao:
        conexao.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {tabela} (
                id INTEGER PRIMARY KEY,
                nome TEXT NOT NULL,
                email TEXT NOT NULL,
                perfil TEXT NOT NULL
            )
            """
        )

        conexao.executemany(
            f"INSERT OR REPLACE INTO {tabela} VALUES (?, ?, ?, ?)",
            linhas
        )

        encontrados = conexao.execute(
            f"SELECT * FROM {tabela} ORDER BY id"
        ).fetchall()

        assert len(encontrados) == 2
        assert encontrados == linhas

    print(
        f"AMBIENTE {ambiente.upper()}: "
        f"{len(encontrados)} registros em {tabela}"
    )

    return {
        "ambiente": ambiente,
        "tabela": tabela,
        "registros": len(encontrados)
    }


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--validar", action="store_true")
    parser.add_argument("--todos", action="store_true")
    parser.add_argument(
        "--ambiente",
        choices=list(AMBIENTES)
    )
    parser.add_argument("--origem")
    parser.add_argument("--destino")

    args = parser.parse_args()

    validar()

    if args.origem or args.destino:
        permitido = (
            args.origem, args.destino
        ) in BRANCHES

        print(
            "PROMOCAO:",
            f"{args.origem} -> {args.destino}",
            "PERMITIDA" if permitido else "BLOQUEADA"
        )

        if not permitido:
            raise SystemExit(2)

    resultados = []

    if args.todos:
        for ambiente in AMBIENTES:
            resultados.append(simular(ambiente))

    elif args.ambiente:
        resultados.append(simular(args.ambiente))

    if resultados:
        relatorio = BASE / "resultados/RELATORIO_EXECUCAO.json"

        relatorio.write_text(
            json.dumps(resultados, indent=2),
            encoding="utf-8"
        )

        print("SIMULACAO LOCAL CONCLUIDA")

    elif args.validar:
        print("VALIDACAO LOCAL CONCLUIDA")


if __name__ == "__main__":
    main()