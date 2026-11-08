"""Aula 10: escolha documentada do candidato campeao.

Le as runs existentes, calcula ranking ponderado,
registra a decisao na run vencedora e prepara
a identificacao do modelo para o Model Registry.
Nao treina, nao cria runs e nao registra modelos.
"""

import json

import mlflow
import numpy as np
import pandas as pd
from mlflow.tracking import MlflowClient

from src.aula04_primeira_run_mlflow import (
    RAIZ,
    configurar_tracking,
)
from src.aula07_autolog import EXPERIMENT_NAME

RESULTADOS = RAIZ / "resultados"
PASTA = RESULTADOS / "aula10_selecao"

CSV = PASTA / "decision_ranking.csv"
POLITICA_JSON = PASTA / "selection_policy.json"
RESUMO_MD = PASTA / "champion_summary.md"
PREPARACAO_JSON = PASTA / "preparacao_registry.json"
RESULTADO_JSON = RESULTADOS / "aula10_escolha_campeao.json"

REGISTRY_NAME = "risco_credito_classifier"

POLITICA = {
    "technical_score": {
        "roc_auc_teste": 0.35,
        "recall_inadimplente": 0.25,
        "precision_inadimplente": 0.15,
        "f1_inadimplente": 0.15,
        "stability_score": 0.10,
    },
    "final_score": {
        "technical_score": 0.75,
        "interpretability_score": 0.15,
        "operational_simplicity_score": 0.10,
    },
    "notes": (
        "Pesos didaticos da Alura. Em producao, "
        "devem ser validados por negocio, risco, "
        "compliance e engenharia."
    ),
}

INTERPRETABILIDADE = {
    "logistic_regression": 1.00,
    "decision_tree": 0.80,
    "random_forest": 0.50,
}

SIMPLICIDADE = {
    "logistic_regression": 1.00,
    "decision_tree": 0.90,
    "random_forest": 0.65,
}

MODELOS = set(INTERPRETABILIDADE)

METRICAS = [
    "roc_auc_teste",
    "roc_auc_cv_media",
    "roc_auc_cv_desvio",
    "accuracy_teste",
    "precision_inadimplente",
    "recall_inadimplente",
    "f1_inadimplente",
]


def buscar_candidatos():
    configurar_tracking()

    exp = mlflow.get_experiment_by_name(
        EXPERIMENT_NAME
    )

    if exp is None:
        raise RuntimeError("Experimento nao encontrado.")

    runs = mlflow.search_runs(
        experiment_ids=[exp.experiment_id],
        filter_string=(
            "tags.course_lesson = 'aula_04' "
            "AND attributes.status = 'FINISHED'"
        ),
        order_by=["metrics.roc_auc_teste DESC"],
    )

    if runs.empty:
        raise RuntimeError("Nao existem runs concluidas.")

    nome_col = "params.candidate_name"

    if nome_col not in runs.columns:
        raise RuntimeError(
            "Parametro candidate_name nao encontrado."
        )

    if "tags.tracking_type" not in runs.columns:
        raise RuntimeError(
            "Tag tracking_type nao encontrada."
        )

    # IDs originais da Aula 07 impedem incluir runs
    # adicionais e experimentos de outra etapa.
    anterior = json.loads(
        (RESULTADOS / "aula07_comparacao_autolog.json")
        .read_text(encoding="utf-8")
    )

    ids = {
        item["run_id"]
        for item in anterior["ranking"]
    }

    runs = runs.loc[
        runs["run_id"].isin(ids)
        & runs[nome_col].isin(MODELOS)
        & (runs["tags.tracking_type"] == "hybrid_autolog")
    ].copy()

    if (
        len(runs) != 3
        or set(runs[nome_col]) != MODELOS
        or runs["run_id"].nunique() != 3
    ):
        raise RuntimeError(
            "Esperadas exatamente 3 runs originais."
        )

    return exp, runs


def calcular_ranking(runs):
    """Aplica os pesos exatos apresentados na aula."""

    colunas = {
        "tags.mlflow.runName": "run_name",
        "params.candidate_name": "model_name",
    }

    for metrica in METRICAS:
        colunas[f"metrics.{metrica}"] = metrica

    faltantes = [
        col for col in colunas if col not in runs.columns
    ]

    if faltantes:
        raise RuntimeError(
            f"Metricas ausentes: {faltantes}"
        )

    df = (
        runs[["run_id", *colunas]]
        .rename(columns=colunas)
        .copy()
    )

    df[METRICAS] = df[METRICAS].astype(float)

    if not np.isfinite(
        df[METRICAS].to_numpy()
    ).all():
        raise RuntimeError("Metricas invalidas.")

    df["interpretability_score"] = (
        df["model_name"].map(INTERPRETABILIDADE)
    )

    df["operational_simplicity_score"] = (
        df["model_name"].map(SIMPLICIDADE)
    )

    df["stability_score"] = (
        1 - df["roc_auc_cv_desvio"].clip(
            lower=0,
            upper=1,
        )
    )

    tecnico = POLITICA["technical_score"]
    final = POLITICA["final_score"]

    df["technical_score"] = sum(
        peso * df[metrica]
        for metrica, peso in tecnico.items()
    )

    df["final_score"] = sum(
        peso * df[metrica]
        for metrica, peso in final.items()
    )

    df = df.sort_values(
        ["final_score", "roc_auc_teste", "model_name"],
        ascending=[False, False, True],
    ).reset_index(drop=True)

    df["candidate_role"] = [
        "champion_candidate" if i == 0
        else "challenger"
        for i in range(len(df))
    ]

    return df


def localizar_modelo_da_run(run_id):
    """Consulta o modelo salvo pelo autolog no MLflow 3."""

    encontrados = mlflow.search_logged_models(
        filter_string=f"source_run_id = '{run_id}'",
        output_format="list",
    )

    if encontrados:
        model_id = encontrados[0].model_id
        return {
            "model_id": model_id,
            "model_uri": f"models:/{model_id}",
            "localizado": True,
        }

    # Nao inventa o caminho 'model' caso a run
    # nao possua um Logged Model associado.
    return {
        "model_id": None,
        "model_uri": None,
        "localizado": False,
    }


def artefatos_registrados(client, run_id):
    return {
        item.path
        for item in client.list_artifacts(
            run_id,
            path="selection",
        )
        if not item.is_dir
    }


def gerar_resumo(champion, modelo_info):
    return f"""# Selecao do modelo campeao

## Contexto

Projeto: risco de credito
Tarefa: classificacao binaria
Target: inadimplente
Dataset: synthetic_credit_v1

## Modelo selecionado

- Run name: {champion['run_name']}
- Run ID: {champion['run_id']}
- Algoritmo: {champion['model_name']}
- Modelo MLflow: {modelo_info['model_uri'] or 'nao localizado'}

## Metricas

- ROC-AUC teste: {champion['roc_auc_teste']:.4f}
- ROC-AUC CV media: {champion['roc_auc_cv_media']:.4f}
- ROC-AUC CV desvio: {champion['roc_auc_cv_desvio']:.4f}
- Recall inadimplente: {champion['recall_inadimplente']:.4f}
- Precision inadimplente: {champion['precision_inadimplente']:.4f}
- F1 inadimplente: {champion['f1_inadimplente']:.4f}

## Pontuacoes

- Score tecnico: {champion['technical_score']:.4f}
- Interpretabilidade: {champion['interpretability_score']:.4f}
- Simplicidade: {champion['operational_simplicity_score']:.4f}
- Score final: {champion['final_score']:.4f}

## Pesos tecnicos

- ROC-AUC: 35%
- Recall: 25%
- Precision: 15%
- F1: 15%
- Estabilidade: 10%

## Pesos finais

- Desempenho tecnico: 75%
- Interpretabilidade: 15%
- Simplicidade operacional: 10%

## Justificativa

O algoritmo apresentou o maior score final
entre os tres candidatos, considerando a
politica didatica da aula.

A escolha nao equivale a aprovacao para
uso real em decisoes de credito.

## Proxima etapa

Preparar o registro e versionamento do
modelo no MLflow Model Registry.
"""


def executar():
    """Calcula, salva e audita a decisao."""

    exp, runs = buscar_candidatos()
    ranking = calcular_ranking(runs)

    champion = ranking.iloc[0].to_dict()
    run_id = champion["run_id"]

    client = MlflowClient()

    modelo_info = localizar_modelo_da_run(run_id)

    print("\n===== RANKING FINAL =====")
    print(
        ranking[[
            "model_name",
            "roc_auc_teste",
            "recall_inadimplente",
            "technical_score",
            "final_score",
        ]].round(4).to_string(index=False)
    )

    print("\nCANDIDATO CAMPEAO:", champion["model_name"])
    print("RUN ID:", run_id)
    print("SCORE FINAL:", f"{champion['final_score']:.4f}")
    print("MODEL URI:", modelo_info["model_uri"])

    PASTA.mkdir(parents=True, exist_ok=True)

    ranking.to_csv(
        CSV,
        index=False,
        encoding="utf-8-sig",
    )

    POLITICA_JSON.write_text(
        json.dumps(POLITICA, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    resumo = gerar_resumo(champion, modelo_info)

    RESUMO_MD.write_text(
        resumo,
        encoding="utf-8",
    )

    preparacao = {
        "registered_model_name": REGISTRY_NAME,
        "champion_run_id": run_id,
        "champion_model_name": champion["model_name"],
        **modelo_info,
        "registered": False,
        "promoted": False,
    }

    PREPARACAO_JSON.write_text(
        json.dumps(
            preparacao,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    # Atualiza apenas as tags de decisao.
    # A aula anterior havia marcado todas
    # as runs como 'candidate'.
    for _, item in ranking.iterrows():
        status = (
            "champion candidate"
            if item["run_id"] == run_id
            else "challenger"
        )

        client.set_tag(
            item["run_id"],
            "selection_status",
            status,
        )

    tags = {
        "selected_for_registry": "true",
        "selection_rule": "weighted_score v1",
        "registry_model_name": REGISTRY_NAME,
        "course_lesson_selection": "aula_05",
    }

    for chave, valor in tags.items():
        client.set_tag(run_id, chave, valor)

    # Registra artefatos na run existente,
    # sem abrir uma nova run ou alterar metricas.
    existentes = artefatos_registrados(
        client, run_id
    )

    if "selection/champion_summary.md" not in existentes:
        client.log_text(
            run_id,
            resumo,
            "selection/champion_summary.md",
        )

    if "selection/selection_policy.json" not in existentes:
        client.log_dict(
            run_id,
            POLITICA,
            "selection/selection_policy.json",
        )

    if "selection/decision_matrix.json" not in existentes:
        client.log_table(
            run_id,
            ranking,
            "selection/decision_matrix.json",
        )

    if "selection/preparacao_registry.json" not in existentes:
        client.log_dict(
            run_id,
            preparacao,
            "selection/preparacao_registry.json",
        )

    esperados = {
        "selection/champion_summary.md",
        "selection/selection_policy.json",
        "selection/decision_matrix.json",
        "selection/preparacao_registry.json",
    }

    encontrados = artefatos_registrados(
        client, run_id
    )

    if not esperados.issubset(encontrados):
        raise RuntimeError(
            "Artefatos de selecao incompletos: "
            + str(sorted(esperados - encontrados))
        )

    for _, item in ranking.iterrows():
        atual = client.get_run(item["run_id"])

        esperado = (
            "champion candidate"
            if item["run_id"] == run_id
            else "challenger"
        )

        assert atual.data.tags["selection_status"] == esperado

    resultado = {
        "aula": 10,
        "experiment_id": exp.experiment_id,
        "champion": champion,
        "model": modelo_info,
        "registry_name": REGISTRY_NAME,
        "selection_policy": POLITICA,
        "ranking": ranking.to_dict(orient="records"),
        "selection_artifacts": sorted(esperados),
        "novos_treinamentos": 0,
        "novas_runs": 0,
        "registro_model_registry": False,
    }

    RESULTADO_JSON.write_text(
        json.dumps(
            resultado,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print("\n===== DECISAO VALIDADA =====")
    print("CANDIDATO:", champion["model_name"])
    print("RUN:", run_id)
    print("SCORE TECNICO:", f"{champion['technical_score']:.4f}")
    print("SCORE FINAL:", f"{champion['final_score']:.4f}")
    print("ARTEFATOS DE SELECAO:", len(esperados))
    print("MODELO LOCALIZADO:", modelo_info["localizado"])
    print("MODEL REGISTRY: AINDA NAO REGISTRADO")

    return resultado


if __name__ == "__main__":
    executar()
