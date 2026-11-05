# Aula 09 - Amazon SageMaker

## Objetivo

Compreender o ciclo de vida de Machine Learning
e preparar o laboratorio local do projeto hospitalar.

## Componentes

1. Notebooks: experimentacao e exploracao de dados.
2. Training Jobs: treinamento gerenciado.
3. Processing Jobs: preparacao de dados.
4. Endpoints: inferencia em tempo real.
5. Batch inference: previsoes em lote.
6. Model Registry: gerenciamento de versoes.
7. Model Monitor: monitoramento de modelos.

## Nosso laboratorio gratuito

S3 -> pasta s3_local/
SageMaker -> Python e Scikit-learn no VS Code
Glue -> processamento local
Athena -> DuckDB

## Dados

Arquivo: raw/heart.csv
Registros: 918
Alvo: HeartDisease

## Cuidados cientificos

- Evitar vazamento de dados entre treino e teste.
- Avaliar precision, recall, F1 e matriz de confusao.
- Verificar possiveis vieses e desempenho por subgrupos.
- Nao utilizar o modelo em decisoes clinicas reais.

## Custos

Nenhuma instancia SageMaker criada.
Nenhum endpoint AWS criado.
Nenhum treinamento realizado nesta aula.
