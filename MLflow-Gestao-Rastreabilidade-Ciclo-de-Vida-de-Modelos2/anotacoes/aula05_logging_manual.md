# Aula 05 — Logging manual no MLflow

## Objetivo

Aprimorar o rastreamento dos experimentos
de risco de crédito com registro manual.

## Experimento

risco_credito_baseline

## Nome da nova run

aula03_lr_manual_v1

Esse nome reproduz o código da aula da Alura.

## Conceito de logging manual

O registro manual permite escolher quais
parâmetros e métricas serão acompanhados.

Diferentemente do autolog, oferece controle
sobre os campos e nomes usados no rastreamento.

## Modelo utilizado

LogisticRegression

max_iter = 2000
class_weight = balanced
random_state = 42

## Dataset

6000 observações sintéticas.
4500 no treinamento.
1500 no teste.

## Parâmetros

São registradas 18 configurações, incluindo:

- algoritmo
- hiperparâmetros
- pré-processamento
- tamanho do dataset
- divisão treino/teste
- validação cruzada
- target

## Métricas

São registradas 11 métricas.

- ROC-AUC no teste
- média ROC-AUC da validação cruzada
- desvio ROC-AUC da validação cruzada
- acurácia
- precisão
- recall
- F1
- TN
- FP
- FN
- TP

## Matriz de confusão

TN: verdadeiro negativo.
FP: falso positivo.
FN: falso negativo.
TP: verdadeiro positivo.

Neste projeto, a classe positiva é
inadimplente = 1.

Um falso positivo corresponde a um cliente
adimplente classificado como inadimplente.

Um falso negativo corresponde a um cliente
inadimplente classificado como adimplente.

## Armazenamento

O banco mlflow.db guarda metadados
de experimentos e execuções.

Os artefatos ficam em armazenamento separado.

## Próxima aula

- Tags personalizadas.
- Arquivos de relatório.
- Gráficos.
- Matriz de confusão como artefato.
- Curva ROC.

Nenhum artefato é logado nesta aula.
