# Aula 18 - Pipeline reproduzivel

## Fluxo
prepare -> train -> evaluate

## MLflow Projects
Quatro entry points:
- prepare
- train
- evaluate
- pipeline

## Modelo
risco_credito_project_model

## Execucao Windows
mlflow run . -e pipeline -P model_name=random_forest -P n_samples=6000 -P test_size=0.25 -P random_state=42 -P threshold=0.5 --env-manager local

## Rastreamento
Execucao principal: parent_run_id
Etapas: prepare_run_id, train_run_id, evaluate_run_id

O vinculo entre runs usa a tag mlflow.parentRunId.

## Artefatos
Dados completos, treino e teste, modelo MLflow,
relatorio de classificacao TXT/JSON,
matriz de confusao e resumo consolidado.

## Seguranca
Dados sinteticos de credito.
Modelos historicos preservados.
Sem promocao automatica para producao.

## Proxima etapa
Arquitetura MLOps e infraestrutura remota.
