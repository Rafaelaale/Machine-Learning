# Kubeflow Pipelines - Machine Learning em Producao

Projeto pratico da trilha Alura de Machine Learning e MLOps.

## Conteudos desenvolvidos

- Analise exploratoria de dados (EDA)
- Pandas e engenharia de atributos
- Treinamento XGBoost
- Avaliacao de modelos e PR-AUC
- Docker e imagens de treinamento
- Kubernetes e Minikube
- PersistentVolumeClaims (PVC)
- Kubeflow Pipelines (KFP)
- Componentes e artefatos
- Execucao e monitoramento de pipelines
- Katib e otimizacao de hiperparametros
- Trainer, Runtime e TrainJob
- Serving e InferenceService
- API de inferencia
- RBAC e ServiceAccounts
- Pipeline End-to-End
- Promocao condicional de modelos
- Deploy e monitoramento do predictor

## Resultados confirmados

Treinamento XGBoost executado em Job Kubernetes.

- PR-AUC de validacao: 0.8264
- PR-AUC de teste: 0.8770
- Artefatos: model.ubj e metrics.json

Pipeline End-to-End:
- Workflow Argo: Succeeded
- Predictor Kubernetes: Ready
- Modelo promovido para uma release versionada

## Compatibilidade

O ambiente utilizou Kubernetes 1.29.

O treinamento e serving foram adaptados com Kubernetes
Jobs e Deployment, respectivamente.

A execucao nativa com Kubeflow Trainer v2 e KServe
permanece pendente de infraestrutura compativel.

## Estrutura

src/ - Scripts Python e pipelines
docker/ - Configuracoes Docker
trainer/ - Jobs, runtimes e pipelines compiladas
serving/ - API, Deployment, InferenceService e RBAC
tests/ - Testes, quando disponiveis

Datasets, ambientes virtuais, PVCs e modelos binarios
nao fazem parte deste repositorio de codigo.
