"""Aula 08 - Comparacao de runs com a API do MLflow.

Somente consultas: nao treina, nao cria runs
e nao altera registros anteriores.
"""

import json

import mlflow
import pandas as pd

from src.aula04_primeira_run_mlflow import (
    RAIZ,
    configurar_tracking,
)
from src.aula07_autolog import EXPERIMENT_NAME


RESULTADOS = RAIZ / "resultados"

CSV_RANKING = RESULTADOS / "aula08_ranking_runs.csv"
CSV_PAPEIS = RESULTADOS / "aula08_ranking_com_papeis.csv"
CSV_SHORTLIST = RESULTADOS / "aula08_shortlist_070.csv"
CSV_RIGOROSA = RESULTADOS / "aula08_shortlist_085.csv"
JSON_RESUMO = RESULTADOS / "aula08_comparacao_runs.json"
MD_RESUMO = RESULTADOS / "aula08_resumo_comparacao.md"

COMPARISON_COLS = [
    "run_id",
    "tags.mlflow.runName",
    "params.candidate_name",
    "metrics.roc_auc_teste",
    "metrics.roc_auc_cv_media",
    "metrics.roc_auc_cv_desvio",
    "metrics.accuracy_teste",
    "metrics.precision_inadimplente",
    "metrics.recall_inadimplente",
    "metrics.f1_inadimplente",
]

CANDIDATOS = {
    "logistic_regression",
    "decision_tree",
    "random_forest",
}


def consultar_experimento():
    """Consulta as runs concluidas da Aula 07."""

    configurar_tracking()

    experimento = mlflow.get_experiment_by_name(
        EXPERIMENT_NAME
    )

    if experimento is None:
        raise RuntimeError(
            "Experimento de comparacao nao encontrado."
        )

    runs = mlflow.search_runs(
        experiment_ids=[experimento.experiment_id],
        filter_string=(
            "tags.course_lesson = 'aula_04' "
            "AND attributes.status = 'FINISHED'"
        ),
        order_by=[
            "metrics.roc_auc_teste DESC",
        ],
    )

    if runs.empty:
        raise RuntimeError(
            "Nenhuma run concluida foi encontrada."
        )

    # Concentra a consulta nas runs da Aula 07.
    # Uma mesma experiencia pode ter runs adicionais
    # no futuro, que nao devem contaminar a comparacao.
    if "tags.tracking_type" not in runs.columns:
        raise RuntimeError("Tag tracking_type ausente.")

    if "params.candidate_name" not in runs.columns:
        raise RuntimeError("Parametro candidate_name ausente.")

    runs = runs.loc[
        (runs["tags.tracking_type"] == "hybrid_autolog")
        & runs["params.candidate_name"].isin(CANDIDATOS)
    ].copy()

    faltantes = [
        coluna for coluna in COMPARISON_COLS
        if coluna not in runs.columns
    ]

    if faltantes:
        raise RuntimeError(
            f"Colunas nao encontradas: {faltantes}"
        )

    # Preserva apenas uma run por candidato.
    # Em repeticoes, usa a run valida mais recente.
    runs = (
        runs.sort_values(
            "start_time",
            ascending=False,
        )
        .drop_duplicates(
            subset=["params.candidate_name"],
            keep="first",
        )
        .sort_values(
            "metrics.roc_auc_teste",
            ascending=False,
        )
        .reset_index(drop=True)
    )

    if set(runs["params.candidate_name"]) != CANDIDATOS:
        raise RuntimeError(
            "Esperadas tres runs: logistic_regression, "
            "decision_tree e random_forest."
        )

    return experimento, runs


def criar_ranking(runs):
    """Seleciona as metricas e define papeis."""

    ranking = (
        runs[COMPARISON_COLS]
        .sort_values(
            "metrics.roc_auc_teste",
            ascending=False,
        )
        .reset_index(drop=True)
    )

    com_papeis = ranking.copy()

    com_papeis["candidate_role"] = [
        "champion_candidate" if i == 0
        else "challenger"
        for i in range(len(com_papeis))
    ]

    return ranking, com_papeis


def buscar_shortlist(
    experiment_id,
    recall_minimo=0.70,
):
    """Aplica os criterios didaticos pela API."""

    if not 0 <= recall_minimo <= 1:
        raise ValueError("Limiar de recall invalido.")

    filtradas = mlflow.search_runs(
        experiment_ids=[experiment_id],
        filter_string=(
            "tags.course_lesson = 'aula_04' "
            "AND attributes.status = 'FINISHED' "
            "AND metrics.roc_auc_teste >= 0.85 "
            f"AND metrics.recall_inadimplente >= {recall_minimo}"
        ),
        order_by=[
            "metrics.roc_auc_teste DESC"
        ],
    )

    if filtradas.empty:
        return pd.DataFrame(columns=COMPARISON_COLS)

    if "tags.tracking_type" not in filtradas.columns:
        return pd.DataFrame(columns=COMPARISON_COLS)

    filtradas = filtradas.loc[
        filtradas["tags.tracking_type"]
        == "hybrid_autolog"
    ].copy()

    if filtradas.empty:
        return pd.DataFrame(columns=COMPARISON_COLS)

    filtradas = filtradas.loc[
        filtradas["params.candidate_name"].isin(
            CANDIDATOS
        )
    ]

    filtradas = (
        filtradas.sort_values(
            "start_time",
            ascending=False,
        )
        .drop_duplicates(
            subset=["params.candidate_name"],
            keep="first",
        )
        .sort_values(
            "metrics.roc_auc_teste",
            ascending=False,
        )
    )

    return filtradas[COMPARISON_COLS].reset_index(
        drop=True
    )


def executar():
    """Exporta a comparacao para CSV, JSON e Markdown."""

    experimento, runs = consultar_experimento()

    ranking, papeis = criar_ranking(runs)

    shortlist = buscar_shortlist(
        experimento.experiment_id,
        recall_minimo=0.70,
    )

    rigorosa = buscar_shortlist(
        experimento.experiment_id,
        recall_minimo=0.85,
    )

    RESULTADOS.mkdir(
        parents=True,
        exist_ok=True,
    )

    for tabela, arquivo in [
        (ranking, CSV_RANKING),
        (papeis, CSV_PAPEIS),
        (shortlist, CSV_SHORTLIST),
        (rigorosa, CSV_RIGOROSA),
    ]:
        tabela.to_csv(
            arquivo,
            index=False,
            encoding="utf-8-sig",
        )

    candidato = papeis.iloc[0]

    resumo = {
        "aula_local": 8,
        "experimento": EXPERIMENT_NAME,
        "experiment_id": experimento.experiment_id,
        "total_runs_comparadas": len(ranking),
        "shortlist_recall_070": len(shortlist),
        "shortlist_recall_085": len(rigorosa),
        "criterio_roc_auc_minimo": 0.85,
        "candidato_campeao": (
            candidato["params.candidate_name"]
        ),
        "candidate_run_id": candidato["run_id"],
        "candidate_roc_auc": float(
            candidato["metrics.roc_auc_teste"]
        ),
        "ranking": papeis.to_dict(orient="records"),
        "campeao_definitivo_selecionado": False,
        "novas_runs_criadas": 0,
    }

    JSON_RESUMO.write_text(
        json.dumps(
            resumo,
            ensure_ascii=False,
            indent=2,
            default=str,
        ),
        encoding="utf-8",
    )

    linhas = [
        "# Aula 08 - Comparacao de runs",
        "",
        f"Experimento: {EXPERIMENT_NAME}",
        f"Runs comparadas: {len(ranking)}",
        "",
        "## Ranking por ROC-AUC",
        "",
        "| Modelo | ROC-AUC | Recall | Precision | Papel |",
        "|---|---:|---:|---:|---|",
    ]

    for _, item in papeis.iterrows():
        linhas.append(
            "| {modelo} | {roc:.4f} | {rec:.4f} | "
            "{prec:.4f} | {papel} |".format(
                modelo=item["params.candidate_name"],
                roc=item["metrics.roc_auc_teste"],
                rec=item["metrics.recall_inadimplente"],
                prec=item["metrics.precision_inadimplente"],
                papel=item["candidate_role"],
            )
        )

    linhas.extend([
        "",
        "## Listas curtas",
        "",
        f"- ROC >= 0.85 e recall >= 0.70: {len(shortlist)} modelos",
        f"- ROC >= 0.85 e recall >= 0.85: {len(rigorosa)} modelos",
        "",
        "## Conclusao",
        "",
        f"Candidato inicial: {resumo['candidato_campeao']}.",
        "",
        "Esta classificacao considera apenas ROC-AUC.",
        "A escolha definitiva exige criterios adicionais.",
        "Dados sinteticos; nenhuma decisao real de credito.",
    ])

    MD_RESUMO.write_text(
        "\n".join(linhas) + "\n",
        encoding="utf-8",
    )

    print("\n===== AULA 08 - COMPARANDO RUNS =====")
    print("EXPERIMENTO:", EXPERIMENT_NAME)
    print("RUNS ENCONTRADAS:", len(runs))
    print("SHAPE:", runs.shape)

    print("\n===== RANKING POR ROC-AUC =====")
    colunas_visiveis = [
        "params.candidate_name",
        "metrics.roc_auc_teste",
        "metrics.roc_auc_cv_media",
        "metrics.precision_inadimplente",
        "metrics.recall_inadimplente",
        "metrics.f1_inadimplente",
    ]

    print(
        ranking[colunas_visiveis]
        .round(4)
        .to_string(index=False)
    )

    print("\n===== PAPEIS DOS CANDIDATOS =====")
    print(
        papeis[[
            "params.candidate_name",
            "candidate_role",
        ]].to_string(index=False)
    )

    print("\n===== SHORTLISTS =====")
    print("ROC >= 0.85 E RECALL >= 0.70:", len(shortlist))
    print("ROC >= 0.85 E RECALL >= 0.85:", len(rigorosa))
    print("CANDIDATO A CAMPEAO:", resumo["candidato_campeao"])
    print("CAMPEAO DEFINITIVO: NAO SELECIONADO")
    print("NOVOS TREINAMENTOS: 0")
    print("NOVAS RUNS: 0")

    return resumo


if __name__ == "__main__":
    executar()
