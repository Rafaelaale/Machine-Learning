# Machine Learning em Produção com Kubeflow

Projeto prático desenvolvido durante a trilha da Alura, aplicando técnicas de Machine Learning, Engenharia de Dados e MLOps para construir um sistema de detecção de fraudes.

## Tecnologias

- Python, Pandas, NumPy e Scikit-learn
- XGBoost e avaliação de modelos
- Docker e Kubernetes
- Minikube e Kubeflow Pipelines (KFP)
- Katib e otimização de hiperparâmetros
- Trainer e TrainJob
- KServe e conceitos de InferenceService
- APIs de inferência
- RBAC e volumes persistentes
- Argo Workflows

## Etapas desenvolvidas

1. Análise exploratória dos dados (EDA).
2. Limpeza e engenharia de atributos.
3. Desenvolvimento do modelo XGBoost.
4. Treinamento e avaliação.
5. Construção de imagens Docker.
6. Configuração do Kubernetes e Minikube.
7. Criação de pipelines KFP.
8. Persistência com PVCs.
9. Otimização de hiperparâmetros com Katib.
10. Configuração de runtimes e TrainJobs.
11. Implementação de servidor de inferência.
12. Integração End-to-End com promoção condicional.
13. Configuração de permissões RBAC.
14. Deploy e monitoramento do predictor.

## Resultados do modelo

| Indicador | Resultado |
|---|---|
| Algoritmo | XGBoost |
| PR-AUC de validação | 0,8264 |
| PR-AUC de teste | 0,8770 |
| Treinamento Kubernetes | Concluído |
| Pipeline End-to-End | Succeeded |
| Predictor Kubernetes | 1/1 Ready |

Artefatos gerados pelo treinamento:

- model.ubj
- metrics.json

## Pipeline End-to-End

O fluxo implementado contempla:

Dataset -> Pré-processamento -> Treinamento XGBoost -> Avaliação -> Promoção -> Deploy -> Inferência

A promoção utiliza um limiar mínimo de PR-AUC de validação de 0,70.

O modelo aprovado é armazenado em uma release versionada.

## Organização do projeto

- `src/` — scripts Python, features, treinamento e pipelines.
- `pipelines/` — exercícios e pipelines KFP.
- `docker/` — Dockerfiles e configuração de imagens.
- `kubernetes/` — recursos Kubernetes.
- `katib/` — experimentos de otimização.
- `trainer/` — runtimes, Jobs, RBAC e pipelines compiladas.
- `serving/` — API, Deployment e InferenceService de referência.
- `infra/` — infraestrutura.
- `notebooks/` — experimentação.
- `tests/` — testes.
- `anotacoes/` — documentação dos estudos.
- `auditoria/` — verificações do projeto.

## Compatibilidade e limitações

O ambiente de estudo utilizou Kubernetes 1.29.

Devido à incompatibilidade com o Kubeflow Trainer v2, o treinamento foi executado por um Job Kubernetes convencional.

O KServe nativo não foi instalado. Foi implementado um servidor de inferência alternativo, por meio de um Deployment Kubernetes, com endpoints compatíveis com parte do protocolo V2.

A pipeline End-to-End adaptada foi executada com sucesso no Argo Workflows.

Datasets, ambientes virtuais, modelos binários e volumes persistentes não são incluídos neste repositório.

## Objetivo do projeto

Demonstrar conhecimentos práticos em Machine Learning, MLOps, orquestração de pipelines, otimização, treinamento, publicação e gerenciamento do ciclo de vida de modelos.

## Repositório

GitHub: https://github.com/Rafaelaale/Machine-Learning
