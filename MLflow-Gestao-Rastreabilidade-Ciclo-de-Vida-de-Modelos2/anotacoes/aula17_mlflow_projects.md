# Aula 17 - MLflow Projects

## Objetivo
Padronizar a preparacao dos dados e o treinamento.

## Arquivos
- MLproject
- python_env.yaml
- src/aula17_prepare_data.py
- src/aula17_train.py

## Entry points implementados
- prepare
- train

## Parametros
- n_samples
- test_size
- random_state
- output_dir
- pipeline_id
- data_dir
- model_name
- registered_model_name

## Execucao
mlflow run . -e prepare -P pipeline_id=teste_aula17 --env-manager local

mlflow run . -e train -P data_dir=data/processed/teste_aula17 -P model_name=random_forest -P pipeline_id=teste_aula17 --env-manager local

## Modelo registrado
risco_credito_project_model

Este modelo e separado dos modelos anteriores.

## Proxima parte
Implementar evaluate e pipeline encadeado.
