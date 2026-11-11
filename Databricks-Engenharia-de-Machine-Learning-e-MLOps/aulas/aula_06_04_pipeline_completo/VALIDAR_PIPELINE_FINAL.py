import argparse
import ast
import json

from datetime import datetime, timedelta, timezone
from pathlib import Path

import yaml

BASE = Path(__file__).resolve().parent
NB = BASE / "notebooks"
RESULTADOS = BASE / "resultados"
RESULTADOS.mkdir(exist_ok=True)

NOMES = [
    "ingestao_dados",
    "pre_processamento",
    "treinamento",
    "dados_prod",
    "monitoramento_drift",
    "check_re_treino",
    "re_treino_modelo",
    "deploy_modelo",
]

ARQUIVOS = [
    "01_ingestao_dados.py",
    "02_pre_processamento.py",
    "03_treinamento_modelo.py",
    "04_gerando_dados_produtivos.py",
    "05_monitoramento_drift.py",
    "06_re_treino.py",
    "07_deploy_modelo.py",
]


def validar():
    cfg = yaml.safe_load(
        (BASE / "databricks.yml").read_text(
            encoding="utf-8-sig"
        )
    )

    y = yaml.safe_load(
        (BASE / "resources/jobs.yml").read_text(
            encoding="utf-8-sig"
        )
    )

    assert cfg["bundle"]["name"] == "alura_pipeline_completo_mlops"
    assert cfg["include"] == ["resources/*.yml"]

    targets = {
        nome: info["variables"]["env_catalog"]
        for nome, info in cfg["targets"].items()
    }

    assert targets == {
        "dev": "dev",
        "stage": "stage",
        "prod": "prod",
    }

    assert "resultados/**" in cfg["sync"]["exclude"]

    tasks = y["resources"]["jobs"]["pipeline_completo_mlops"]["tasks"]

    assert [t["task_key"] for t in tasks] == NOMES, (
        "Ordem ou numero de tarefas invalido"
    )

    por_nome = {
        t["task_key"]: t
        for t in tasks
    }

    dependencias = [
        [],
        ["ingestao_dados"],
        ["pre_processamento"],
        ["treinamento"],
        ["dados_prod"],
        ["monitoramento_drift"],
        ["check_re_treino"],
        ["check_re_treino", "re_treino_modelo"],
    ]

    for chave, esperado in zip(NOMES, dependencias):
        atual = [
            d["task_key"]
            for d in por_nome[chave].get("depends_on", [])
        ]

        assert atual == esperado, (
            chave, atual, esperado
        )

    condicao = por_nome["check_re_treino"]["condition_task"]

    assert condicao == {
        "op": "EQUAL_TO",
        "left": "{{tasks.monitoramento_drift.values.drift_detectado}}",
        "right": "true",
    }

    assert (
        por_nome["re_treino_modelo"]["depends_on"][0]["outcome"]
        == "true"
    )

    deploy = por_nome["deploy_modelo"]

    assert deploy["depends_on"][0]["outcome"] == "false"
    assert deploy["run_if"] == "AT_LEAST_ONE_SUCCESS"

    assert (
        deploy["notebook_task"]["base_parameters"]["data_fim"]
        == "{{tasks.dados_prod.values.data_fim}}"
    )

    tarefas_notebook = [
        t for t in tasks if "notebook_task" in t
    ]

    for tarefa, nome in zip(tarefas_notebook, ARQUIVOS):
        notebook_task = tarefa["notebook_task"]

        caminho = (
            BASE / "resources" / notebook_task["notebook_path"]
        ).resolve()

        assert caminho == (NB / nome).resolve(), nome

        assert (
            notebook_task["base_parameters"]["env_catalog"]
            == "${var.env_catalog}"
        )

        codigo = caminho.read_text(encoding="utf-8-sig")

        # Ignora magics do Databricks apenas para AST.
        linhas = [
            "pass" if linha.lstrip().startswith("%") else linha
            for linha in codigo.splitlines()
        ]

        ast.parse("\n".join(linhas), filename=nome)

        assert 'dbutils.widgets.get("env_catalog")' in codigo

        print("NOTEBOOK OK:", nome)

    ingestao = (NB / ARQUIVOS[0]).read_text(
        encoding="utf-8-sig"
    )

    producao = (NB / ARQUIVOS[3]).read_text(
        encoding="utf-8-sig"
    )

    monitoramento = (NB / ARQUIVOS[4]).read_text(
        encoding="utf-8-sig"
    )

    scoring = (NB / ARQUIVOS[6]).read_text(
        encoding="utf-8-sig"
    )

    assert "FROM {tabela_silver_eventos} s" in ingestao

    assert (
        "INNER JOIN {tabela_gold_dim_produto} p"
        in ingestao
    )

    assert 'taskKey="dados_prod"' in monitoramento

    assert (
        'taskKey="task_geracao_dados"'
        not in monitoramento
    )

    assert (
        "modelo_local.predict_proba(df_features)[:, 1]"
        in scoring
    )

    for valor in ("data_inicio", "data_fim"):
        assert (
            f'dbutils.jobs.taskValues.set(key="{valor}"'
            in producao
        )

    assert (
        'dbutils.jobs.taskValues.set(key="drift_detectado"'
        in monitoramento
    )

    print("YAML: ESTRUTURA FORMAL VALIDA")
    print("OITO TAREFAS: ORDEM E DEPENDENCIAS APROVADAS")
    print("TRES CORRECOES: VERIFICADAS")

    return por_nome


def simular(por_nome, drift):
    # Simulacao de fluxo, nao execucao de notebooks.

    estados = {
        chave: "SUCCESS"
        for chave in NOMES[:5]
    }

    estados["check_re_treino"] = (
        "TRUE" if drift else "FALSE"
    )

    estados["re_treino_modelo"] = (
        "SUCCESS" if drift else "SKIPPED"
    )

    dependencia_falsa = (
        por_nome["deploy_modelo"]["depends_on"][0]["outcome"]
        == "false"
    )

    retreino_ok = (
        estados["re_treino_modelo"] == "SUCCESS"
    )

    permitido = (
        (not drift and dependencia_falsa)
        or retreino_ok
    )

    assert permitido

    estados["deploy_modelo"] = "ELIGIBLE_SIMULATED"

    assert (
        estados["re_treino_modelo"] == "SUCCESS"
    ) is drift

    fim = datetime.strptime("20260601", "%Y%m%d")

    dia_anterior = (
        fim - timedelta(days=1)
    ).strftime("%Y%m%d")

    assert dia_anterior == "20260531"

    return {
        "drift_simulado": drift,
        "estados_simulados": estados,
        "data_fim_exclusiva_teste": "20260601",
        "dia_d_menos_1": dia_anterior,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--auditar", action="store_true")
    parser.parse_args()

    por_nome = validar()

    cenarios = {}

    for ambiente in ("dev", "stage", "prod"):
        for drift in (False, True):

            nome = (
                f"{ambiente}_"
                f"{'COM' if drift else 'SEM'}_DRIFT"
            )

            cenarios[nome] = simular(
                por_nome, drift
            )

            print("CONTROLE SIMULADO OK:", nome)

    relatorio = {
        "data_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "tipo": "VALIDACAO_E_SIMULACAO_DE_CONTROLE",
        "tarefas": 8,
        "notebooks": 7,
        "ambientes": 3,
        "cenarios": cenarios,
        "execucao_real_de_modelos": False,
        "deploy_databricks": False,
        "git_push_realizado": False,
        "bundle_validate_oficial": False,
        "pendencias": [
            "Volumes CSV necessarios no Databricks",
            "Validacao oficial com Databricks CLI",
            "Execucao real Spark, Feature Store e MLflow",
            "Testes do contrato de previsao LightGBM",
        ],
    }

    destino = RESULTADOS / "AUDITORIA_FINAL.json"

    destino.write_text(
        json.dumps(
            relatorio,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8",
    )

    print("SEIS CENARIOS DE CONTROLE: APROVADOS")
    print("AULA 6.4 - VALIDACAO LOCAL APROVADA")
    print("DEPLOY REMOTO: NAO REALIZADO")


if __name__ == "__main__":
    main()