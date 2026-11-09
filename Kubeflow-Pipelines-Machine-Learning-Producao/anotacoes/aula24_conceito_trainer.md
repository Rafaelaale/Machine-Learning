# Aula 24 — Conceito Trainer do Kubeflow

## Objetivo
Compreender o funcionamento do Kubeflow Trainer.

## Kubeflow Trainer
Componente responsável por automatizar e gerenciar treinamentos
de Machine Learning dentro do Kubernetes.

Permite utilizar recursos do cluster para treinamento
paralelo e distribuído.

## TrainJob
Define declarativamente a tarefa de treinamento.

Especifica o que será treinado e quais parâmetros utilizar.

## Runtime
Define o ambiente responsável pela execução do TrainJob.

Determina como o treinamento será realizado no cluster.

## Configuração declarativa
O processo de treinamento pode ser organizado em arquivos YAML.

## Aplicação no projeto
Nas próximas aulas:

1. Criar um TrainJob para o modelo XGBoost.
2. Criar um Runtime personalizado.
3. Executar o treinamento utilizando o Kubeflow Trainer.

## Situação
Aula conceitual. Nenhuma execução prática necessária.
