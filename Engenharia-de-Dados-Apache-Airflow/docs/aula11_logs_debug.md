# Aula 11 — Lendo logs e debugando erros

## Pipeline
pipeline_vendas

## Tarefas
1. extrair_vendas
2. transformar_vendas
3. carregar_resumo

## Simulacao de falha

Codigo correto:
    df["valor_total"] = df["quantidade"] * df["valor_unitario"]

Codigo com erro intencional:
    df["valor_total"] = df["invalido"] * df["valor_unitario"]

Erro esperado:
    KeyError: 'invalido'

## Como investigar
1. Abrir a DAG pipeline_vendas no Airflow.
2. Acessar Grid.
3. Selecionar a execucao e a tarefa transformar_vendas.
4. Abrir Logs.
5. Identificar o erro e sua origem.
6. Restaurar o codigo correto.
7. Limpar o estado da tarefa para reexecuta-la.
8. Confirmar success e verificar o arquivo de saida.

## Conceitos
- queued: aguardando execucao
- running: executando
- success: sucesso
- failed: falha definitiva
- up_for_retry: aguardando nova tentativa

## Cuidados
- Nao marcar success manualmente para esconder erros.
- Nao reexecutar todo o pipeline se apenas uma tarefa precisa ser recuperada.
- Preservar os arquivos originais.
