# Aula 03 - Arquitetura do Kubeflow

## Objetivo

Entender os componentes do Kubeflow e suas responsabilidades
ao longo do ciclo de vida de Machine Learning.

## 1. Kubeflow Notebooks

Ambiente para exploracao, analise de dados e experimentacao.

## 2. Kubeflow Pipelines (KFP)

Orquestra etapas de Machine Learning.

Conceitos:
- Componentes independentes
- Dependencias entre tarefas
- DAG (grafo aciclico direcionado)
- Entradas e saidas tipadas
- Compilacao da pipeline para YAML

Decoradores principais:
- @dsl.component
- @dsl.pipeline

## 3. Katib

Ferramenta de otimizacao de hiperparametros.

A aula apresenta:
- Busca em grade
- Busca aleatoria
- Otimizacao bayesiana

Nota de atualizacao:
A documentacao atual do Kubeflow marca Katib como depreciado
e orienta a migracao para OptimizationJob do Kubeflow Trainer.

## 4. Kubeflow Trainer

Executa tarefas de treinamento, incluindo cargas distribuidas,
conforme infraestrutura e runtime configurados.

## 5. KServe

Disponibiliza modelos treinados para inferencia por API.

## Exemplo desta aula

Arquivo:
pipelines/aula03_arquitetura_kfp.py

Componentes:
- preprocess
- train

Orquestracao:
- pipeline_ml

Fluxo:
preprocess -> train

As duas etapas sao demonstrativas.
Nao treinam um modelo real nesta aula.

## Compilacao

Com SDK KFP V2 instalado:

python -m pipelines.aula03_arquitetura_kfp

Isso gera:
pipelines/aula03_pipeline_compilado.yaml

## Limites da aula

Nenhum cluster Kubernetes foi criado.
Nenhuma pipeline foi executada remotamente.
Katib, Trainer e KServe foram estudados conceitualmente.

## Proximas aulas

Jupyter dentro do cluster, pipelines de dados,
otimizacao de hiperparametros, treinamento e serving.
