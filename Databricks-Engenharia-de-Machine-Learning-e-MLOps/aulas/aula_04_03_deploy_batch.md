# Aula 4.3 - Deploy de Modelo em Batch

## Fonte
aula_4/aula_4_3_deploy_modelo_batch.ipynb

## Modelo esperado
workspace.gold.propensao_compra_modelo

## Objetivos

- Consultar versoes no Unity Catalog.
- Utilizar MlflowClient.
- Consultar alias Champion.
- Selecionar explicitamente uma versao.
- Conferir a Signature.
- Criar 13 clientes ficticios.
- Executar mlflow.pyfunc.spark_udf.
- Gerar a coluna vai_comprar.
- Salvar predicoes no Delta opcionalmente.

## Compatibilidade com a Aula 4.2

O modelo preparado na Aula 4.2 utiliza
16 features numericas e categoricas.

Os exemplos do notebook original da Alura
nao possuem exatamente a mesma estrutura.

Por isso, esta versao confere as colunas
e os tipos antes de executar a inferencia.

## Cuidados

Nao escolher Champion apenas pela versao
mais recente.

Revisar metricas antes da promocao.

Alterar alias somente com confirmacao.

Nao sobrescrever dados existentes.

Nao criar endpoints nesta aula.

## Estado

Preparacao local: pendente de validacao PowerShell.

Treinamento e registro no Unity Catalog:
dependem da execucao da Aula 4.2 na nuvem.

Inferencia batch:
depende do modelo registrado e das permissoes.