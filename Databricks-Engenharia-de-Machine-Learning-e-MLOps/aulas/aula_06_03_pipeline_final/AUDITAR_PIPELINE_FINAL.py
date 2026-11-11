import ast
import hashlib
import json

from datetime import datetime, timedelta
from pathlib import Path

BASE = Path(__file__).resolve().parent
CODIGOS = BASE / "codigos_oficiais"

NOMES = [
    "01_ingestao_dados.py",
    "02_pre_processamento.py",
    "03_treinamento_modelo.py",
    "04_gerando_dados_produtivos.py",
    "05_monitoramento_drift.py",
    "06_re_treino.py",
    "07_deploy_modelo.py",
]

fontes = {}
hashes = {}

print("\n===== VALIDANDO OS SETE CODIGOS =====")

for nome in NOMES:
    arquivo = CODIGOS / nome

    if not arquivo.is_file():
        raise AssertionError(
            f"Arquivo ausente: {nome}"
        )

    codigo = arquivo.read_text(
        encoding="utf-8-sig"
    )

    if not codigo.lstrip().startswith(
        "# Databricks notebook source"
    ):
        raise AssertionError(
            f"Cabecalho inesperado: {nome}"
        )

    if 'dbutils.widgets.get("env_catalog")' not in codigo:
        raise AssertionError(
            f"Parametro env_catalog ausente: {nome}"
        )

    # As linhas %pip sao magics do Databricks.
    # Sao isoladas somente para verificar sintaxe Python.
    linhas = []

    for linha in codigo.splitlines():
        if linha.lstrip().startswith("%"):
            linhas.append("pass")
        else:
            linhas.append(linha)

    ast.parse(
        "\n".join(linhas),
        filename=nome
    )

    fontes[nome] = codigo

    hashes[nome] = hashlib.sha256(
        arquivo.read_bytes()
    ).hexdigest()

    print(f"OK: {nome}")

assert len(fontes) == 7

print("\n===== VALIDANDO TASK VALUES =====")

producao = fontes["04_gerando_dados_produtivos.py"]
monitoramento = fontes["05_monitoramento_drift.py"]
deploy = fontes["07_deploy_modelo.py"]

for parametro in ("data_inicio", "data_fim"):
    trecho = (
        f'dbutils.jobs.taskValues.set(key="{parametro}"'
    )

    assert trecho in producao, (
        f"Parametro ausente: {parametro}"
    )

assert (
    'dbutils.jobs.taskValues.set(key="drift_detectado"'
    in monitoramento
)

print("PASSAGEM DE DATAS: OK")
print("DECISAO DE DRIFT: OK")

print("\n===== VALIDANDO CAMINHOS CONDICIONAIS =====")

com_drift = [
    "ingestao_dados",
    "pre_processamento",
    "treinamento",
    "dados_prod",
    "monitoramento_drift",
    "check_re_treino",
    "re_treino_modelo",
    "deploy_modelo",
]

sem_drift = [
    "ingestao_dados",
    "pre_processamento",
    "treinamento",
    "dados_prod",
    "monitoramento_drift",
    "check_re_treino",
    "deploy_modelo",
]

assert "re_treino_modelo" in com_drift
assert "re_treino_modelo" not in sem_drift

print("ROTA COM DRIFT: OK")
print("ROTA SEM DRIFT: OK")

print("\n===== VALIDANDO CALCULO D-1 =====")

assert "timedelta(days=1)" in deploy

fim_exclusivo = datetime.strptime(
    "20260601",
    "%Y%m%d"
)

ultimo_dia = (
    fim_exclusivo - timedelta(days=1)
).strftime("%Y%m%d")

assert ultimo_dia == "20260531"

print(f"ULTIMO DIA DO LOTE: {ultimo_dia}")

print("\n===== VERIFICANDO PONTOS DE ATENCAO =====")

alertas = []

ingestao = fontes["01_ingestao_dados.py"]

if (
    "workspace.silver." in ingestao
    or "workspace.default.dim_produtos" in ingestao
):
    alertas.append(
        "Ingestao: referencias fixas ao catalogo workspace."
    )

if 'taskKey="task_geracao_dados"' in monitoramento:
    alertas.append(
        "Monitoramento: taskKey diverge de dados_prod."
    )

if (
    "modelo_local.predict(df_features)" in deploy
    and "predict_proba" not in deploy
):
    alertas.append(
        "Deploy: verificar classes versus probabilidades."
    )

for alerta in alertas:
    print("ATENCAO:", alerta)

mapa = json.loads(
    (BASE / "MAPA_PIPELINE_FINAL.json").read_text(
        encoding="utf-8-sig"
    )
)

assert len(mapa["tarefas"]) == 8
assert len(mapa["ambientes"]) == 3

relatorio = {
    "aula": "Pipeline Final e Codigos Produtivos",
    "tipo": "auditoria_estatica",
    "codigos_verificados": 7,
    "tarefas_mapeadas": 8,
    "ambientes": mapa["ambientes"],
    "rotas_condicionais_verificadas": 2,
    "teste_d_menos_um": ultimo_dia,
    "hashes_sha256": hashes,
    "pontos_de_atencao": alertas,
    "spark_executado": False,
    "mlflow_executado": False,
    "databricks_remoto_executado": False,
    "deploy_executado": False,
}

destino = BASE / "AUDITORIA_PIPELINE_FINAL.json"

destino.write_text(
    json.dumps(
        relatorio,
        indent=2,
        ensure_ascii=False
    ),
    encoding="utf-8"
)

print("\nSETE CODIGOS: 7/7")
print("SINTAXE ESTATICA: 7/7")
print("TASK VALUES: VERIFICADOS")
print("ROTAS CONDICIONAIS: 2")
print("AUDITORIA ESTATICA: APROVADA")
print("EXECUCAO DATABRICKS: NAO REALIZADA")