"""Exemplo da transcricao - Celery.

Requer Celery e configuracao apropriada
para executar tarefas em ambiente real.
"""

from celery import shared_task


@shared_task
def enviar_email():
    print("Email enviado!")
