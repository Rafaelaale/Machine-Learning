"""Aula 16: smoke test HTTP do serving Docker do MLflow."""

import json
import math
from pathlib import Path
import requests

from src.aula04_primeira_run_mlflow import RAIZ

API = "http://127.0.0.1:5002"
PASTA = RAIZ / "resultados" / "aula16_docker"
RELATORIO = RAIZ / "resultados" / "aula16_docker_smoke.json"
PREVISOES = PASTA / "predicoes_docker.json"
RESUMO = PASTA / "relatorio_docker.md"

COLUMNS = [
    "idade", "renda_mensal", "tempo_emprego_anos",
    "score_interno", "valor_solicitado", "num_parcelas",
    "tipo_renda", "possui_restricao"
]
VALUES = [34, 4200.0, 5.0, 620, 12000.0, 24, "CLT", "nao"]
FIELDS = {
    "probabilidade_inadimplencia",
    "classe_prevista",
    "limiar_utilizado",
}


def payload(threshold=0.3, omit=None):
    if not math.isfinite(float(threshold)) or not 0 <= float(threshold) <= 1:
        raise ValueError("Threshold invalido.")
    columns = COLUMNS.copy()
    values = VALUES.copy()
    if omit is not None:
        index = columns.index(omit)
        columns.pop(index)
        values.pop(index)
    return {
        "dataframe_split": {"columns": columns, "data": [values]},
        "params": {"threshold": float(threshold)},
    }


def health():
    """Ping obrigatorio; health/version podem nao existir."""
    result = {}
    for path in ("ping", "health", "version"):
        r = requests.get(f"{API}/{path}", timeout=15)
        if path == "ping":
            r.raise_for_status()
        elif r.status_code != 404:
            r.raise_for_status()
        result[path] = r.status_code
    return result


def predict(threshold):
    response = requests.post(
        f"{API}/invocations",
        json=payload(threshold),
        timeout=45,
    )
    response.raise_for_status()
    body = response.json()
    predictions = body.get("predictions")
    if not isinstance(predictions, list) or len(predictions) != 1:
        raise AssertionError("Resposta precisa conter uma predicao.")
    item = predictions[0]
    if not isinstance(item, dict) or not FIELDS.issubset(item):
        raise AssertionError("Contrato de resposta incompleto.")
    probability = float(item["probabilidade_inadimplencia"])
    classe = int(item["classe_prevista"])
    returned_threshold = float(item["limiar_utilizado"])
    if not math.isfinite(probability) or not 0 <= probability <= 1:
        raise AssertionError("Probabilidade invalida.")
    if classe not in (0, 1):
        raise AssertionError("Classe invalida.")
    if abs(returned_threshold - threshold) > 1e-9:
        raise AssertionError("Threshold retornado incorreto.")
    if classe != int(probability >= threshold):
        raise AssertionError("Classe incompativel com o threshold.")
    return {
        "probabilidade_inadimplencia": probability,
        "classe_prevista": classe,
        "limiar_utilizado": returned_threshold,
    }


def invalid_input():
    r = requests.post(
        f"{API}/invocations",
        json=payload(0.3, omit="score_interno"),
        timeout=45,
    )
    if not 400 <= r.status_code < 500:
        raise AssertionError(f"Esperado HTTP 4xx; recebido {r.status_code}.")
    if "score_interno" not in r.text:
        raise AssertionError("Erro nao informa a coluna score_interno.")
    return {"http_status": r.status_code, "column": "score_interno"}


def executar():
    checks = health()
    preds = [predict(t) for t in (0.3, 0.4, 0.5)]
    invalid = invalid_input()

    if any(
        abs(item["probabilidade_inadimplencia"]
            - preds[0]["probabilidade_inadimplencia"]) > 1e-10
        for item in preds
    ):
        raise AssertionError("Probabilidade mudou entre thresholds.")

    # Compara Docker com o serving local da Aula 15, quando ativo.
    comparison = "not_checked"
    try:
        r = requests.post(
            "http://127.0.0.1:5001/invocations",
            json=payload(0.3),
            timeout=15,
        )
        r.raise_for_status()
        local = r.json()["predictions"][0]
        if abs(
            float(local["probabilidade_inadimplencia"])
            - preds[0]["probabilidade_inadimplencia"]
        ) > 1e-10:
            raise AssertionError("Docker divergiu do serving local.")
        comparison = "matching"
    except requests.RequestException:
        comparison = "local_server_unavailable"

    result = {
        "aula": 16,
        "api": API,
        "model": "risco_credito_classifier_pyfunc",
        "alias": "servingCandidate",
        "health": checks,
        "predictions": preds,
        "invalid_payload": invalid,
        "local_comparison": comparison,
        "new_runs": 0,
        "new_model_versions": 0,
        "new_trainings": 0,
    }

    PASTA.mkdir(parents=True, exist_ok=True)
    RELATORIO.write_text(
        json.dumps(result, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    PREVISOES.write_text(
        json.dumps(preds, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    RESUMO.write_text(
        "# Aula 16 - Docker e smoke tests\n\n"
        "Imagem: risco-credito-serving:latest\n\n"
        "Container: risco-credito-api\n\n"
        "Portas: 5002:8080\n\n"
        f"Health checks: {checks}\n\n"
        f"Payload invalido: HTTP {invalid['http_status']}\n\n"
        f"Comparacao com serving local: {comparison}\n\n"
        "Somente demonstracao educacional com dados sinteticos.\n",
        encoding="utf-8",
    )

    print("\n===== SMOKE TEST DOCKER =====")
    for name, status in checks.items():
        print(name.upper(), "HTTP", status)
    for item in preds:
        print(
            "THRESHOLD", item["limiar_utilizado"],
            "PROBABILIDADE", round(item["probabilidade_inadimplencia"], 6),
            "CLASSE", item["classe_prevista"],
        )
    print("PAYLOAD INVALIDO: HTTP", invalid["http_status"])
    print("COMPARACAO LOCAL:", comparison)
    print("SMOKE TEST PASSOU")
    return result


if __name__ == "__main__":
    executar()
