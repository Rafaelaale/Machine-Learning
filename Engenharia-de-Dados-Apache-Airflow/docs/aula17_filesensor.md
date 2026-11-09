# Aula 17 — FileSensor

DAG: pipeline_vendas
Sensor: aguardar_arquivo_vendas
Connection: fs_default
Variable: vendas_dir_input

Intervalo de verificacao: 60 segundos
Timeout: 3 horas
Modo: reschedule

A data do arquivo e calculada com dag_run.run_after,
mantendo o criterio das tarefas ja existentes.

Sequencia:
1. aguardar_arquivo_vendas
2. extrair_vendas
3. transformar_vendas
4. carregar_resumo

XCom da Aula 15 preservado.

Validacao funcional pendente.
