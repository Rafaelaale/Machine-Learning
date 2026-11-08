"""MLflow Project - prepare: dados sinteticos reprodutiveis."""

import argparse
import json
import re
from pathlib import Path

import mlflow
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from src.aula04_primeira_run_mlflow import RAIZ

EXPERIMENTO = "risco_credito_08_mlflow_projects"
ALVO = "inadimplente"

FEATURES = [
    "idade",
    "renda_mensal",
    "tempo_emprego_anos",
    "score_interno",
    "valor_solicitado",
    "num_parcelas",
    "tipo_renda",
    "possui_restricao",
]


def gerar_dados(n_samples=6000, random_state=42):
    """Gera dados artificiais com oito features."""

    if n_samples < 100:
        raise ValueError("n_samples deve ser >= 100.")

    rng = np.random.default_rng(random_state)

    idade = rng.integers(18, 76, n_samples)
    renda = rng.uniform(1500, 16000, n_samples)
    emprego = rng.uniform(0, 25, n_samples)
    score = rng.integers(300, 851, n_samples)
    valor = rng.uniform(1500, 80000, n_samples)
    parcelas = rng.choice(
        [6, 12, 18, 24, 36, 48, 60],
        size=n_samples,
    )
    renda_tipo = rng.choice(
        ["CLT", "Autonomo", "Servidor"],
        size=n_samples,
        p=[0.60, 0.25, 0.15],
    )
    restricao = rng.choice(
        ["sim", "nao"],
        size=n_samples,
        p=[0.18, 0.82],
    )

    # Regra sintetica educacional, nao politica real.
    risco = (
        -1.4
        + 1.2 * (valor / np.maximum(renda * 8, 1))
        - 0.008 * (score - 550)
        - 0.03 * emprego
        + 1.4 * (restricao == "sim")
        + 0.4 * (renda_tipo == "Autonomo")
    )

    prob = 1 / (1 + np.exp(-np.clip(risco, -20, 20)))
    alvo = rng.binomial(1, prob)

    return pd.DataFrame({
        "idade": idade,
        "renda_mensal": np.round(renda, 2),
        "tempo_emprego_anos": np.round(emprego, 2),
        "score_interno": score,
        "valor_solicitado": np.round(valor, 2),
        "num_parcelas": parcelas,
        "tipo_renda": renda_tipo,
        "possui_restricao": restricao,
        "inadimplente": alvo,
    })


def preparar(
    n_samples=6000,
    test_size=0.25,
    random_state=42,
    output_dir="data/processed",
    pipeline_id="manual",
):
    if not 0.05 <= test_size <= 0.5:
        raise ValueError("test_size fora do intervalo permitido.")

    if not re.fullmatch(r"[A-Za-z0-9_-]{1,80}", pipeline_id):
        raise ValueError("pipeline_id invalido.")

    base = Path(output_dir)

    if not base.is_absolute():
        base = RAIZ / base

    destino = base / pipeline_id

    # Evita sobrescrever resultados de outros pipelines.
    destino.mkdir(parents=True, exist_ok=True)

    for nome in ("full.csv", "train.csv", "test.csv"):
        if (destino / nome).exists():
            raise FileExistsError(
                f"Arquivo existente preservado: {destino / nome}. "
                "Escolha outro pipeline_id."
            )

    df = gerar_dados(n_samples, random_state)

    treino, teste = train_test_split(
        df,
        test_size=test_size,
        random_state=random_state,
        stratify=df[ALVO],
    )

    caminhos = {
        "full": destino / "full.csv",
        "train": destino / "train.csv",
        "test": destino / "test.csv",
    }

    df.to_csv(caminhos["full"], index=False)
    treino.to_csv(caminhos["train"], index=False)
    teste.to_csv(caminhos["test"], index=False)

    mlflow.set_experiment(EXPERIMENTO)

    with mlflow.start_run() as run:
        mlflow.log_params({
            "step": "prepare",
            "n_samples": n_samples,
            "test_size": test_size,
            "random_state": random_state,
            "pipeline_id": pipeline_id,
            "base_output_dir": str(base),
            "output_dir_final": str(destino),
        })

        mlflow.log_metrics({
            "total_amostras": len(df),
            "amostras_treino": len(treino),
            "amostras_teste": len(teste),
            "taxa_inadimplencia": float(df[ALVO].mean()),
        })

        mlflow.set_tags({
            "project": "risco_credito",
            "course_lesson": "aula_17",
            "pipeline_step": "prepare",
            "pipeline_id": pipeline_id,
        })

        for caminho in caminhos.values():
            mlflow.log_artifact(
                str(caminho),
                artifact_path="data",
            )

        run_id = run.info.run_id

    resultado = {
        "pipeline_id": pipeline_id,
        "run_id": run_id,
        "n_samples": len(df),
        "n_train": len(treino),
        "n_test": len(teste),
        "positive_rate": float(df[ALVO].mean()),
        "data_dir": str(destino),
        "columns": list(df.columns),
        "random_state": random_state,
        "test_size": test_size,
    }

    (destino / "manifest.json").write_text(
        json.dumps(resultado, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    if pipeline_id.startswith("aula18_"):
        relatorio = (
            RAIZ / "resultados" / "aula18_pipeline"
            / pipeline_id / "prepare.json"
        )
        relatorio.parent.mkdir(parents=True, exist_ok=True)
    else:
        relatorio = RAIZ / "resultados" / "aula17_prepare.json"

    relatorio.write_text(
        json.dumps(resultado, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print("PREPARE CONCLUIDO")
    print("PIPELINE_ID:", pipeline_id)
    print("DADOS:", destino)
    print("TREINO:", len(treino))
    print("TESTE:", len(teste))
    print("RUN_ID:", run_id)

    return resultado


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-samples", type=int, default=6000)
    parser.add_argument("--test-size", type=float, default=0.25)
    parser.add_argument("--random-state", type=int, default=42)
    parser.add_argument("--output-dir", default="data/processed")
    parser.add_argument("--pipeline-id", default="manual")

    args = parser.parse_args()

    preparar(
        n_samples=args.n_samples,
        test_size=args.test_size,
        random_state=args.random_state,
        output_dir=args.output_dir,
        pipeline_id=args.pipeline_id,
    )


if __name__ == "__main__":
    main()
