"""Aula 15 - Serving REST do PyFunc personalizado.

Consulta o modelo registrado da Aula 14.
Realiza testes HTTP de saude, predicao e erros.
Nao cria runs, versoes ou treinamentos.
"""

import json
from pathlib import Path

import mlflow
import mlflow.pyfunc
import numpy as np
import pandas as pd
import requests

from src.aula04_primeira_run_mlflow import RAIZ


TRACKING_URI = "http://127.0.0.1:5000"
BASE_URL = "http://127.0.0.1:5001"
MODEL_URI = (
    "models:/risco_credito_classifier_pyfunc"
    "@servingCandidate"
)

PASTA = RAIZ / "resultados" / "aula15_serving"

RELATORIO_JSON = (
    RAIZ / "resultados" / "aula15_serving_rest.json"
)

RESPOSTAS_JSON = PASTA / "respostas_http.json"
PREVISOES_CSV = PASTA / "previsoes_thresholds.csv"
RELATORIO_MD = PASTA / "relatorio_serving.md"
PAYLOAD_JSON = PASTA / "payload_valido.json"
PAYLOAD_INVALIDO_JSON = PASTA / "payload_invalido.json"

COLUNAS = [
    "idade",
    "renda_mensal",
    "tempo_emprego_anos",
    "score_interno",
    "valor_solicitado",
    "num_parcelas",
    "tipo_renda",
    "possui_restricao",
]

VALORES = [
    34,
    4200.0,
    5.0,
    620,
    12000.0,
    24,
    "CLT",
    "nao",
]

CAMPOS_RESPOSTA = [
    "probabilidade_inadimplencia",
    "classe_prevista",
    "limiar_utilizado",
]


def criar_payload(threshold=0.30, remover_coluna=None):
    """Cria JSON de inferencia no formato dataframe_split."""

    if not 0 <= float(threshold) <= 1:
        raise ValueError(
            "Threshold deve estar entre 0 e 1."
        )

    colunas = list(COLUNAS)
    valores = list(VALORES)

    if remover_coluna is not None:
        if remover_coluna not in colunas:
            raise ValueError(
                f"Coluna desconhecida: {remover_coluna}"
            )

        indice = colunas.index(remover_coluna)

        colunas.pop(indice)
        valores.pop(indice)

    return {
        "dataframe_split": {
            "columns": colunas,
            "data": [valores],
        },
        "params": {
            "threshold": float(threshold),
        },
    }


def verificar_health():
    """Consulta os endpoints auxiliares do servidor."""

    resultados = {}

    for endpoint in ("ping", "health", "version"):
        resposta = requests.get(
            f"{BASE_URL}/{endpoint}",
            timeout=15,
        )

        resposta.raise_for_status()

        resultados[endpoint] = {
            "status_code": resposta.status_code,
            "body": resposta.text.strip()[:500],
        }

    return resultados


def chamar_api(payload):
    """Envia uma requisicao real ao endpoint invocations."""

    resposta = requests.post(
        f"{BASE_URL}/invocations",
        json=payload,
        headers={
            "Content-Type": "application/json",
        },
        timeout=60,
    )

    try:
        corpo = resposta.json()
    except ValueError:
        corpo = {
            "raw_response": resposta.text[:2000]
        }

    return {
        "status_code": resposta.status_code,
        "body": corpo,
    }


def extrair_predicao(resposta):
    """Normaliza a saida JSON produzida pelo MLflow."""

    if resposta["status_code"] != 200:
        raise RuntimeError(
            f"HTTP {resposta['status_code']}: "
            f"{resposta['body']}"
        )

    corpo = resposta["body"]

    if not isinstance(corpo, dict):
        raise RuntimeError(
            "Resposta nao possui estrutura JSON esperada."
        )

    previsoes = corpo.get("predictions")

    if not isinstance(previsoes, list):
        raise RuntimeError(
            "Campo predictions ausente ou invalido."
        )

    if len(previsoes) != 1:
        raise RuntimeError(
            "Era esperada uma unica predicao."
        )

    linha = previsoes[0]

    if not isinstance(linha, dict):
        raise RuntimeError(
            "Predicao nao e um objeto JSON."
        )

    faltantes = [
        campo
        for campo in CAMPOS_RESPOSTA
        if campo not in linha
    ]

    if faltantes:
        raise RuntimeError(
            f"Campos ausentes: {faltantes}"
        )

    resultado = {
        "probabilidade_inadimplencia": float(
            linha["probabilidade_inadimplencia"]
        ),
        "classe_prevista": int(
            linha["classe_prevista"]
        ),
        "limiar_utilizado": float(
            linha["limiar_utilizado"]
        ),
    }

    probabilidade = resultado[
        "probabilidade_inadimplencia"
    ]

    limiar = resultado["limiar_utilizado"]

    if not (
        np.isfinite(probabilidade)
        and 0 <= probabilidade <= 1
    ):
        raise RuntimeError(
            "Probabilidade retornada e invalida."
        )

    if not (
        np.isfinite(limiar)
        and 0 <= limiar <= 1
    ):
        raise RuntimeError(
            "Limiar retornado e invalido."
        )

    classe_esperada = int(
        probabilidade >= limiar
    )

    if resultado["classe_prevista"] != classe_esperada:
        raise RuntimeError(
            "Classe diferente da regra de threshold."
        )

    return resultado


def conferir_modelo_registrado():
    """Garante que o servidor aponta ao Registry correto."""

    mlflow.set_tracking_uri(TRACKING_URI)
    mlflow.set_registry_uri(TRACKING_URI)

    from mlflow.tracking import MlflowClient

    client = MlflowClient()

    alias = client.get_model_version_by_alias(
        "risco_credito_classifier_pyfunc",
        "servingCandidate",
    )

    anterior = json.loads(
        (
            RAIZ
            / "resultados"
            / "aula14_pyfunc_personalizado.json"
        ).read_text(encoding="utf-8")
    )

    if str(alias.version) != str(anterior["version"]):
        raise RuntimeError(
            "Alias servingCandidate nao corresponde "
            "ao modelo registrado na Aula 14."
        )

    if alias.run_id != anterior["run_id"]:
        raise RuntimeError(
            "Run do modelo registrado divergente."
        )

    return {
        "version": str(alias.version),
        "run_id": alias.run_id,
    }


def conferir_contra_modelo_local(previsoes):
    """Compara a API ao proprio modelo MLflow."""

    modelo = mlflow.pyfunc.load_model(
        MODEL_URI
    )

    entrada = pd.DataFrame(
        [VALORES],
        columns=COLUNAS,
    )

    for item in previsoes:
        threshold = item["limiar_utilizado"]

        esperado = modelo.predict(
            entrada,
            params={"threshold": threshold},
        ).iloc[0]

        if not np.isclose(
            item["probabilidade_inadimplencia"],
            float(
                esperado["probabilidade_inadimplencia"]
            ),
            rtol=0,
            atol=1e-10,
        ):
            raise RuntimeError(
                "Predicao REST diferente do modelo MLflow."
            )

        if item["classe_prevista"] != int(
            esperado["classe_prevista"]
        ):
            raise RuntimeError(
                "Classe REST diferente da classe local."
            )


def executar():
    """Executa os testes de integracao e gera relatorios."""

    origem = conferir_modelo_registrado()

    health = verificar_health()

    respostas = {}
    previsoes = []

    for threshold in (0.30, 0.40, 0.50):
        payload = criar_payload(threshold)

        resposta = chamar_api(payload)

        predicao = extrair_predicao(
            resposta
        )

        if not np.isclose(
            predicao["limiar_utilizado"],
            threshold,
            atol=1e-12,
        ):
            raise RuntimeError(
                "Servidor nao aplicou o threshold enviado."
            )

        chave = f"threshold_{threshold:.2f}"

        respostas[chave] = resposta

        previsoes.append(predicao)

    # O mesmo cliente deve apresentar a mesma
    # probabilidade para todos os thresholds.
    probabilidades = [
        item["probabilidade_inadimplencia"]
        for item in previsoes
    ]

    if not np.allclose(
        probabilidades,
        probabilidades[0],
        atol=1e-10,
        rtol=0,
    ):
        raise RuntimeError(
            "Threshold alterou a probabilidade."
        )

    conferir_contra_modelo_local(
        previsoes
    )

    payload_invalido = criar_payload(
        threshold=0.30,
        remover_coluna="score_interno",
    )

    resposta_invalida = chamar_api(
        payload_invalido
    )

    if not 400 <= resposta_invalida["status_code"] < 500:
        raise RuntimeError(
            "Payload incompleto deveria ser "
            "rejeitado com HTTP 4xx. "
            f"Recebido: {resposta_invalida['status_code']}"
        )

    mensagem_erro = json.dumps(
        resposta_invalida["body"],
        ensure_ascii=False,
    )

    if "score_interno" not in mensagem_erro:
        raise RuntimeError(
            "Resposta de erro nao identifica "
            "a coluna ausente score_interno."
        )

    PASTA.mkdir(
        parents=True,
        exist_ok=True,
    )

    PAYLOAD_JSON.write_text(
        json.dumps(
            criar_payload(0.30),
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    PAYLOAD_INVALIDO_JSON.write_text(
        json.dumps(
            payload_invalido,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    respostas["payload_invalido"] = resposta_invalida

    RESPOSTAS_JSON.write_text(
        json.dumps(
            respostas,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    tabela = pd.DataFrame(
        previsoes
    )

    tabela.to_csv(
        PREVISOES_CSV,
        index=False,
        encoding="utf-8-sig",
    )

    resultado = {
        "aula_local": 15,
        "tracking_uri": TRACKING_URI,
        "serving_url": BASE_URL,
        "model_uri": MODEL_URI,
        "model_version": origem["version"],
        "model_run_id": origem["run_id"],
        "health": health,
        "thresholds": [0.30, 0.40, 0.50],
        "previsoes": previsoes,
        "erro_status_code": resposta_invalida[
            "status_code"
        ],
        "erro_coluna_identificada": True,
        "predicoes_conferidas_com_modelo": True,
        "novas_runs": 0,
        "novas_versoes": 0,
        "novos_treinamentos": 0,
    }

    RELATORIO_JSON.write_text(
        json.dumps(
            resultado,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    linhas = []

    for item in previsoes:
        linhas.append(
            f"| {item['limiar_utilizado']:.2f} "
            f"| {item['probabilidade_inadimplencia']:.4f} "
            f"| {item['classe_prevista']} |"
        )

    RELATORIO_MD.write_text(
        f"""# Aula 15 - Serving REST

## Modelo

{MODEL_URI}

Versao: {origem['version']}
Run: {origem['run_id']}

## Endpoints

- GET /ping
- GET /health
- GET /version
- POST /invocations

## Comparacao de thresholds

| Threshold | Probabilidade | Classe |
|---|---|---|
{chr(10).join(linhas)}

## Validacao HTTP

Payload valido: HTTP 200.
Payload sem score_interno: HTTP {resposta_invalida['status_code']}.

## Conferencia

Predicoes REST comparadas com o
mesmo modelo carregado localmente.

## Proxima etapa

Docker e testes automatizados do serving.

## Observacao

API local para estudos com dados sinteticos.
Nao autorizada para decisoes reais de credito.
""",
        encoding="utf-8",
    )

    print("\n===== HEALTH CHECKS =====")

    for endpoint, info in health.items():
        print(
            endpoint.upper(),
            "HTTP",
            info["status_code"],
        )

    print("\n===== PREDICOES HTTP =====")

    for item in previsoes:
        print(
            "THRESHOLD:",
            f"{item['limiar_utilizado']:.2f}",
            "PROBABILIDADE:",
            f"{item['probabilidade_inadimplencia']:.4f}",
            "CLASSE:",
            item["classe_prevista"],
        )

    print("\n===== PAYLOAD INVALIDO =====")
    print(
        "HTTP:",
        resposta_invalida["status_code"]
    )
    print(
        "COLUNA score_interno: IDENTIFICADA"
    )

    print("\n===== SERVING REST VALIDADO =====")
    print("MODELO:", MODEL_URI)
    print("VERSAO:", origem["version"])
    print("HTTP E MODELO LOCAL: CONSISTENTES")
    print("NOVAS RUNS: 0")
    print("NOVAS VERSOES: 0")
    print("NOVOS TREINAMENTOS: 0")

    return resultado


if __name__ == "__main__":
    executar()
