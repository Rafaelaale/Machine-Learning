"""Aula 12 - Promocao didatica no MLflow.

Utiliza o Model Registry existente.
Valida staging antes de configurar production.
Nao cria novas runs, versoes ou treinamentos.
"""

import json

import mlflow
import mlflow.pyfunc
import mlflow.sklearn
import numpy as np
import pandas as pd

from mlflow.tracking import MlflowClient

from src.aula04_primeira_run_mlflow import RAIZ
from src.aula11_model_registry import (
    REGISTERED_MODEL_NAME,
    configurar_registry,
)

RESULTADOS = RAIZ / "resultados"

ENTRADA = (
    RESULTADOS / "aula11_model_registry.json"
)

SAIDA = (
    RESULTADOS / "aula12_promocao_modelos.json"
)

PREVISOES = (
    RESULTADOS / "aula12_previsoes.csv"
)

RELATORIO = (
    RESULTADOS / "aula12_promocao_relatorio.md"
)

VERSAO_ALIAS = "candidate"


def novo_cliente():
    """Cliente sintetico usado na transcricao."""

    return pd.DataFrame([{
        "idade": 34,
        "renda_mensal": 4200.0,
        "tempo_emprego_anos": 5.0,
        "score_interno": 620,
        "valor_solicitado": 12000.0,
        "num_parcelas": 24,
        "tipo_renda": "CLT",
        "possui_restricao": "nao",
    }])


def carregar_registro():
    """Recupera exatamente a versao criada na Aula 11."""

    return json.loads(
        ENTRADA.read_text(encoding="utf-8")
    )


def conferir_alias(client, alias, versao):
    """Evita sobrescrever alias de outra versao."""

    try:
        atual = client.get_model_version_by_alias(
            REGISTERED_MODEL_NAME,
            alias,
        )
    except Exception as exc:
        from mlflow.exceptions import MlflowException

        if (
            isinstance(exc, MlflowException)
            and "not found" in str(exc).lower()
        ):
            return

        raise

    if str(atual.version) != str(versao):
        raise RuntimeError(
            f"O alias {alias} ja aponta para "
            f"versao {atual.version}. "
            "Nao sera sobrescrito automaticamente."
        )


def atribuir_alias(client, alias, versao):
    """Cria ou reafirma alias da versao esperada."""

    conferir_alias(client, alias, versao)

    client.set_registered_model_alias(
        name=REGISTERED_MODEL_NAME,
        alias=alias,
        version=str(versao),
    )

    atual = client.get_model_version_by_alias(
        REGISTERED_MODEL_NAME,
        alias,
    )

    if str(atual.version) != str(versao):
        raise RuntimeError(
            f"Alias {alias} aponta para versao incorreta."
        )


def validar_inferencia(uri, cliente):
    """Valida contrato pyfunc e flavor sklearn."""

    modelo = mlflow.pyfunc.load_model(uri)

    resultado = np.asarray(
        modelo.predict(cliente)
    ).reshape(-1)

    if resultado.size != 1:
        raise RuntimeError(
            "Predicao deveria conter apenas um cliente."
        )

    classe = int(resultado[0])

    if classe not in (0, 1):
        raise RuntimeError(
            "Classe prevista fora do intervalo [0, 1]."
        )

    sklearn_modelo = mlflow.sklearn.load_model(uri)

    probabilidades = sklearn_modelo.predict_proba(
        cliente
    )

    if probabilidades.shape != (1, 2):
        raise RuntimeError(
            "Probabilidades com formato incorreto."
        )

    probabilidade = float(
        probabilidades[0, 1]
    )

    if not 0 <= probabilidade <= 1:
        raise RuntimeError(
            "Probabilidade fora do intervalo [0, 1]."
        )

    classe_sklearn = int(
        sklearn_modelo.predict(cliente)[0]
    )

    if classe != classe_sklearn:
        raise RuntimeError(
            "Pyfunc e sklearn produziram classes diferentes."
        )

    return {
        "classe_prevista": classe,
        "classe_descricao": (
            "inadimplente" if classe == 1
            else "adimplente"
        ),
        "probabilidade_inadimplencia": probabilidade,
        "probabilidade_adimplencia": 1 - probabilidade,
    }


def executar():
    """Executa a promocao didatica da mesma versao."""

    dados = carregar_registro()

    client, tracking_uri = configurar_registry()

    versao = str(dados["version"])

    modelo = client.get_model_version(
        REGISTERED_MODEL_NAME,
        versao,
    )

    if modelo.run_id != dados["registration_run_id"]:
        raise RuntimeError(
            "Run de origem diverge da Aula 11."
        )

    candidato = client.get_model_version_by_alias(
        REGISTERED_MODEL_NAME,
        VERSAO_ALIAS,
    )

    if str(candidato.version) != versao:
        raise RuntimeError(
            "O alias candidate nao aponta para "
            "a versao registrada na Aula 11."
        )

    # Antes da promocao, protege aliases existentes.
    for alias in ("staging", "production", "champion"):
        conferir_alias(client, alias, versao)

    cliente = novo_cliente()

    print("\n===== 1. PROMOVENDO PARA STAGING =====")

    atribuir_alias(
        client,
        "staging",
        versao,
    )

    client.set_model_version_tag(
        REGISTERED_MODEL_NAME,
        versao,
        "lifecycle_status",
        "staging",
    )

    client.set_model_version_tag(
        REGISTERED_MODEL_NAME,
        versao,
        "validation_status",
        "pending_business_validation",
    )

    client.set_model_version_tag(
        REGISTERED_MODEL_NAME,
        versao,
        "deployment_scope",
        "local_educational_only",
    )

    staging_uri = (
        f"models:/{REGISTERED_MODEL_NAME}@staging"
    )

    print("URI:", staging_uri)

    staging = validar_inferencia(
        staging_uri,
        cliente,
    )

    print("CLASSE:", staging["classe_prevista"])
    print(
        "PROBABILIDADE:",
        f"{staging['probabilidade_inadimplencia']:.4f}",
    )

    print("\n===== 2. PROMOCAO DIDATICA PARA PRODUCTION =====")

    # Esta etapa representa uma aprovacao simulada,
    # nao uma validacao real de negocio.
    atribuir_alias(
        client,
        "production",
        versao,
    )

    atribuir_alias(
        client,
        "champion",
        versao,
    )

    client.set_model_version_tag(
        REGISTERED_MODEL_NAME,
        versao,
        "lifecycle_status",
        "production",
    )

    client.set_model_version_tag(
        REGISTERED_MODEL_NAME,
        versao,
        "validation_status",
        "approved_for_production",
    )

    client.set_model_version_tag(
        REGISTERED_MODEL_NAME,
        versao,
        "approval_type",
        "simulated_course_exercise",
    )

    client.set_model_version_tag(
        REGISTERED_MODEL_NAME,
        versao,
        "archive_policy",
        "keep_until_replaced_by_new_champion",
    )

    production_uri = (
        f"models:/{REGISTERED_MODEL_NAME}@production"
    )

    production = validar_inferencia(
        production_uri,
        cliente,
    )

    if staging["classe_prevista"] != production["classe_prevista"]:
        raise RuntimeError(
            "Predicoes de staging e production divergem."
        )

    if not np.isclose(
        staging["probabilidade_inadimplencia"],
        production["probabilidade_inadimplencia"],
        rtol=0,
        atol=1e-10,
    ):
        raise RuntimeError(
            "Probabilidades de staging e production divergem."
        )

    # Auditoria final do Registry.
    for alias in (
        "candidate",
        "staging",
        "production",
        "champion",
    ):
        atual = client.get_model_version_by_alias(
            REGISTERED_MODEL_NAME,
            alias,
        )

        if str(atual.version) != versao:
            raise RuntimeError(
                f"Alias {alias} divergente."
            )

    registro_final = client.get_model_version(
        REGISTERED_MODEL_NAME,
        versao,
    )

    if registro_final.tags.get("lifecycle_status") != "production":
        raise RuntimeError(
            "Lifecycle nao foi atualizado."
        )

    # Persistencia local.
    RESULTADOS.mkdir(
        parents=True,
        exist_ok=True,
    )

    tabela = cliente.copy()

    tabela["classe_prevista"] = production[
        "classe_prevista"
    ]

    tabela["probabilidade_inadimplencia"] = (
        production["probabilidade_inadimplencia"]
    )

    tabela.to_csv(
        PREVISOES,
        index=False,
        encoding="utf-8-sig",
    )

    relatorio = {
        "aula_local": 12,
        "registered_model_name": REGISTERED_MODEL_NAME,
        "version": versao,
        "registration_run_id": modelo.run_id,
        "tracking_uri": tracking_uri,
        "staging_uri": staging_uri,
        "production_uri": production_uri,
        "aliases_validados": [
            "candidate",
            "staging",
            "production",
            "champion",
        ],
        "validation_status": "approved_for_production",
        "approval_type": "simulated_course_exercise",
        "deployment_scope": "local_educational_only",
        "staging_prediction": staging,
        "production_prediction": production,
        "rollback_executado": False,
        "novas_runs": 0,
        "novas_versoes": 0,
        "treinamentos": 0,
        "ambiente_real_de_producao": False,
    }

    SAIDA.write_text(
        json.dumps(
            relatorio,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    RELATORIO.write_text(
        f"""# Aula 12 - Promocao de modelos

## Modelo
{REGISTERED_MODEL_NAME}

## Versao
{versao}

## Aliases
- candidate
- staging
- production
- champion

## Staging
{staging_uri}

## Production
{production_uri}

## Cliente sintetico
Idade: 34
Renda mensal: R$ 4200
Tempo de emprego: 5 anos
Score interno: 620
Valor solicitado: R$ 12000
Parcelas: 24
Renda: CLT
Restricao: nao

## Predicao
Classe: {production['classe_prevista']}
Probabilidade inadimplencia:
{production['probabilidade_inadimplencia']:.4%}

## Rollback
Para reverter um alias, primeiro identificar
uma versao anterior aprovada e executar:

client.set_registered_model_alias(
    name=REGISTERED_MODEL_NAME,
    alias="production",
    version="VERSAO_ANTERIOR_APROVADA",
)

Nao executar rollback para uma versao inexistente.

## Governanca
Promocao exclusivamente didatica.
Nenhuma validacao real de negocio foi realizada.
Nao utilizar para decidir credito real.
""",
        encoding="utf-8",
    )

    print("\n===== MODEL REGISTRY VALIDADO =====")
    print("MODELO:", REGISTERED_MODEL_NAME)
    print("VERSAO:", versao)
    print("RUN:", modelo.run_id)
    print("SOURCE:", modelo.source)

    print("\n===== INFERENCIA PRODUCTION =====")
    print("URI:", production_uri)
    print("CLASSE:", production["classe_prevista"])
    print("DESCRICAO:", production["classe_descricao"])
    print(
        "PROBABILIDADE INADIMPLENCIA:",
        f"{production['probabilidade_inadimplencia']:.2%}",
    )

    print("\n===== PROMOCAO CONCLUIDA =====")
    print("STAGING: VALIDADO")
    print("PRODUCTION: SIMULADA LOCALMENTE")
    print("CHAMPION: VALIDADO")
    print("ROLLBACK: DOCUMENTADO")
    print("NOVAS RUNS: 0")
    print("NOVAS VERSOES: 0")
    print("NOVOS TREINAMENTOS: 0")

    return relatorio


if __name__ == "__main__":
    executar()
