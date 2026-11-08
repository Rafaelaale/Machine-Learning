"""Aula 09 - Organizacao do historico no MLflow.

Padroniza tags das tres runs da Aula 07,
registra hipoteses e cria relatorios.

Nao realiza treinamento nem cria novas runs.
Nao altera parametros ou metricas existentes.
"""

import hashlib
import json
from pathlib import Path

import mlflow
import pandas as pd

from mlflow.tracking import MlflowClient

from src.aula04_primeira_run_mlflow import (
    RAIZ,
    configurar_tracking,
)
from src.aula07_autolog import EXPERIMENT_NAME


RESULTADOS = RAIZ / "resultados"

ARQUIVO_JSON = (
    RESULTADOS / "aula09_organizacao_experimentos.json"
)
ARQUIVO_MD = (
    RESULTADOS / "aula09_checklist_rastreabilidade.md"
)
ARQUIVO_CSV = (
    RESULTADOS / "aula09_historico_organizado.csv"
)
ARQUIVO_FILTRO = (
    RESULTADOS / "aula09_filtro_candidatos.csv"
)

CODE_VERSION = "not_available"

COMMON_TAGS = {
    "project": "risco_credito",
    "task": "binary_classification",
    "target": "inadimplente",
    "dataset_version": "synthetic_credit_v1",
    "feature_set": "core_features_v1",
    "split_strategy": "train_test_stratified_75_25",
    "code_version": CODE_VERSION,
}

HYPOTHESES = {
    "logistic_regression": (
        "Verificar se a regressao logistica "
        "oferece boa ROC-AUC e recall com "
        "maior simplicidade e interpretabilidade."
    ),
    "decision_tree": (
        "Verificar se uma arvore de decisao "
        "atinge desempenho competitivo com "
        "regras mais faceis de inspecionar."
    ),
    "random_forest": (
        "Verificar se um ensemble de arvores "
        "melhora ROC-AUC e recall em relacao "
        "ao baseline, considerando maior "
        "complexidade operacional."
    ),
}

CHECKLIST = {
    "objetivo": "Hipotese documentada na tag hypothesis",
    "dados": "Dataset sintetico synthetic_credit_v1",
    "codigo": "Versao do codigo e hash dos arquivos",
    "features": "Oito atributos definidos na Aula 03",
    "split": "Treino e teste estratificados 75/25",
    "metricas": "ROC-AUC, precision, recall, F1 e matriz",
    "artefatos": "Inspecionar os artefatos de cada run",
    "decisao": "Status candidate; selecao futura",
}

MODELOS = {
    "logistic_regression",
    "decision_tree",
    "random_forest",
}


def calcular_fingerprint():
    """Calcula o hash dos arquivos principais."""

    arquivos = [
        RAIZ / "src" / "aula03_ambiente_dataset.py",
        RAIZ / "src" / "aula04_primeira_run_mlflow.py",
        RAIZ / "src" / "aula07_autolog.py",
    ]

    digest = hashlib.sha256()

    for arquivo in arquivos:
        if not arquivo.is_file():
            raise FileNotFoundError(str(arquivo))

        digest.update(
            arquivo.name.encode("utf-8")
        )
        digest.update(
            arquivo.read_bytes()
        )

    return digest.hexdigest()


def carregar_runs_originais(client):
    """Recupera os tres IDs gravados pela Aula 07."""

    arquivo = (
        RESULTADOS / "aula07_comparacao_autolog.json"
    )

    dados = json.loads(
        arquivo.read_text(encoding="utf-8")
    )

    experimento = client.get_experiment_by_name(
        EXPERIMENT_NAME
    )

    if experimento is None:
        raise RuntimeError(
            "Experimento de comparacao ausente."
        )

    runs = {}

    for item in dados["ranking"]:
        nome = item["modelo"]
        run_id = item["run_id"]

        if nome in runs:
            raise RuntimeError(
                "Modelo duplicado no ranking."
            )

        run = client.get_run(run_id)

        if run.info.status != "FINISHED":
            raise RuntimeError(
                "Run nao concluida: " + nome
            )

        if run.info.experiment_id != experimento.experiment_id:
            raise RuntimeError(
                "Run pertence a outro experimento."
            )

        if run.data.tags.get("candidate") != nome:
            raise RuntimeError(
                "Identificacao de candidato divergente."
            )

        runs[nome] = run

    if set(runs) != MODELOS:
        raise RuntimeError(
            "Historico nao contem os tres modelos."
        )

    return experimento, runs


def criar_tags(nome, fingerprint):
    """Define metadados organizacionais reutilizaveis."""

    return {
        **COMMON_TAGS,
        "code_fingerprint_sha256": fingerprint,
        "hypothesis": HYPOTHESES[nome],
        "selection_status": "candidate",
        "experiment_phase": "model_comparison",
        "organization_lesson": "aula_09",
    }


def organizar_runs(client, runs, fingerprint):
    """Atualiza apenas tags, sem alterar metricas."""

    for nome, run in runs.items():
        tags = criar_tags(nome, fingerprint)

        for chave, valor in tags.items():
            existente = run.data.tags.get(chave)

            # Nao altera uma tag ja preenchida
            # com valor conflitante.
            if existente is not None and existente != valor:
                raise RuntimeError(
                    f"Conflito de tag {chave} na run {nome}: "
                    f"{existente!r} != {valor!r}"
                )

    for nome, run in runs.items():
        tags = criar_tags(nome, fingerprint)

        for chave, valor in tags.items():
            if run.data.tags.get(chave) != valor:
                client.set_tag(
                    run.info.run_id,
                    chave,
                    valor,
                )

        print("TAGS ORGANIZADAS:", nome)


def consultar_organizadas(experiment_id):
    """Usa filtros de tags e recupera metricas."""

    tabela = mlflow.search_runs(
        experiment_ids=[experiment_id],
        filter_string=(
            "tags.project = 'risco_credito' "
            "AND tags.dataset_version = "
            "'synthetic_credit_v1' "
            "AND tags.organization_lesson = 'aula_09' "
            "AND tags.organization_lesson = 'aula_09'"
        ),
        order_by=[
            "metrics.roc_auc_teste DESC"
        ],
    )

    colunas = [
        "run_id",
        "tags.mlflow.runName",
        "tags.candidate",
        "tags.selection_status",
        "tags.code_version",
        "tags.code_fingerprint_sha256",
        "metrics.roc_auc_teste",
        "metrics.precision_inadimplente",
        "metrics.recall_inadimplente",
        "metrics.f1_inadimplente",
    ]

    if tabela.empty:
        raise RuntimeError(
            "Consulta de tags nao encontrou runs."
        )

    faltantes = [
        c for c in colunas if c not in tabela.columns
    ]

    if faltantes:
        raise RuntimeError(
            "Colunas ausentes: " + str(faltantes)
        )

    return tabela[colunas].copy()


def consultar_candidatos(experiment_id):
    """Exemplo de busca por tags e ROC-AUC >= 0.85."""

    return mlflow.search_runs(
        experiment_ids=[experiment_id],
        filter_string=(
            "tags.project = 'risco_credito' "
            "AND tags.dataset_version = "
            "'synthetic_credit_v1' "
            "AND tags.organization_lesson = 'aula_09' "
            "AND metrics.roc_auc_teste >= 0.85"
        ),
        order_by=[
            "metrics.roc_auc_teste DESC"
        ],
    )


def executar():
    """Organiza o historico existente e o documenta."""

    configurar_tracking()

    client = MlflowClient()

    experimento, runs = carregar_runs_originais(
        client
    )

    fingerprint = calcular_fingerprint()

    organizar_runs(
        client,
        runs,
        fingerprint,
    )

    tabela = consultar_organizadas(
        experimento.experiment_id
    )

    if len(tabela) != 3:
        raise RuntimeError(
            "Esperadas exatamente 3 runs organizadas."
        )

    filtro = consultar_candidatos(
        experimento.experiment_id
    )

    ids_originais = {
        run.info.run_id
        for run in runs.values()
    }

    if set(tabela["run_id"]) != ids_originais:
        raise RuntimeError(
            "A consulta recuperou IDs inesperados."
        )

    RESULTADOS.mkdir(
        parents=True,
        exist_ok=True,
    )

    tabela.to_csv(
        ARQUIVO_CSV,
        index=False,
        encoding="utf-8-sig",
    )

    if filtro.empty:
        pd.DataFrame(
            columns=tabela.columns
        ).to_csv(
            ARQUIVO_FILTRO,
            index=False,
            encoding="utf-8-sig",
        )
    else:
        filtro.to_csv(
            ARQUIVO_FILTRO,
            index=False,
            encoding="utf-8-sig",
        )

    relatorio = {
        "aula": 9,
        "experimento": EXPERIMENT_NAME,
        "experiment_id": experimento.experiment_id,
        "code_version": CODE_VERSION,
        "code_fingerprint_sha256": fingerprint,
        "common_tags": COMMON_TAGS,
        "hypotheses": HYPOTHESES,
        "checklist": CHECKLIST,
        "runs_organizadas": len(tabela),
        "runs_ids": sorted(ids_originais),
        "candidatos_roc_085": len(filtro),
        "novos_treinamentos": 0,
        "novas_runs": 0,
        "campeao_definitivo": None,
    }

    ARQUIVO_JSON.write_text(
        json.dumps(
            relatorio,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    linhas = [
        "# Aula 09 - Checklist de rastreabilidade",
        "",
        "## Experimento",
        "",
        EXPERIMENT_NAME,
        "",
        "## Convencoes",
        "",
        "- Experimentos: projeto, fase e objetivo.",
        "- Runs: aula, modelo, objetivo e versao.",
        "- Artefatos: reports, plots, data e selection.",
        "",
        "## Checklist",
        "",
    ]

    for nome, descricao in CHECKLIST.items():
        linhas.append(
            f"- [x] {nome}: {descricao}"
        )

    linhas.extend([
        "",
        "## Versao do codigo",
        "",
        f"- Commit: {CODE_VERSION}",
        f"- SHA-256 dos arquivos: {fingerprint}",
        "",
        "O hash nao e um identificador de commit.",
        "",
        "## Hipoteses dos modelos",
        "",
    ])

    for nome, hipotese in HYPOTHESES.items():
        linhas.append(
            f"- **{nome}**: {hipotese}"
        )

    linhas.extend([
        "",
        "## Resultado",
        "",
        f"- Runs organizadas: {len(tabela)}",
        f"- Candidatos ROC-AUC >= 0.85: {len(filtro)}",
        "- Campeao definitivo: nao selecionado",
        "",
        "## Limitacoes",
        "",
        "As tags documentam o contexto; nao demonstram,",
        "sozinhas, a reproducibilidade integral.",
        "A selecao do campeao pertence a proxima etapa.",
    ])

    ARQUIVO_MD.write_text(
        "\n".join(linhas) + "\n",
        encoding="utf-8",
    )

    print("\n===== AULA 09 - HISTORICO ORGANIZADO =====")
    print("EXPERIMENTO:", EXPERIMENT_NAME)
    print("RUNS ORGANIZADAS:", len(tabela))
    print("TAGS COMUNS:", len(COMMON_TAGS))
    print("HIPOTESES:", len(HYPOTHESES))
    print("CHECKLIST:", len(CHECKLIST))
    print("CODE VERSION:", CODE_VERSION)
    print("SHA-256:", fingerprint)

    print("\n===== CONSULTA POR TAGS =====")

    visiveis = [
        "tags.candidate",
        "tags.selection_status",
        "metrics.roc_auc_teste",
        "metrics.recall_inadimplente",
    ]

    print(
        tabela[visiveis]
        .round(4)
        .to_string(index=False)
    )

    print("\nFILTRO ROC-AUC >= 0.85:", len(filtro))
    print("NOVAS RUNS: 0")
    print("NOVOS TREINAMENTOS: 0")
    print("CAMPEAO DEFINITIVO: NAO SELECIONADO")

    return relatorio


if __name__ == "__main__":
    executar()
