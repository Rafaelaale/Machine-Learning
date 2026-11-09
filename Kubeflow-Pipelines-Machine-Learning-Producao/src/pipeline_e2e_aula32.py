from kfp import compiler, dsl, kubernetes as k8s

from src.pipeline_kfp_aula27 import (
    load_dataset,
    process_to_pvc,
    submit_training,
    read_metrics,
)


@dsl.component(base_image="fraude-trainer:2.4")
def promote_model(metrics_path: str, threshold: float) -> str:
    import json
    import shutil
    import uuid
    from pathlib import Path

    metrics_file = Path(metrics_path)
    modelo = metrics_file.with_name("model.ubj")

    with metrics_file.open(encoding="utf-8") as f:
        metricas = json.load(f)

    auc = float(metricas["val_pr_auc"])

    if auc < threshold:
        raise RuntimeError("Modelo reprovado")

    if not modelo.is_file() or modelo.stat().st_size == 0:
        raise RuntimeError("Modelo nao encontrado")

    destino = Path("/models/serving/releases") / uuid.uuid4().hex
    destino.mkdir(parents=True, exist_ok=False)

    novo_modelo = destino / "model.ubj"
    shutil.copy2(modelo, novo_modelo)

    if novo_modelo.stat().st_size != modelo.stat().st_size:
        raise RuntimeError("Falha ao copiar modelo")

    print(f"Modelo aprovado: PR-AUC={auc:.4f}")
    print(f"Modelo promovido: {novo_modelo}")

    return str(novo_modelo)


@dsl.component(base_image="fraude-trainer:2.4")
def deploy_model(model_path: str) -> str:
    import time
    from kubernetes import client, config

    config.load_incluster_config()

    apps = client.AppsV1Api()
    namespace = "kubeflow"
    nome = "fraude-predictor-compat"

    atual = apps.read_namespaced_deployment(nome, namespace)

    if (atual.status.ready_replicas or 0) < 1:
        raise RuntimeError(
            "Predictor atual nao esta Ready. "
            "Deploy bloqueado para proteger a versao anterior."
        )

    container = next(
        c for c in atual.spec.template.spec.containers
        if c.name == "predictor"
    )

    anterior = next(
        (e.value for e in (container.env or [])
         if e.name == "MODEL_PATH"),
        None,
    )

    if not anterior:
        raise RuntimeError("MODEL_PATH anterior nao encontrado")

    def atualizar(path):
        apps.patch_namespaced_deployment(
            nome,
            namespace,
            {
                "spec": {
                    "template": {
                        "spec": {
                            "containers": [{
                                "name": "predictor",
                                "env": [{
                                    "name": "MODEL_PATH",
                                    "value": path
                                }]
                            }]
                        }
                    }
                }
            },
        )

    atualizar(model_path)

    for _ in range(60):
        dep = apps.read_namespaced_deployment(nome, namespace)
        status = dep.status

        if (
            status.observed_generation == dep.metadata.generation
            and (status.updated_replicas or 0) == 1
            and (status.ready_replicas or 0) == 1
            and (status.replicas or 0) == 1
        ):
            print(f"Modelo publicado: {model_path}")
            return model_path

        time.sleep(5)

    atualizar(anterior)
    raise RuntimeError(
        "Novo predictor nao ficou pronto. "
        "Configuracao anterior restaurada; verificar rollout."
    )


@dsl.pipeline(
    name="fraude-pipeline-e2e-aula32",
    description="Load, process, XGBoost, metricas, promocao e deploy"
)
def fraude_pipeline_e2e(
    eta: float = 0.2430296138044891,
    max_depth: int = 5,
    n_estimators: int = 194,
    threshold: float = 0.70,
):

    ld = load_dataset(
        csv_path="/data/creditcard.csv"
    ).set_display_name("load").set_caching_options(False)

    k8s.mount_pvc(
        ld,
        pvc_name="dataset-fraude",
        mount_path="/data"
    )

    pr = process_to_pvc(
        raw=ld.outputs["output_df"]
    ).set_display_name("process").set_caching_options(False)

    k8s.mount_pvc(
        pr,
        pvc_name="models-pvc-kubeflow",
        mount_path="/models"
    )

    tj = submit_training(
        features_path=pr.output,
        eta=eta,
        max_depth=max_depth,
        n_estimators=n_estimators
    ).set_display_name("train").set_caching_options(False)

    rm = read_metrics(
        metrics_path=tj.output
    ).set_display_name("metrics").set_caching_options(False)

    k8s.mount_pvc(
        rm,
        pvc_name="models-pvc-kubeflow",
        mount_path="/models"
    )

    with dsl.If(
        rm.outputs["Output"] >= threshold,
        name="modelo-aprovado"
    ):

        pm = promote_model(
            metrics_path=tj.output,
            threshold=threshold
        ).set_display_name("promote").set_caching_options(False)

        k8s.mount_pvc(
            pm,
            pvc_name="models-pvc-kubeflow",
            mount_path="/models"
        )

        deploy_model(
            model_path=pm.output
        ).set_display_name("deploy").set_caching_options(False)


if __name__ == "__main__":
    compiler.Compiler().compile(
        fraude_pipeline_e2e,
        "trainer/pipeline-e2e-aula32.yaml"
    )
    print("PIPELINE E2E COMPILADA")
