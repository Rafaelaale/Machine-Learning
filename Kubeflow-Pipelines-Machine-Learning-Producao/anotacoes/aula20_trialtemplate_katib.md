# Aula 20 — TrialTemplate do Katib

## Arquivos criados
- src/train_katib.py
- katib/trial_template.yaml

## Imagem Docker
fraude-trainer:2.2

## Hiperparâmetros
- eta
- max-depth
- n-estimators

## Métrica objetivo
val_pr_auc

## Kubernetes
Cada trial executará um Job.
O dataset será acessado pelo PVC dataset-fraude.

## Resultado desta aula
Script e TrialTemplate preparados e validados.
Imagem Docker disponibilizada no Minikube.

O experimento completo ainda não foi submetido.
