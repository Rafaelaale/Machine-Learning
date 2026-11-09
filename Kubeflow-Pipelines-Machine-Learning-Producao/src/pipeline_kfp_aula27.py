from kfp import dsl, compiler, kubernetes
from kfp.dsl import Input, Output, Dataset, Metrics

IMAGE = "fraude-trainer:2.4"


@dsl.component(base_image=IMAGE)
def load_dataset(
    csv_path: str,
    output_df: Output[Dataset]
):
    import pandas as pd

    df = pd.read_csv(csv_path)

    print(f"Dataset carregado: {len(df)} linhas")

    df.to_csv(output_df.path, index=False)


@dsl.component(base_image=IMAGE)
def process_to_pvc(raw: Input[Dataset]) -> str:
    import pandas as pd
    import os
    import uuid
    from src.features import build_features

    df = pd.read_csv(raw.path)
    df = build_features(df)

    pasta = "/models/kfp-aula27/" + uuid.uuid4().hex
    os.makedirs(pasta, exist_ok=True)

    caminho = pasta + "/features.parquet"

    df.to_parquet(caminho, index=False)

    print(f"Features salvas: {caminho}")

    return caminho


@dsl.component(base_image=IMAGE)
def submit_training(
    features_path: str,
    eta: float,
    max_depth: int,
    n_estimators: int
) -> str:

    import time
    from kubernetes import client, config

    config.load_incluster_config()

    with open(
        "/var/run/secrets/kubernetes.io/serviceaccount/namespace"
    ) as arquivo:
        namespace = arquivo.read().strip()

    batch = client.BatchV1Api()

    pasta = features_path.rsplit("/", 1)[0]

    ambiente = [
        client.V1EnvVar(name="CSV", value=features_path),
        client.V1EnvVar(name="MODELS_DIR", value=pasta),
        client.V1EnvVar(name="ETA", value=str(eta)),
        client.V1EnvVar(name="MAX_DEPTH", value=str(max_depth)),
        client.V1EnvVar(
            name="N_ESTIMATORS",
            value=str(n_estimators)
        )
    ]

    container = client.V1Container(
        name="trainer",
        image="fraude-trainer:2.4",
        image_pull_policy="Never",
        command=["python", "-m", "src.train_node_kfp"],
        env=ambiente,
        resources=client.V1ResourceRequirements(
            requests={"cpu": "250m", "memory": "512Mi"},
            limits={"cpu": "2", "memory": "3Gi"}
        ),
        volume_mounts=[
            client.V1VolumeMount(
                name="models",
                mount_path="/models"
            )
        ]
    )

    pod = client.V1PodSpec(
        restart_policy="Never",
        containers=[container],
        volumes=[
            client.V1Volume(
                name="models",
                persistent_volume_claim=client.V1PersistentVolumeClaimVolumeSource(
                    claim_name="models-pvc-kubeflow"
                )
            )
        ]
    )

    job = client.V1Job(
        api_version="batch/v1",
        kind="Job",
        metadata=client.V1ObjectMeta(
            generate_name="fraude-kfp-",
            namespace=namespace
        ),
        spec=client.V1JobSpec(
            backoff_limit=0,
            template=client.V1PodTemplateSpec(spec=pod)
        )
    )

    criado = batch.create_namespaced_job(namespace, job)
    nome = criado.metadata.name

    print(f"Job criado: {nome}", flush=True)

    inicio = time.monotonic()

    while time.monotonic() - inicio < 600:
        estado = batch.read_namespaced_job(
            name=nome,
            namespace=namespace
        ).status

        if estado.succeeded and estado.succeeded >= 1:
            print("Treinamento concluido", flush=True)
            return pasta + "/metrics.json"

        if estado.failed and estado.failed > 0:
            raise RuntimeError(f"Treinamento falhou: {nome}")

        time.sleep(5)

    raise TimeoutError(f"Job excedeu 600 segundos: {nome}")


@dsl.component(base_image=IMAGE)
def read_metrics(
    metrics_path: str,
    metrics: Output[Metrics]
) -> float:

    import json

    with open(metrics_path, encoding="utf-8") as arquivo:
        dados = json.load(arquivo)

    for nome, valor in dados.items():
        if isinstance(valor, (int, float)) and not isinstance(valor, bool):
            metrics.log_metric(nome, float(valor))

    resultado = float(dados["val_pr_auc"])

    print(f"PR-AUC validacao: {resultado:.4f}")

    return resultado


@dsl.pipeline(
    name="fraude-pipeline-kfp-aula27",
    description="Load, processamento, Job XGBoost e metricas"
)
def fraude_pipeline(
    eta: float = 0.2430296138044891,
    max_depth: int = 5,
    n_estimators: int = 194
):

    load = load_dataset(
        csv_path="/data/creditcard.csv"
    ).set_caching_options(False)

    kubernetes.mount_pvc(
        load,
        pvc_name="dataset-fraude",
        mount_path="/data"
    )

    process = process_to_pvc(
        raw=load.outputs["output_df"]
    ).set_caching_options(False)

    kubernetes.mount_pvc(
        process,
        pvc_name="models-pvc-kubeflow",
        mount_path="/models"
    )

    train = submit_training(
        features_path=process.output,
        eta=eta,
        max_depth=max_depth,
        n_estimators=n_estimators
    ).set_caching_options(False).after(process)

    metrics = read_metrics(
        metrics_path=train.output
    ).set_caching_options(False).after(train)

    kubernetes.mount_pvc(
        metrics,
        pvc_name="models-pvc-kubeflow",
        mount_path="/models"
    )


if __name__ == "__main__":
    compiler.Compiler().compile(
        pipeline_func=fraude_pipeline,
        package_path="trainer/pipeline-aula27.yaml"
    )
