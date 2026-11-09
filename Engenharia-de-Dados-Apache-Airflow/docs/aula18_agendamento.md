# Aula 18 — Agendamento dos pipelines

DAG: pipeline_vendas
Schedule: 0 7 * * *
Fuso: America/Bahia
Catchup: False

Execucao programada:
Todos os dias as 07:00, horario de Salvador.

FileSensor:
Connection: fs_default
Intervalo: 60 segundos
Timeout: 3 horas
Modo: reschedule

Data de referencia dos arquivos:
dag_run.run_after

Fluxo:
aguardar_arquivo_vendas
extrair_vendas
transformar_vendas
carregar_resumo

As Variables e o XCom foram preservados.

A confirmacao do proximo agendamento no scheduler
ainda deve ser realizada.
