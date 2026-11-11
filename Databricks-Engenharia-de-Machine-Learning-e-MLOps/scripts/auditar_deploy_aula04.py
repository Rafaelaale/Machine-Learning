from pathlib import Path
import json
import re
import sys

projeto = Path(__file__).resolve().parents[1]
pasta = (
    projeto
    / "material-alura"
    / "6123-alura-ml-databricks"
    / "aula_4"
)

destino = (
    projeto
    / "relatorios"
    / "auditoria_deploy_aula04.txt"
)

if not pasta.is_dir():
    raise RuntimeError("Pasta aula_4 ausente")

arquivos = sorted(pasta.rglob("*.ipynb"))

if not arquivos:
    raise RuntimeError("Nenhum notebook da Aula 4 encontrado")

linhas = [
    "AUDITORIA AULA 4 - DEPLOY DATABRICKS",
    "",
    f"Notebooks encontrados: {len(arquivos)}",
    "",
]

palavras = {
    "Registro MLflow": r"mlflow|registered_model_name",
    "Model Registry": r"register_model|set_registered_model_alias|ModelVersion",
    "Alias Champion": r"Champion|champion",
    "Deploy Batch": r"spark_udf|batch|predict",
    "Serving Endpoint": r"serving_endpoints|create_endpoint|serving",
    "Gravacao overwrite": r"mode\(['\"]overwrite['\"]\)|CREATE OR REPLACE",
    "Credenciais": r"token|secret|password",
}

erros = []

print("===== NOTEBOOKS DA AULA 4 =====")

for arquivo in arquivos:

    relativo = arquivo.relative_to(projeto)

    try:
        notebook = json.loads(
            arquivo.read_text(encoding="utf-8-sig")
        )

        celulas = notebook.get("cells", [])

        codigo = "\n".join(
            "".join(celula.get("source", []))
            for celula in celulas
            if celula.get("cell_type") == "code"
        )

        codigo_count = sum(
            c.get("cell_type") == "code"
            for c in celulas
        )

        print(f"VALIDADO: {arquivo.name}")
        print(f"  Celulas: {len(celulas)}")
        print(f"  Celulas de codigo: {codigo_count}")

        linhas.extend([
            str(relativo),
            f"Celulas: {len(celulas)}",
            f"Codigo: {codigo_count}",
        ])

        for descricao, padrao in palavras.items():
            if re.search(
                padrao,
                codigo,
                flags=re.IGNORECASE
            ):
                linhas.append(f"REFERENCIA: {descricao}")
                print(f"  Encontrado: {descricao}")

        linhas.append("")

    except (ValueError, KeyError) as erro:
        erros.append(f"{relativo}: {erro}")

linhas.extend([
    "PENDENCIAS PARA EXECUCAO:",
    "- Confirmar treinamento real no Databricks.",
    "- Verificar modelo e versao no Unity Catalog.",
    "- Validar compatibilidade das features.",
    "- Verificar permissao e suporte ao deploy.",
    "- Evitar sobrescrita de dados produtivos.",
    "- Nao ativar endpoint nem alias automaticamente.",
    "",
    "Esta auditoria e estatica.",
    "Referencias encontradas nao comprovam execucao.",
    "Nenhum deploy foi realizado.",
])

if erros:
    linhas.extend(["", "ERROS:"] + erros)

destino.write_text(
    "\n".join(linhas) + "\n",
    encoding="utf-8"
)

print("\n===== RESULTADO DA AUDITORIA =====")
print("NOTEBOOKS:", len(arquivos))
print("ERROS:", len(erros))
print("RELATORIO:", destino)

if erros:
    sys.exit(1)