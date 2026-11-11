# Aula 3 - Treinamento de Modelos

## Objetivo

Aprender a treinar, avaliar, comparar e rastrear
modelos de Machine Learning no Databricks.

## Ciclo de ML

1. Problema de negocio.
2. Pre-processamento.
3. Engenharia de features.
4. Treinamento.
5. Validacao.
6. Implantacao.
7. Monitoramento e retreinamento.

## MLflow

- Tracking: registra experimentos, metricas e parametros.
- Runs: execucoes individuais dos experimentos.
- Artifacts: modelos e outros arquivos.
- Model Registry: gerencia modelos e versoes.
- Unity Catalog: pode governar modelos registrados.

O historico de experimentos do MLflow nao equivale
automaticamente ao registro de modelos no Unity Catalog.

## AutoML

Ferramenta de treinamento automatizado.
Disponibilidade depende da edicao e dos recursos
habilitados no workspace Databricks.

## Preparacao da trilha

Notebooks da Alura examinados:

- aula_3_2_treinamento_modelos.ipynb
- aula_3_3_SparkML_Hyperopt_Optuna.ipynb
- aula_3_4_projeto_modelos.ipynb

## Pontos preventivos

- Conferir permissao de acesso ao Unity Catalog.
- Confirmar tabelas de origem antes do treinamento.
- Compativelizar chaves temporais do FeatureLookup.
- Evitar data leakage no e-commerce.
- Comparar modelos com metricas reais.
- Nao sobrescrever tabelas sem validacao.
- Registrar modelos somente quando a aula exigir.

## Status

Aula teorica registrada.
Baseline Iris preparado.
Treinamento remoto ainda pendente.