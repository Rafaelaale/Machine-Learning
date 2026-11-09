from helpers.callbacks import notificar_falha
import pendulum
from datetime import datetime, timedelta

from airflow.decorators import dag, task
import helpers.vendas as vendas_helper
from airflow.sdk import Variable
from airflow.providers.standard.sensors.filesystem import FileSensor


DIR_INPUT = None  # configurado por Variable: vendas_dir_input
DIR_TEMP = None  # configurado por Variable: vendas_dir_temp
DIR_OUTPUT = None  # configurado por Variable: vendas_dir_output


ARGS_PADRAO = {
    "on_failure_callback": notificar_falha,
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": pendulum.datetime(2025, 1, 1, tz="America/Bahia"),
    "retries": 1,
    "retry_delay": timedelta(minutes=1),

}


@dag(
    dag_id="pipeline_vendas",
    default_args=ARGS_PADRAO,
    schedule="0 7 * * *",
    catchup=False,
    tags=["vendas"],
)
def pipeline_vendas():

    @task
    def extrair_vendas(**context):
        ds = context["dag_run"].run_after.strftime("%Y-%m-%d")
        caminho = f"{Variable.get('vendas_dir_input')}/vendas_{ds}.csv"

        resultado = vendas_helper.extrair_vendas(caminho)

        print(
            f"Arquivo lido: {resultado['caminho']} "
            f"- {resultado['linhas']} linhas"
        )

        return resultado


    @task
    def transformar_vendas(**context):
        ds = context["dag_run"].run_after.strftime("%Y-%m-%d")

        caminho_entrada = f"{Variable.get('vendas_dir_input')}/vendas_{ds}.csv"
        caminho_saida = f"{Variable.get('vendas_dir_temp')}/resumo_categoria_{ds}.csv"

        vendas_helper.transformar_vendas(
            caminho_entrada,
            caminho_saida,
        )

        print(f"Resumo intermediario salvo em: {caminho_saida}")

    @task
    def carregar_resumo(metadados, **context):
        ds = context["dag_run"].run_after.strftime("%Y-%m-%d")

        caminho_transformado = (
            f"{Variable.get('vendas_dir_temp')}/resumo_categoria_{ds}.csv"
        )
        caminho_final = (
            f"{Variable.get('vendas_dir_output')}/resumo_categoria_{ds}.csv"
        )

        vendas_helper.carregar_resumo(
            caminho_transformado,
            caminho_final,
        )

        print(f"Resumo final disponivel em: {caminho_final}")
        print(f"Total de linhas processadas: {metadados['linhas']}")

    t_aguardar = FileSensor(
        task_id='aguardar_arquivo_vendas',
        fs_conn_id='fs_default',
        filepath=(
            "{{ var.value.vendas_dir_input }}/"
            "vendas_{{ dag_run.run_after.strftime('%Y-%m-%d') }}.csv"
        ),
        poke_interval=60,
        timeout=10800,
        mode='reschedule',
    )

    t_extrair = extrair_vendas()
    t_transformar = transformar_vendas()
    t_carregar = carregar_resumo(t_extrair)
    t_aguardar >> t_extrair >> t_transformar >> t_carregar


pipeline_vendas()
