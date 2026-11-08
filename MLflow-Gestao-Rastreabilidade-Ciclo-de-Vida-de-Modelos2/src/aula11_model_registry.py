"""Aula 11: registro e versionamento de modelos MLflow.

Usa o banco SQLite existente do projeto.
Treina uma nova run de registro para o campeao
selecionado na Aula 10.

Registra modelo, signature, metadados e aliases.
Nao promove o modelo para producao.
"""

import json
from pathlib import Path

import mlflow
import mlflow.sklearn

from mlflow.models import infer_signature
from mlflow.tracking import MlflowClient

from sklearn.base import clone
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

from src.aula04_primeira_run_mlflow import (
    RAIZ,
    TARGET,
    carregar_dados,
    configurar_tracking,
)

from src.aula07_autolog import (
    make_candidates,
    make_pipeline,
)


EXPERIMENT_NAME = "risco_credito_06_model_registry"
REGISTERED_MODEL_NAME = "risco_credito_classifier"
RUN_NAME = "aula06_register_champion"

RESULTADO = (
    RAIZ
    / "resultados"
    / "aula11_model_registry.json"
)

DECISAO = (
    RAIZ
    / "resultados"
    / "aula10_escolha_campeao.json"
)

ANOTACAO = (
    RAIZ
    / "anotacoes"
    / "aula11_registry_resultado.md"
)


def carregar_decisao():
    """Recupera o campeao real da Aula 10."""

    dados = json.loads(
        DECISAO.read_text(encoding="utf-8")
    )

    champion = dados["champion"]
    nome = champion["model_name"]

    if nome not in make_candidates():
        raise ValueError(
            "Algoritmo selecionado nao reconhecido: "
            + str(nome)
        )

    return {
        "model_name": nome,
        "selection_run_id": champion["run_id"],
        "selection_score": champion["final_score"],
    }


def build_estimator(model_name):
    """Cria um estimador novo e nao ajustado."""

    candidatos = make_candidates()

    if model_name not in candidatos:
        raise ValueError(
            f"Modelo nao reconhecido: {model_name}"
        )

    return clone(candidatos[model_name])


def configurar_registry():
    """Reutiliza o mesmo backend SQLite do projeto."""

    tracking_uri = configurar_tracking()

    if not tracking_uri.startswith("sqlite:///"):
        raise RuntimeError(
            "Tracking nao aponta para o SQLite esperado."
        )

    mlflow.set_registry_uri(tracking_uri)
    mlflow.set_experiment(EXPERIMENT_NAME)

    return MlflowClient(), tracking_uri


def buscar_versao_existente(client, selection_run_id):
    """Evita registrar repetidamente o mesmo campeao."""

    try:
        versoes = client.search_model_versions(
            f"name = '{REGISTERED_MODEL_NAME}'"
        )
    except Exception as exc:
        # O modelo pode nao existir ainda.
        from mlflow.exceptions import MlflowException

        if isinstance(exc, MlflowException):
            if "not found" in str(exc).lower():
                return None

        raise

    candidatas = []

    for versao in versoes:
        if not versao.run_id:
            continue

        run = client.get_run(versao.run_id)

        if (
            run.data.tags.get("selection_run_id")
            == selection_run_id
            and run.data.tags.get("run_purpose")
            == "register_champion_model"
        ):
            candidatas.append(versao)

    if not candidatas:
        return None

    return max(
        candidatas,
        key=lambda v: int(v.version),
    )


def metricas_do_modelo(y_test, y_pred, y_proba):
    """Metricas da nova run de registro."""

    return {
        "roc_auc_teste": float(
            roc_auc_score(y_test, y_proba)
        ),
        "accuracy_teste": float(
            accuracy_score(y_test, y_pred)
        ),
        "precision_inadimplente": float(
            precision_score(
                y_test, y_pred, zero_division=0
            )
        ),
        "recall_inadimplente": float(
            recall_score(
                y_test, y_pred, zero_division=0
            )
        ),
        "f1_inadimplente": float(
            f1_score(
                y_test, y_pred, zero_division=0
            )
        ),
    }


def registrar_treinamento(decisao):
    """Produz nova run e primeira versao registrada."""

    (
        df,
        X_train,
        X_test,
        y_train,
        y_test,
    ) = carregar_dados()

    estimador = build_estimator(
        decisao["model_name"]
    )

    pipe = make_pipeline(estimador)

    input_example = X_train.head(5).copy()

    # Evita capturas automaticas acidentais.
    mlflow.sklearn.autolog(disable=True)

    with mlflow.start_run(
        run_name=RUN_NAME
    ) as run:

        pipe.fit(X_train, y_train)

        y_pred = pipe.predict(X_test)
        y_proba = pipe.predict_proba(X_test)[:, 1]

        metricas = metricas_do_modelo(
            y_test,
            y_pred,
            y_proba,
        )

        mlflow.log_params({
            "model_name": decisao["model_name"],
            "registered_model_name": REGISTERED_MODEL_NAME,
            "dataset_version": "synthetic_credit_v1",
            "feature_set": "core_features_v1",
            "target": TARGET,
            "registry_lesson": "aula_06",
            "n_train": len(X_train),
            "n_test": len(X_test),
        })

        mlflow.log_metrics(metricas)

        mlflow.set_tags({
            "project": "risco_credito",
            "course_lesson": "aula_06",
            "run_purpose": "register_champion_model",
            "selection_status": "champion_candidate",
            "tracking_backend": "sqlite_local",
            "selection_run_id": decisao["selection_run_id"],
            "model_family": "linear_model"
                if decisao["model_name"] == "logistic_regression"
                else "tree_model",
        })

        signature = infer_signature(
            input_example,
            pipe.predict(input_example),
        )

        model_info = mlflow.sklearn.log_model(
            sk_model=pipe,
            name="model",
            signature=signature,
            input_example=input_example,
            registered_model_name=REGISTERED_MODEL_NAME,
            serialization_format="skops",
            skops_trusted_types=["numpy.dtype"],
        )

        run_id = run.info.run_id

    return {
        "run_id": run_id,
        "model_uri": model_info.model_uri,
        "metrics": metricas,
    }


def configurar_metadados(client, versao, decisao):
    """Adiciona descricoes e tags a versao."""

    model_description = (
        "Modelo didatico de classificacao de risco "
        "de credito. Agrupa versoes candidatas "
        "do classificador de inadimplencia. "
        "Usa dados sinteticos e nao esta aprovado "
        "para uso real em decisoes de credito."
    )

    version_description = (
        f"Versao registrada a partir da run {versao.run_id}. "
        f"Algoritmo: {decisao['model_name']}. "
        "Dataset: synthetic_credit_v1. "
        "Feature set: core_features_v1. "
        f"Run da selecao: {decisao['selection_run_id']}."
    )

    client.update_registered_model(
        name=REGISTERED_MODEL_NAME,
        description=model_description,
    )

    client.update_model_version(
        name=REGISTERED_MODEL_NAME,
        version=versao.version,
        description=version_description,
    )

    for chave, valor in {
        "project": "risco_credito",
        "task": "binary_classification",
        "target": TARGET,
    }.items():
        client.set_registered_model_tag(
            REGISTERED_MODEL_NAME,
            chave,
            valor,
        )

    for chave, valor in {
        "dataset_version": "synthetic_credit_v1",
        "feature_set": "core_features_v1",
        "lifecycle_status": "candidate",
        "selection_run_id": decisao["selection_run_id"],
        "algorithm": decisao["model_name"],
    }.items():
        client.set_model_version_tag(
            REGISTERED_MODEL_NAME,
            versao.version,
            chave,
            valor,
        )

    # Nao usa aliases de producao nesta aula.
    for alias in (
        "candidate",
        decisao["model_name"],
    ):
        try:
            atual = client.get_model_version_by_alias(
                REGISTERED_MODEL_NAME,
                alias,
            )
        except Exception as exc:
            from mlflow.exceptions import MlflowException

            if isinstance(exc, MlflowException):
                if "not found" in str(exc).lower():
                    atual = None
                else:
                    raise
            else:
                raise

        if (
            atual is not None
            and str(atual.version) != str(versao.version)
        ):
            raise RuntimeError(
                f"Alias {alias} ja aponta para outra versao. "
                "Nenhuma alteracao automatica foi feita."
            )

        client.set_registered_model_alias(
            name=REGISTERED_MODEL_NAME,
            alias=alias,
            version=versao.version,
        )


def executar():
    """Executa ou valida o registro do campeao."""

    decisao = carregar_decisao()

    client, tracking_uri = configurar_registry()

    if mlflow.active_run() is not None:
        raise RuntimeError(
            "Ha uma run ativa. Encerre-a antes."
        )

    versao = buscar_versao_existente(
        client,
        decisao["selection_run_id"],
    )

    if versao is None:
        print("\n===== REGISTRANDO MODELO =====")
        print("CAMPEAO:", decisao["model_name"])

        registro = registrar_treinamento(decisao)

        versoes = client.search_model_versions(
            f"name = '{REGISTERED_MODEL_NAME}'"
        )

        correspondentes = [
            v for v in versoes
            if v.run_id == registro["run_id"]
        ]

        if not correspondentes:
            raise RuntimeError(
                "Nenhuma versao associada a nova run."
            )

        versao = max(
            correspondentes,
            key=lambda v: int(v.version),
        )
    else:
        print("\nVERSAO EXISTENTE LOCALIZADA")
        print("NENHUMA NOVA VERSAO CRIADA")

    configurar_metadados(
        client,
        versao,
        decisao,
    )

    atualizada = client.get_model_version(
        REGISTERED_MODEL_NAME,
        versao.version,
    )

    alias_candidate = client.get_model_version_by_alias(
        REGISTERED_MODEL_NAME,
        "candidate",
    )

    alias_algoritmo = client.get_model_version_by_alias(
        REGISTERED_MODEL_NAME,
        decisao["model_name"],
    )

    if (
        str(alias_candidate.version) != str(versao.version)
        or str(alias_algoritmo.version) != str(versao.version)
    ):
        raise RuntimeError("Aliases nao correspondem a versao.")

    run = client.get_run(versao.run_id)

    if run.info.status != "FINISHED":
        raise RuntimeError("Run nao finalizada.")

    resultado = {
        "aula_local": 11,
        "registered_model_name": REGISTERED_MODEL_NAME,
        "version": str(versao.version),
        "status": atualizada.status,
        "source": atualizada.source,
        "registration_run_id": versao.run_id,
        "selection_run_id": decisao["selection_run_id"],
        "champion_model_name": decisao["model_name"],
        "selection_score": decisao["selection_score"],
        "tracking_uri": tracking_uri,
        "model_uri": (
            f"models:/{REGISTERED_MODEL_NAME}/{versao.version}"
        ),
        "candidate_alias_uri": (
            f"models:/{REGISTERED_MODEL_NAME}@candidate"
        ),
        "aliases": [
            "candidate",
            decisao["model_name"],
        ],
        "metrics": dict(run.data.metrics),
        "registry_created": True,
        "production_promoted": False,
    }

    RESULTADO.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    RESULTADO.write_text(
        json.dumps(
            resultado,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    ANOTACAO.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    ANOTACAO.write_text(
        f"""# Aula 11 - Model Registry

## Modelo registrado

Nome: {REGISTERED_MODEL_NAME}
Versao: {versao.version}
Status: {atualizada.status}

## Origem

Algoritmo: {decisao['model_name']}
Run da selecao: {decisao['selection_run_id']}
Run do registro: {versao.run_id}

## URIs

Versao: models:/{REGISTERED_MODEL_NAME}/{versao.version}
Alias: models:/{REGISTERED_MODEL_NAME}@candidate

## Metadados

Dataset: synthetic_credit_v1
Feature set: core_features_v1
Lifecycle: candidate

## Proxima aula

Promocao para homologacao e producao.

Este modelo ainda nao foi aprovado
para uso real em credito.
""",
        encoding="utf-8",
    )

    print("\n===== MODEL REGISTRY VALIDADO =====")
    print("MODELO:", REGISTERED_MODEL_NAME)
    print("VERSAO:", versao.version)
    print("STATUS:", atualizada.status)
    print("RUN REGISTRO:", versao.run_id)
    print("RUN SELECAO:", decisao["selection_run_id"])
    print("SOURCE:", atualizada.source)
    print("ALIAS CANDIDATE:", alias_candidate.version)
    print("ALIAS MODELO:", alias_algoritmo.version)
    print("MODEL URI:", resultado["model_uri"])
    print("PROMOVIDO PARA PRODUCAO: NAO")

    return resultado


if __name__ == "__main__":
    executar()
