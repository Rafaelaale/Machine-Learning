# Aula 02 - Arquitetura Databricks

## Objetivo

Compreender Lakehouse, Delta Lake, Unity Catalog,
arquitetura Medallion, Databricks Runtime e MLflow.

## Lakehouse

Combina caracteristicas de Data Lake e Data Warehouse.

Permite trabalhar com:
- Dados estruturados e semiestruturados.
- Analises SQL e BI.
- Engenharia de dados.
- Machine Learning e Inteligencia Artificial.
- Governanca e controle de acesso.

## Delta Lake

Utiliza dados em Parquet e um log transacional
separado, normalmente no diretorio `_delta_log`.

Principais recursos:
- Transacoes ACID.
- Versionamento.
- Time Travel, sujeito a retencao dos dados.
- MERGE.
- Evolucao de esquema.
- Restauracao de versoes quando disponiveis.

## Unity Catalog

Organizacao de tres niveis:

catalogo.esquema.tabela

Exemplo:

workspace.gold.base_eventos_produto_gold

Centraliza governanca e descoberta de ativos.

## Arquitetura Medallion

BRONZE:
Ingestao dos dados brutos.

SILVER:
Limpeza, conversoes, validacoes e estruturacao.

GOLD:
Regras de negocio e preparacao para analise e ML.

## MLflow

Gerenciamento de experimentos, metricas,
artefatos e versoes dos modelos.

## Aplicacao no curso

Projeto: previsao de propensao de compra
de produtos eletronicos no e-commerce.

Arquivos de referencia:

aula_1/base_bronze_eventos.csv
aula_1/base_dim_produtos.csv
aula_1/aula_1_4_projeto_ingestao.ipynb
aula_6/pipeline/01_ingestao_dados.py
aula_6/pipeline/02_pre_processamento.py
aula_6/pipeline/03_treinamento_modelo.py

## Observacao preventiva

O pipeline de ingestao do instrutor contem
referencias fixas a tabelas do workspace.

Antes da execucao na Free Edition, devemos
conferir os catalogos, esquemas e volumes
disponiveis na conta do aluno.

## Estado

Aula teorica documentada.
Nenhum recurso Databricks criado.
Nenhum deploy realizado.
Nenhum arquivo original alterado.