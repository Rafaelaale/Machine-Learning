# Aula 10 - Escolha do campeao

## Objetivo

Selecionar o melhor candidato entre:
- Regressao Logistica
- Arvore de Decisao
- Random Forest

## Politica tecnica

ROC-AUC: 35%
Recall inadimplente: 25%
Precision inadimplente: 15%
F1 inadimplente: 15%
Estabilidade: 10%

Estabilidade = 1 - desvio ROC-AUC CV, limitado a [0,1].

## Politica final

Score tecnico: 75%
Interpretabilidade: 15%
Simplicidade operacional: 10%

## Interpretabilidade

Regressao Logistica: 1.00
Arvore de Decisao: 0.80
Random Forest: 0.50

## Simplicidade

Regressao Logistica: 1.00
Arvore de Decisao: 0.90
Random Forest: 0.65

## Artefatos

selection/champion_summary.md
selection/selection_policy.json
selection/decision_matrix.json
selection/preparacao_registry.json

## Atencao

O vencedor e candidato a campeao segundo uma
politica didatica. Nao esta aprovado para producao.

O MLflow Model Registry sera utilizado
na proxima etapa.
