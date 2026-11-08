# Aula 04 — Primeira run no MLflow

## Objetivo

Treinar o baseline de risco de crédito
e registrar a primeira execução rastreada.

## Experimento

risco_credito_baseline

## Run

baseline_regressao_logistica

## Modelo

Regressão Logística

- max_iter = 2000
- class_weight = balanced
- random_state = 42

## Dataset

6000 observações sintéticas.
4500 para treinamento.
1500 para teste.

Target: inadimplente.

## MLflow Tracking

O rastreamento é configurado por:

mlflow.set_tracking_uri(...)
mlflow.set_experiment(...)

Cada execução utiliza:

with mlflow.start_run(...) as run:

O contexto encerra a execução ao final.

## Parâmetros registrados

- modelo
- max_iter
- class_weight
- test_size
- cv_folds
- random_state
- n_amostras
- n_features
- scoring_cv

## Métricas registradas

- roc_auc_teste
- roc_auc_cv_media
- roc_auc_cv_desvio
- accuracy_teste
- precision_inadimplente
- recall_inadimplente
- f1_inadimplente

## Validação cruzada

StratifiedKFold com cinco partições.

A avaliação utiliza ROC-AUC.

O pré-processamento está dentro
do Pipeline para evitar vazamento
de estatísticas do conjunto de teste.

## Interpretação

ROC-AUC avalia a capacidade de ordenar
observações positivas e negativas.

Recall alto acompanhado de baixa precisão
pode indicar muitos falsos positivos.

Em crédito, os erros precisam ser analisados
considerando impacto econômico, vieses,
governança e critérios de decisão.

## Cliente simulado

A aula utiliza um perfil sintético para
estimar a probabilidade de inadimplência.

O valor exibido deve ser calculado pelo
modelo executado e não informado manualmente.

## Limites desta aula

Nenhum modelo foi registrado no Model Registry.

Nenhum artefato foi logado na run.

Essas etapas serão estudadas depois.

Os relatórios locais foram salvos apenas
para facilitar a auditoria da execução.

## Interface local

A interface pode ser iniciada com:

python -m mlflow ui --backend-store-uri ./mlruns --port 5000

O servidor deve usar o mesmo diretório
de rastreamento configurado no código.
