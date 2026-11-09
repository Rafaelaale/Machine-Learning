# Aula 10 — Feature Engineering e Funções Auxiliares

## Arquivos

- src/features.py
- src/model.py
- src/train.py

## Engenharia de atributos

Nova coluna: hour_of_day.

Fórmula: (Time % 86400) / 3600.

Features: V1 a V28, Amount e hour_of_day.

Target: Class (0 = legítima; 1 = fraude).

## Divisão dos dados

- Treinamento: 60%.
- Validação: 20%.
- Teste: 20%.
- Estratificação por Class.
- Seed: 42.

## Modelo

Classificador: XGBoost.

- learning_rate: 0.1
- max_depth: 5
- n_estimators: 200
- eval_metric: aucpr
- tree_method: hist
- n_jobs: -1
- random_state: 42

O scale_pos_weight é calculado com os dados de treinamento.

## Métricas

- Precision
- Recall
- F1-score
- PR-AUC

## Resultado

Funções preparadas para as próximas aulas de treinamento,
pipelines Kubeflow e otimização de hiperparâmetros.

Nesta etapa, verificamos a sintaxe dos arquivos.
O treinamento completo será realizado nas próximas aulas.
