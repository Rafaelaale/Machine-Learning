"""Aula 14 - Contrato personalizado de inferencia.

Reutiliza o classificador registrado na Aula 11.
Nao treina um novo algoritmo.
Cria um segundo registered model para serving.
"""

import json
from pathlib import Path

import mlflow
import mlflow.artifacts
import mlflow.pyfunc
import mlflow.sklearn
import numpy as np
import pandas as pd

from mlflow.models import infer_signature
from mlflow.tracking import MlflowClient

from src.aula04_primeira_run_mlflow import (
    RAIZ,
    FEATURES,
    carregar_dados,
)
from src.aula11_model_registry import (
    configurar_registry,
)
from src.aula12_promovendo_modelos import (
    novo_cliente,
)


SOURCE_MODEL_NAME = "risco_credito_classifier"
SOURCE_URI = f"models:/{SOURCE_MODEL_NAME}@production"

EXPERIMENT_NAME = "risco_credito_07_mlflow_models"
RUN_NAME = "aula07_pyfunc_credit_risk_contract"
PYFUNC_MODEL_NAME = "risco_credito_classifier_pyfunc"

ARQUIVO_RESULTADO = (
    RAIZ / "resultados" / "aula14_pyfunc_personalizado.json"
)

ARQUIVO_PREVISOES = (
    RAIZ / "resultados" / "aula14_previsoes_pyfunc.csv"
)

ARQUIVO_RELATORIO = (
    RAIZ / "anotacoes" / "aula14_resultado_pyfunc.md"
)


class CreditRiskPyfuncModel(mlflow.pyfunc.PythonModel):
    """Modelo com resposta tabular e limiar configuravel."""

    def __init__(
        self,
        required_columns,
        default_threshold=0.5,
    ):
        self.required_columns = list(required_columns)
        self.default_threshold = float(default_threshold)
        self.sklearn_model = None

    def load_context(self, context):
        """Carrega o pipeline da pasta de artefatos."""

        caminho = context.artifacts["sklearn_model"]

        self.sklearn_model = mlflow.sklearn.load_model(
            caminho
        )

    def predict(self, context, model_input, params=None):
        """Retorna probabilidade, classe e limiar."""

        if not isinstance(model_input, pd.DataFrame):
            model_input = pd.DataFrame(model_input)

        faltantes = [
            coluna
            for coluna in self.required_columns
            if coluna not in model_input.columns
        ]

        if faltantes:
            raise ValueError(
                "Colunas obrigatorias ausentes: "
                + str(faltantes)
            )

        threshold = self.default_threshold

        if params is not None and "threshold" in params:
            threshold = float(params["threshold"])

        if not np.isfinite(threshold):
            raise ValueError(
                "Threshold precisa ser um numero finito."
            )

        if not 0 <= threshold <= 1:
            raise ValueError(
                "Threshold deve estar entre 0 e 1."
            )

        if self.sklearn_model is None:
            raise RuntimeError(
                "Modelo base ainda nao foi carregado."
            )

        X = model_input[
            self.required_columns
        ].copy()

        probabilidades = (
            self.sklearn_model.predict_proba(X)[:, 1]
        )

        classes = (
            probabilidades >= threshold
        ).astype(int)

        return pd.DataFrame({
            "probabilidade_inadimplencia": (
                probabilidades.astype(float)
            ),
            "classe_prevista": classes,
            "limiar_utilizado": np.repeat(
                threshold, len(X)
            ),
        })


def configurar():
    """Mantem o mesmo backend SQLite das aulas."""

    client, tracking_uri = configurar_registry()

    mlflow.set_experiment(EXPERIMENT_NAME)

    return client, tracking_uri


def conferir_origem(client):
    """Confere se o modelo base segue na versao 1."""

    anterior = json.loads(
        (
            RAIZ / "resultados"
            / "aula11_model_registry.json"
        ).read_text(encoding="utf-8")
    )

    origem = client.get_model_version_by_alias(
        SOURCE_MODEL_NAME,
        "production",
    )

    if str(origem.version) != str(anterior["version"]):
        raise RuntimeError(
            "Alias production foi alterado."
        )

    if origem.run_id != anterior["registration_run_id"]:
        raise RuntimeError(
            "Run de origem nao corresponde a Aula 11."
        )

    return origem


def testar_wrapper_local():
    """Valida a logica antes de registrar."""

    wrapper = CreditRiskPyfuncModel(
        required_columns=FEATURES,
        default_threshold=0.5,
    )

    wrapper.sklearn_model = mlflow.sklearn.load_model(
        SOURCE_URI
    )

    (
        _,
        X_train,
        _,
        _,
        _,
    ) = carregar_dados()

    entrada = X_train.head(5).copy()

    saida = wrapper.predict(
        context=None,
        model_input=entrada,
    )

    if list(saida.columns) != [
        "probabilidade_inadimplencia",
        "classe_prevista",
        "limiar_utilizado",
    ]:
        raise RuntimeError(
            "Contrato de saida incorreto."
        )

    if len(saida) != 5:
        raise RuntimeError(
            "Esperadas cinco previsoes."
        )

    return entrada, saida


def buscar_versao_existente(client, source_run_id):
    """Evita gerar versoes duplicadas."""

    try:
        versoes = client.search_model_versions(
            f"name = '{PYFUNC_MODEL_NAME}'"
        )
    except Exception as exc:
        from mlflow.exceptions import MlflowException

        if (
            isinstance(exc, MlflowException)
            and "not found" in str(exc).lower()
        ):
            return None

        raise

    validas = []

    for versao in versoes:
        if not versao.run_id:
            continue

        run = client.get_run(versao.run_id)

        if (
            run.info.status == "FINISHED"
            and run.data.tags.get("run_purpose")
                == "custom_inference_contract"
            and run.data.params.get("source_model_run_id")
                == source_run_id
        ):
            validas.append(versao)

    if not validas:
        return None

    return max(
        validas,
        key=lambda item: int(item.version),
    )


def registrar_modelo(client, origem, entrada, saida):
    """Cria uma run nova e um modelo PyFunc separado."""

    diretorio = mlflow.artifacts.download_artifacts(
        artifact_uri=SOURCE_URI
    )

    signature = infer_signature(
        entrada,
        saida,
        params={"threshold": 0.5},
    )

    mlflow.sklearn.autolog(disable=True)

    with mlflow.start_run(
        run_name=RUN_NAME
    ) as run:

        mlflow.log_params({
            "source_model_uri": SOURCE_URI,
            "source_model_run_id": origem.run_id,
            "default_threshold": 0.5,
            "output_format": "probability_label_threshold",
            "registered_model_name": PYFUNC_MODEL_NAME,
        })

        mlflow.set_tags({
            "project": "risco_credito",
            "course_lesson": "aula_07",
            "model_interface": "custom_pyfunc",
            "run_purpose": "custom_inference_contract",
            "source_model_version": str(origem.version),
        })

        # O artefato base ja foi gerado na Aula 11.
        # A nova run apenas empacota sua inferencia.
        info = mlflow.pyfunc.log_model(
            name="credit_risk_pyfunc",
            python_model=CreditRiskPyfuncModel(
                required_columns=FEATURES,
                default_threshold=0.5,
            ),
            artifacts={
                "sklearn_model": str(diretorio),
            },
            signature=signature,
            input_example=entrada,
            registered_model_name=PYFUNC_MODEL_NAME,
            code_paths=[str(RAIZ / "src")],
        )

        novo_run_id = run.info.run_id

    return novo_run_id, info.model_uri


def configurar_aliases(client, versao):
    """Prepara aliases sem mudar production."""

    for alias in ("candidate", "servingCandidate"):
        try:
            anterior = client.get_model_version_by_alias(
                PYFUNC_MODEL_NAME,
                alias,
            )

        except Exception as exc:
            from mlflow.exceptions import MlflowException

            if (
                isinstance(exc, MlflowException)
                and "not found" in str(exc).lower()
            ):
                anterior = None
            else:
                raise

        if (
            anterior is not None
            and str(anterior.version) != str(versao.version)
        ):
            raise RuntimeError(
                f"Alias {alias} aponta para outra versao."
            )

        client.set_registered_model_alias(
            name=PYFUNC_MODEL_NAME,
            alias=alias,
            version=versao.version,
        )

    client.set_registered_model_tag(
        PYFUNC_MODEL_NAME,
        "project",
        "risco_credito",
    )

    client.set_registered_model_tag(
        PYFUNC_MODEL_NAME,
        "task",
        "binary_classification",
    )

    client.set_model_version_tag(
        PYFUNC_MODEL_NAME,
        versao.version,
        "lifecycle_status",
        "candidate",
    )

    client.set_model_version_tag(
        PYFUNC_MODEL_NAME,
        versao.version,
        "interface",
        "probability_label_threshold",
    )


def testar_registrado(model_uri):
    """Confere inferencia pelo Registry e seus parametros."""

    modelo = mlflow.pyfunc.load_model(
        model_uri
    )

    cliente = novo_cliente()

    padrao = modelo.predict(
        cliente
    )

    ajustado = modelo.predict(
        cliente,
        params={"threshold": 0.30},
    )

    if len(padrao) != 1 or len(ajustado) != 1:
        raise RuntimeError(
            "Quantidade incorreta de previsoes."
        )

    if not np.isclose(
        float(padrao.iloc[0]["limiar_utilizado"]),
        0.5,
    ):
        raise RuntimeError(
            "Limiar padrao incorreto."
        )

    if not np.isclose(
        float(ajustado.iloc[0]["limiar_utilizado"]),
        0.3,
    ):
        raise RuntimeError(
            "Limiar personalizado incorreto."
        )

    prob1 = float(
        padrao.iloc[0][
            "probabilidade_inadimplencia"
        ]
    )

    prob2 = float(
        ajustado.iloc[0][
            "probabilidade_inadimplencia"
        ]
    )

    if not np.isclose(
        prob1,
        prob2,
        atol=1e-12,
        rtol=0,
    ):
        raise RuntimeError(
            "Alterar threshold modificou a probabilidade."
        )

    incompleto = cliente.drop(
        columns=["score_interno"]
    )

    erro_controlado = False

    try:
        modelo.predict(incompleto)
    except Exception as exc:
        erro_controlado = (
            "score_interno" in str(exc)
        )

    if not erro_controlado:
        raise RuntimeError(
            "Entrada incompleta nao gerou erro claro."
        )

    return padrao, ajustado


def executar():
    """Registra e audita o modelo personalizado."""

    client, tracking_uri = configurar()
    origem = conferir_origem(client)

    entrada, saida = testar_wrapper_local()

    print("\n===== WRAPPER LOCAL =====")
    print(saida.to_string(index=False))

    existente = buscar_versao_existente(
        client,
        origem.run_id,
    )

    if existente is None:
        print("\n===== REGISTRANDO PYFUNC =====")

        novo_run_id, model_uri = registrar_modelo(
            client,
            origem,
            entrada,
            saida,
        )

        versoes = client.search_model_versions(
            f"name = '{PYFUNC_MODEL_NAME}'"
        )

        correspondentes = [
            versao
            for versao in versoes
            if versao.run_id == novo_run_id
        ]

        if not correspondentes:
            raise RuntimeError(
                "Versao registrada nao encontrada."
            )

        versao = max(
            correspondentes,
            key=lambda item: int(item.version),
        )
    else:
        versao = existente

        print("\nVERSAO EXISTENTE REUTILIZADA")
        print("NENHUMA VERSAO DUPLICADA")

    configurar_aliases(
        client,
        versao,
    )

    alias_uri = (
        f"models:/{PYFUNC_MODEL_NAME}@servingCandidate"
    )

    padrao, ajustado = testar_registrado(
        alias_uri
    )

    resultado = {
        "aula_local": 14,
        "registered_model_name": PYFUNC_MODEL_NAME,
        "version": str(versao.version),
        "run_id": versao.run_id,
        "source_model_uri": SOURCE_URI,
        "source_run_id": origem.run_id,
        "tracking_uri": tracking_uri,
        "model_uri": (
            f"models:/{PYFUNC_MODEL_NAME}/{versao.version}"
        ),
        "serving_alias_uri": alias_uri,
        "aliases": [
            "candidate",
            "servingCandidate",
        ],
        "output_columns": list(padrao.columns),
        "default_threshold": 0.5,
        "alternative_threshold": 0.3,
        "default_prediction": (
            padrao.iloc[0].to_dict()
        ),
        "alternative_prediction": (
            ajustado.iloc[0].to_dict()
        ),
        "invalid_column_rejected": True,
        "trained_new_algorithm": False,
        "original_production_unchanged": True,
        "production_promoted": False,
    }

    ARQUIVO_RESULTADO.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    ARQUIVO_RESULTADO.write_text(
        json.dumps(
            resultado,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    tabela = pd.concat(
        [
            padrao.assign(cenario="threshold_050"),
            ajustado.assign(cenario="threshold_030"),
        ],
        ignore_index=True,
    )

    tabela.to_csv(
        ARQUIVO_PREVISOES,
        index=False,
        encoding="utf-8-sig",
    )

    ARQUIVO_RELATORIO.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    ARQUIVO_RELATORIO.write_text(
        f"""# Aula 14 - Modelo PyFunc personalizado

## Modelo registrado

{PYFUNC_MODEL_NAME}

Versao: {versao.version}
Run: {versao.run_id}

## Modelo de origem

{SOURCE_URI}
Run de origem: {origem.run_id}

## Interface de entrada

Oito features do dataset sintetico.

## Interface de saida

- probabilidade_inadimplencia
- classe_prevista
- limiar_utilizado

## Resultado com threshold 0.50

{padrao.to_string(index=False)}

## Resultado com threshold 0.30

{ajustado.to_string(index=False)}

## URI para serving

{alias_uri}

## Seguranca e governanca

Modelo apenas didatico.
Ainda nao promovido para production.
O modelo de origem foi preservado.
""",
        encoding="utf-8",
    )

    print("\n===== PYFUNC REGISTRADO =====")
    print("MODELO:", PYFUNC_MODEL_NAME)
    print("VERSAO:", versao.version)
    print("RUN ID:", versao.run_id)
    print("SOURCE:", SOURCE_URI)
    print("ALIAS:", alias_uri)

    print("\n===== THRESHOLD 0.50 =====")
    print(padrao.to_string(index=False))

    print("\n===== THRESHOLD 0.30 =====")
    print(ajustado.to_string(index=False))

    print("\n===== VALIDACAO =====")
    print("COLUNA AUSENTE: REJEITADA")
    print("PROBABILIDADE: CONSISTENTE")
    print("MODELO BASE: PRESERVADO")
    print("NOVO ALGORITMO TREINADO: NAO")
    print("PRODUCTION PYFUNC: NAO PROMOVIDO")

    return resultado


if __name__ == "__main__":
    executar()
