# Aula 25 — TrainJob e script de treino

## Arquivos
- infra/pvc-models.yaml
- src/train_node.py
- trainer/trainjob.yaml

## PVC
- Nome: models-pvc-kubeflow
- Namespace: kubeflow
- Capacidade: 512Mi
- Caminho planejado no contêiner: /models

## Modelo
XGBoost para classificação de fraude.

## Hiperparâmetros encontrados no Katib
- ETA: 0.2430296138044891
- MAX_DEPTH: 5
- N_ESTIMATORS: 194

## TrainJob
- Nome: fraude
- Runtime: xgboost-fraude
- Quantidade de nós: 1

## Artefatos esperados
- /models/model.ubj
- /models/metrics.json

## Próxima aula
Criar o ClusterTrainingRuntime personalizado e preparar
a imagem do treinamento.

## Observação
O TrainJob ainda não foi submetido ao Kubernetes.