# Aula 06 — Tags e artefatos

## Objetivo

Enriquecer o rastreamento manual do baseline
com contexto e evidencias de desempenho.

## Experimento

risco_credito_baseline

## Run

aula03_lr_manual_v2

## Tags

- project = risco_credito
- course_lesson = aula_03
- dataset_version = synthetic_credit_v1
- model_family = linear_model
- task = binary_classification
- target = inadimplente
- tracking_type = manual
- run_purpose = baseline_with_manual_artifacts

## Metodos MLflow estudados

mlflow.set_tags
mlflow.log_text
mlflow.log_dict
mlflow.log_figure
mlflow.log_table

## Artefatos

1. reports/classification_report.txt
2. reports/classification_report.json
3. reports/run_summary.md
4. plots/matriz_confusao.png
5. plots/curva_roc.png
6. plots/coeficientes_modelo.png
7. tables/coeficientes_modelo.json
8. data/dataset_profile.json

## Matriz de confusao

TN: adimplente classificado como adimplente.
FP: adimplente classificado como inadimplente.
FN: inadimplente classificado como adimplente.
TP: inadimplente classificado como inadimplente.

## Curva ROC

Representa o comportamento do classificador
em diferentes limiares de classificacao.

## Coeficientes

A regressao logistica permite analisar
coeficientes por variavel transformada.

Eles nao representam explicacao causal nem
substituem auditorias completas de vieses.

## Perfil do dataset

Resume a versao, quantidades, colunas,
tipos e proporcoes da variavel-alvo.

O dataset e sintetico, para fins didaticos.

## Armazenamento

Metadados: mlflow.db.
Artefatos: destino local registrado no MLflow.

## Proxima aula

Autolog e comparacao de diferentes modelos.
