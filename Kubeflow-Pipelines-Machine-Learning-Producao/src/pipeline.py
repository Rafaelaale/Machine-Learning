import kfp

from kfp import dsl
from kfp import kubernetes as k8s
from kfp.dsl import Dataset, Input, Metrics, Model, Output


IMAGE = "fraude-trainer:2.1"


@dsl.component(base_image=IMAGE)
def load_dataset(
    csv_path: str,
    output_df: Output[Dataset],
):
    import pandas as pd

    df = pd.read_csv(csv_path)
    df.to_csv(output_df.path, index=False)

    print(f"Dataset carregado: {len(df)} linhas")


@dsl.component(base_image=IMAGE)
def process(
    raw: Input[Dataset],
    features_out: Output[Dataset],
):
    import pandas as pd

    from src.features import build_features

    df = build_features(pd.read_csv(raw.path))

    df.to_parquet(
        features_out.path,
        index=False,
    )

    print(f"Features: {len(df.columns)}")
    print(f"Linhas: {len(df)}")
    print(
        "Segmentos:",
        df["segment"].value_counts().sort_index().to_dict(),
    )


@dsl.component(base_image=IMAGE)
def train_model(
    features: Input[Dataset],
    eta: float,
    max_depth: int,
    n_estimators: int,
    model_out: Output[Model],
    metrics_out: Output[Metrics],
):
    import shutil
    import tempfile

    import pandas as pd

    from pathlib import Path
    from src.train import train

    df = pd.read_parquet(features.path)

    with tempfile.TemporaryDirectory() as temp:
        caminho = str(Path(temp) / "model.ubj")

        result = train(
            df,
            eta=eta,
            max_depth=max_depth,
            n_estimators=n_estimators,
            model_out=caminho,
        )

        shutil.copyfile(
            result.model_path,
            model_out.path,
        )

    model_out.metadata["framework"] = "xgboost"
    model_out.metadata["format"] = "ubj"
    model_out.metadata["architecture"] = "single-model"

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

    print("MODELO UNICO TREINADO")


@dsl.pipeline(
    name="fraude-pipeline-unica",
    description="Load, process e train: XGBoost com segment como feature.",
)
def fraude_pipeline(
    csv_path: str = "/data/creditcard.csv",
    eta: float = 0.1,
    max_depth: int = 5,
    n_estimators: int = 200,
):
    ld = load_dataset(
        csv_path=csv_path,
    ).set_display_name("load")

    ld.set_cpu_limit("1")
    ld.set_memory_limit("1Gi")

    k8s.mount_pvc(
        ld,
        pvc_name="dataset-fraude",
        mount_path="/data",
    )

    pr = process(
        raw=ld.outputs["output_df"],
    ).set_display_name("process")

    pr.set_cpu_limit("1")
    pr.set_memory_limit("1Gi")

    tr = train_model(
        features=pr.outputs["features_out"],
        eta=eta,
        max_depth=max_depth,
        n_estimators=n_estimators,
    ).set_display_name("train")

    tr.set_cpu_limit("1")
    tr.set_memory_limit("1500Mi")


if __name__ == "__main__":
    kfp.compiler.Compiler().compile(
        fraude_pipeline,
        "pipelines/pipeline_unica.yaml",
    )

    print("PIPELINE UNICA YAML GERADO")