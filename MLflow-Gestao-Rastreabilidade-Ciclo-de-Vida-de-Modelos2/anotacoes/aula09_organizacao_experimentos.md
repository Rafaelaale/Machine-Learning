# Aula 09 - Organizacao do historico

## Objetivo

Padronizar os registros de experimentos
para facilitar busca, auditoria e selecao.

## Convencoes

Experimento:
projeto + fase + objetivo

Run:
aula + modelo + objetivo + versao

Exemplo:
aula04_autolog_random_forest

## Artefatos

reports: relatorios
plots: graficos
data: informacoes sobre os dados
selection: justificativas de selecao

## Tags comuns

project
task
target
dataset_version
feature_set
split_strategy
code_version

## Outras tags

hypothesis
selection_status
experiment_phase
organization_lesson

## Versao do codigo

code_version = not_available

Um hash SHA-256 dos arquivos auxilia
a identificar o conteudo do codigo.

Hash de arquivo nao e um commit.

## Hipoteses

Regressao logistica:
avaliar desempenho e interpretabilidade.

Arvore de decisao:
avaliar desempenho e regras de decisao.

Random Forest:
avaliar possivel ganho tecnico do ensemble
em relacao ao baseline.

## Checklist de rastreabilidade

1. Objetivo
2. Dados
3. Codigo
4. Features
5. Estrategia de split
6. Metricas
7. Artefatos
8. Decisao

## Consultas

mlflow.search_runs()

Filtros por:

tags.project
tags.dataset_version
tags.selection_status
metrics.roc_auc_teste

## Status

As tres runs continuam candidatas.
Nenhum campeao definitivo foi selecionado.
Nenhum treinamento adicional foi executado.

## Proxima etapa

Consolidacao dos criterios e escolha
fundamentada do modelo campeao.
