import logging
from html import escape

from airflow.sdk import Variable
from airflow.utils.email import send_email

log = logging.getLogger(__name__)


def notificar_falha(context):
    """Registra falha definitiva e tenta enviar alerta por e-mail."""

    dag = context.get("dag")
    task_instance = context.get("task_instance")
    dag_run = context.get("dag_run")

    dag_id = getattr(dag, "dag_id", "desconhecida")
    task_id = getattr(task_instance, "task_id", "desconhecida")

    data_execucao = (
        getattr(dag_run, "run_after", None)
        or context.get("logical_date")
        or context.get("execution_date")
    )

    erro = context.get("exception")

    log.error(
        "FALHA DEFINITIVA | DAG=%s | TASK=%s | DATA=%s | ERRO=%s",
        dag_id,
        task_id,
        data_execucao,
        erro,
    )

    try:
        destinatario = Variable.get(
            "email_alertas",
            default=None,
        )

        if not destinatario:
            log.warning(
                "Alerta por e-mail nao enviado: "
                "Variable email_alertas ainda nao configurada."
            )
            return

        assunto = f"[Airflow] Falha em {dag_id}.{task_id}"

        corpo = f"""
        <h3>Falha detectada no pipeline Vende+</h3>
        <ul>
            <li><b>DAG:</b> {escape(str(dag_id))}</li>
            <li><b>Tarefa:</b> {escape(str(task_id))}</li>
            <li><b>Execucao:</b> {escape(str(data_execucao))}</li>
            <li><b>Erro:</b> {escape(str(erro))}</li>
        </ul>
        """

        send_email(
            to=destinatario,
            subject=assunto,
            html_content=corpo,
        )

        log.info(
            "Solicitacao de alerta enviada para %s",
            destinatario,
        )

    except Exception:
        log.exception(
            "Nao foi possivel enviar o alerta de falha."
        )