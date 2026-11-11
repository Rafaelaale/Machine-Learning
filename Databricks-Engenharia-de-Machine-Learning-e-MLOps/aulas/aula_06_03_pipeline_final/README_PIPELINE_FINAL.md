# Aula 6.3 - Pipeline Final e Codigos Produtivos

## Fonte oficial

https://github.com/alura-cursos/6123-alura-ml-databricks

Pasta:
aula_6/pipeline

## Codigos da aula

01_ingestao_dados.py
02_pre_processamento.py
03_treinamento_modelo.py
04_gerando_dados_produtivos.py
05_monitoramento_drift.py
06_re_treino.py
07_deploy_modelo.py

Os sete codigos oficiais estao em:
codigos_oficiais/

## Sequencia

1. Ingestao Bronze, Silver e Gold.
2. Pre-processamento e Feature Store.
3. Treinamento, Optuna e Champion.
4. Dados produtivos por 15 dias.
5. Monitoramento do drift.
6. Condicao booleana de retreinamento.
7. Retreinamento, quando necessario.
8. Deploy batch, incluindo processamento D-1.

Sete scripts e oito tarefas logicas.

## Cuidados para a proxima aula

Verificar referencias fixas a workspace na ingestao.

Alinhar taskKey do monitoramento com o nome
da tarefa de dados produtivos no workflow.

Verificar se a inferencia deve gerar classes
ou probabilidades.

Preservar os codigos oficiais; realizar
adaptacoes futuras em arquivos separados.

## Validacao atual

Arquivos Python: validacao estatica de sintaxe.

Dependencias: mapeadas.

TaskValues: verificados no codigo.

Caminhos condicionais: conferidos logicamente.

Nao foram executados:
- Spark
- Feature Store
- MLflow
- Optuna
- Databricks Jobs
- GitHub Actions
- Deploy remoto

As aulas anteriores permanecem preservadas.