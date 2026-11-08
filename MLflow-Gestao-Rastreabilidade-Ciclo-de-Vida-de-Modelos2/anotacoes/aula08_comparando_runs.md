# Aula 08 - Comparando runs

## Objetivo

Comparar modelos treinados na Aula 07
pela interface e pela API do MLflow.

## Experimento

risco_credito_comparacao_modelos

## Consulta principal

mlflow.get_experiment_by_name()
mlflow.search_runs()

Filtro:

tags.course_lesson = 'aula_04'

Ordenacao:

metrics.roc_auc_teste DESC

## Modelos

- logistic_regression
- decision_tree
- random_forest

## Metricas de comparacao

- ROC-AUC no teste
- ROC-AUC da validacao cruzada
- desvio da validacao cruzada
- accuracy
- precision dos inadimplentes
- recall dos inadimplentes
- F1 dos inadimplentes

## Shortlist inicial

ROC-AUC >= 0.85
Recall >= 0.70

## Shortlist rigorosa

ROC-AUC >= 0.85
Recall >= 0.85

Os limiares sao didaticos e nao representam
uma politica real de concessao de credito.

## Papeis

Maior ROC-AUC:
champion_candidate

Demais modelos:
challenger

## Cuidados

O melhor ROC-AUC nao garante o melhor
resultado operacional.

Falsos positivos podem prejudicar
clientes que pagariam suas obrigacoes.

Falsos negativos podem representar
maior risco para a instituicao.

A escolha precisa considerar custos,
interpretabilidade, estabilidade e governanca.

## Arquivos

resultados/aula08_ranking_runs.csv
resultados/aula08_ranking_com_papeis.csv
resultados/aula08_shortlist_070.csv
resultados/aula08_shortlist_085.csv
resultados/aula08_comparacao_runs.json
resultados/aula08_resumo_comparacao.md

## Proxima aula

Definir criterios e justificar a
selecao do modelo campeao.
