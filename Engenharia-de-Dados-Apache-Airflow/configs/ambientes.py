"""Configuracoes por ambiente do projeto Vende+."""

import os


CONFIGS = {
    "dev": {
        "pasta_input": "/opt/airflow/data/input",
        "pasta_output": "/opt/airflow/data/output",
        "pasta_cotacao_raw": "/opt/airflow/data/cotacao/raw",
        "pasta_cotacao_consolidated": "/opt/airflow/data/cotacao/consolidated",
        "url_cotacao": "https://economia.awesomeapi.com.br/json/daily/USD-BRL/7",
    },
    "prod": {
        "pasta_input": "/data/vendemais/input",
        "pasta_output": "/data/vendemais/output",
        "pasta_cotacao_raw": "/data/vendemais/cotacao/raw",
        "pasta_cotacao_consolidated": "/data/vendemais/cotacao/consolidated",
        "url_cotacao": "https://economia.awesomeapi.com.br/json/daily/USD-BRL/7",
    },
}


def get_config() -> dict:
    """Retorna as configuracoes do ambiente selecionado por ENV."""
    ambiente = os.getenv("ENV", "dev").lower()

    if ambiente not in CONFIGS:
        raise ValueError(f"Ambiente desconhecido: {ambiente}")

    return CONFIGS[ambiente].copy()