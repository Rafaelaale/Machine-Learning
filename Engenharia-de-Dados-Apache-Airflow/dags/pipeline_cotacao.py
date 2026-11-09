from helpers.callbacks import notificar_falha
"""DAG de cotacao USD-BRL com historico dos ultimos sete dias."""

from datetime import datetime, timedelta

from airflow.decorators import dag, task

import helpers.cotacao as cotacao_helper
from airflow.sdk import Variable, Connection


URL_API = None  # configurada por Connection: awesomeapi_http

PASTA_RAW = None  # configurado por Variable: cotacao_pasta_raw

CAMINHO_CONSOLIDADO = None  # configurado por Variable: cotacao_caminho_consolidado

ARGS_PADRAO = {
    "on_failure_callback": notificar_falha,
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
}


@dag(
    dag_id="pipeline_cotacao",
    description="Busca cotacao USD-BRL e consolida historico de 7 dias.",
    start_date=datetime(2025, 1, 14),
    schedule=None,
    catchup=False,
    default_args=ARGS_PADRAO,
    tags=["cotacao", "financeiro"],
)
def pipeline_cotacao():

    @task()
    def buscar_e_salvar_cotacao():
        """Consulta a API e salva o JSON bruto."""
        cotacao = cotacao_helper.buscar_cotacao(f"{Connection.get('awesomeapi_http').schema}://{Connection.get('awesomeapi_http').host}/last/USD-BRL")
        cotacao_helper.salvar_json_bruto(cotacao, Variable.get("cotacao_pasta_raw"))

    @task()
    def consolidar():
        """Consolida os JSONs dos ultimos sete dias."""
        cotacao_helper.consolidar_historico(
            Variable.get("cotacao_pasta_raw"),
            Variable.get("cotacao_caminho_consolidado"),
        )

    buscar_e_salvar_cotacao() >> consolidar()


pipeline_cotacao()
