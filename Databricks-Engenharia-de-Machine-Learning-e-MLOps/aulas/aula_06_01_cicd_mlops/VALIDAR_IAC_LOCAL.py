import ast
import json
import re
import sys

from pathlib import Path

raiz = Path(sys.argv[1])
bundle = raiz / "databricks.yml"
jobs = raiz / "resources" / "jobs.yml"
notebooks = raiz / "notebooks"

ordem = [
    "carga_prod",
    "monitoramento_drift",
    "verificar_drift",
    "condicao_drift",
    "re_treino"
]

arquivos = [
    "aula_5_2_job_dados_prod_aprimorado.ipynb",
    "aula_5_2_job_monitoramento_drift_aprimorado.ipynb",
    "verificar_drift_dab.ipynb",
    "aula_5_5_re_treino_dab.ipynb"
]

assert bundle.is_file(), "databricks.yml ausente"
assert jobs.is_file(), "resources/jobs.yml ausente"

print("CONFIGURACAO PRINCIPAL: encontrada")

for nome in arquivos:
    caminho = notebooks / nome

    assert caminho.is_file(), f"Notebook ausente: {nome}"

    nb = json.loads(caminho.read_text(encoding="utf-8-sig"))

    assert nb["nbformat"] == 4

    codigo = "\n".join(
        cell["source"]
        if isinstance(cell["source"], str)
        else "".join(cell["source"])
        for cell in nb["cells"]
        if cell["cell_type"] == "code"
    )

    assert codigo.strip(), f"Notebook sem codigo: {nome}"

    if nome in (
        "verificar_drift_dab.ipynb",
        "aula_5_5_re_treino_dab.ipynb"
    ):
        ast.parse(codigo, filename=nome)

    print("NOTEBOOK OK:", nome)

texto = jobs.read_text(encoding="utf-8-sig")

chaves = re.findall(
    r"^ {8}- task_key:\s*(\S+)\s*$",
    texto,
    flags=re.MULTILINE
)

assert chaves == ordem, (
    f"Sequencia de tarefas incorreta: {chaves}"
)

for nome in arquivos:
    assert f"../notebooks/{nome}" in texto, (
        f"Referencia ausente: {nome}"
    )

assert "op: GREATER_THAN" in texto
assert "outcome: \"true\"" in texto
assert "{{tasks.verificar_drift.values.total_drift}}" in texto

assert "periodo_inicio" in (
    notebooks / "verificar_drift_dab.ipynb"
).read_text(encoding="utf-8-sig")

assert "dia_prtc" in (
    notebooks / "aula_5_5_re_treino_dab.ipynb"
).read_text(encoding="utf-8-sig")

print("SEQUENCIA DAS CINCO TAREFAS: OK")
print("CONDICAO DE RETREINO: OK")
print("CAMINHOS DOS NOTEBOOKS: OK")

try:
    import yaml
except ImportError:
    print(
        "YAML: verificacao estrutural OK; "
        "parser PyYAML indisponivel"
    )
else:
    config = yaml.safe_load(
        bundle.read_text(encoding="utf-8-sig")
    )

    recursos = yaml.safe_load(texto)

    assert config["bundle"]["name"] == "alura_mlops_cicd"

    assert all(
        t in config["targets"]
        for t in ("dev", "staging", "prod")
    )

    job = recursos["resources"]["jobs"][
        "carga_produtiva_monitoramento"
    ]

    tarefas = job["tasks"]

    assert [t["task_key"] for t in tarefas] == ordem

    assert tarefas[1]["depends_on"][0]["task_key"] == "carga_prod"
    assert tarefas[2]["depends_on"][0]["task_key"] == "monitoramento_drift"
    assert tarefas[3]["depends_on"][0]["task_key"] == "verificar_drift"
    assert tarefas[4]["depends_on"][0]["task_key"] == "condicao_drift"

    assert tarefas[4]["depends_on"][0]["outcome"] == "true"

    print("YAML: PARSE FORMAL OK")

print("VALIDACAO LOCAL CONCLUIDA")
print("DEPLOY REMOTO: NAO REALIZADO")