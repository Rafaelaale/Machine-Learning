import kfp

from kfp import dsl
from kfp import kubernetes as k8s
from kfp.dsl import Dataset, Input, Metrics, Model, Output


IMAGE = "fraude-trainer:1.0"
SEGMENTS = ["low", "medium", "high"]


@dsl.component(base_image=IMAGE)
def preprocess(
    csv_path: str,
    segment: str,
    output_df: Output[Dataset],
):
    import pandas as pd

    if segment not in ("low", "medium", "high"):
        raise ValueError(f"Segmento invalido: {segment}")

    df = pd.read_csv(csv_path)

    q1, q3 = df["Amount"].quantile([0.25, 0.75])

    bins = [-float("inf"), q1, q3, float("inf")]
    labels = ["low", "medium", "high"]

    df["segment"] = pd.cut(
        df["Amount"],
        bins=bins,
        labels=labels,
    )

    seg_df = (
        df[df["segment"] == segment]
        .drop(columns=["segment"])
        .reset_index(drop=True)
    )

    if seg_df.empty:
        raise ValueError(f"Segmento vazio: {segment}")

    seg_df.to_csv(output_df.path, index=False)

    print(f"Segmento: {segment}")
    print(f"Linhas: {len(seg_df)}")
    print(f"Fraudes: {int(seg_df['Class'].sum())}")


@dsl.component(base_image=IMAGE)
def train_segment(
    df: Input[Dataset],
    segment: str,
    eta: float,
    max_depth: int,
    n_estimators: int,
    model_out: Output[Model],
    metrics_out: Output[Metrics],
):
    import shutil
    import tempfile
    from pathlib import Path

    from src.train import train_from_csv

    with tempfile.TemporaryDirectory() as pasta:
        caminho_modelo = str(Path(pasta) / "model.ubj")

        result = train_from_csv(
            df.path,
            eta=eta,
            max_depth=max_depth,
            n_estimators=n_estimators,
            model_out=caminho_modelo,
        )

        shutil.copyfile(
            result.model_path,
            model_out.path,
        )

    model_out.metadata["framework"] = "xgboost"
    model_out.metadata["segment"] = segment
    model_out.metadata["format"] = "ubj"

    for nome, valor in result.val_metrics.items():
        metrics_out.log_metric(
            f"val_{nome}",
            float(valor),
        )

    for nome, valor in result.test_metrics.items():
        metrics_out.log_metric(
            f"test_{nome}",
            float(valor),
        )

    print(
        f"[{segment}] "
        f"val_pr_auc={result.val_metrics['pr_auc']:.4f}"
    )


@dsl.pipeline(
    name="fraude-pipeline",
    description="Treina 3 modelos XGBoost por segmento de Amount.",
)
def fraude_pipeline(
    csv_path: str = "/data/creditcard.csv",
    eta: float = 0.1,
    max_depth: int = 5,
    n_estimators: int = 200,
):
    for segment in SEGMENTS:

        pre = preprocess(
            csv_path=csv_path,
            segment=segment,
        ).set_display_name(f"preprocess-{segment}")

        pre.set_cpu_limit("1")
        pre.set_memory_limit("1Gi")
        pre.set_caching_options(False)

        k8s.mount_pvc(
            pre,
            pvc_name="dataset-fraude",
            mount_path="/data",
        )

        treino = train_segment(
            df=pre.outputs["output_df"],
            segment=segment,
            eta=eta,
            max_depth=max_depth,
            n_estimators=n_estimators,
        ).set_display_name(f"train-{segment}")

        treino.set_cpu_limit("1")
        treino.set_memory_limit("1500Mi")
        treino.set_caching_options(False)


if __name__ == "__main__":
    kfp.compiler.Compiler().compile(
        fraude_pipeline,
        "pipelines/pipeline.yaml",
    )
    print("PIPELINE YAML GERADO")
