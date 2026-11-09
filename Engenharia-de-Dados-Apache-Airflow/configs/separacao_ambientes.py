"""Separacao logica de ambientes do projeto Vende+."""

import os


AMBIENTES = {
    "dev": {
        "conexao_cotacao": "awesomeapi_http_dev",
        "pasta_input": "/opt/airflow/data/dev/input",
        "pasta_temp": "/opt/airflow/data/dev/temp",
        "pasta_output": "/opt/airflow/data/dev/output",
        "pasta_cotacao_raw": "/opt/airflow/data/dev/cotacao/raw",
        "pasta_cotacao_consolidated": "/opt/airflow/data/dev/cotacao/consolidated",
    },
    "prod": {
        "conexao_cotacao": "awesomeapi_http",
        "pasta_input": "/opt/airflow/data/input",
        "pasta_temp": "/opt/airflow/data/temp",
        "pasta_output": "/opt/airflow/data/output",
        "pasta_cotacao_raw": "/opt/airflow/data/cotacao/raw",
        "pasta_cotacao_consolidated": "/opt/airflow/data/cotacao/consolidated",
    },
}


def get_ambiente(nome=None):
    """Seleciona o ambiente sem alterar as DAGs existentes."""
    ambiente = (nome or os.getenv("ENV", "dev")).lower()

    if ambiente not in AMBIENTES:
        raise ValueError(f"Ambiente desconhecido: {ambiente}")

    return AMBIENTES[ambiente].copy()