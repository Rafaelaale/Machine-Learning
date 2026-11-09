# Aula 15 — XCom

Erro identificado:
KeyError: 'ds'

Causa:
A tarefa tentou acessar context["ds"], mas essa chave não estava
disponível no contexto da execução.

Correção:
Utilizar context["dag_run"].run_after.strftime("%Y-%m-%d")
nas três tarefas para identificar a data da execução.

XCom:
A tarefa extrair_vendas retorna um dicionário com o caminho
do arquivo e a quantidade de linhas.

A tarefa carregar_resumo recebe esses metadados e deve
registrar a quantidade de linhas processadas.

Validação:
CSV de entrada confirmado com 80 linhas.
Execução completa ainda pendente de confirmação.
