# Aula 19 — Retries, falhas e notificações

Pipelines:
- pipeline_vendas
- pipeline_cotacao

Configurações:
- retries = 1
- retry_delay = 1 minuto
- on_failure_callback = notificar_falha

Helper:
helpers/callbacks.py

Comportamento:
1. Uma tarefa falha.
2. Airflow aguarda um minuto.
3. Airflow realiza uma nova tentativa.
4. Se a tarefa falhar novamente, executa o callback.
5. O callback registra o erro.
6. Se SMTP e email_alertas estiverem configurados, tenta enviar e-mail.

Configuração SMTP:
Pendente de credenciais fornecidas pelo usuário.

Não remover Variables ou Connections existentes para testar falhas.

Agendamento diário da DAG de vendas preservado.
FileSensor e XCom preservados.
