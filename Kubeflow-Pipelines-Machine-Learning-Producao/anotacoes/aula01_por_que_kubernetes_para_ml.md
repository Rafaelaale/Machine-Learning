# Aula 01 - Por que Kubernetes para Machine Learning?

## Objetivo
Compreender a necessidade de Kubernetes e Kubeflow em projetos de ML.

## Problemas principais

1. Reprodutibilidade: manter o comportamento entre ambientes.
2. Escalabilidade: permitir uso de recursos computacionais adequados.
3. Resiliencia: recuperar cargas de trabalho apos falhas.

## Docker
Empacota codigo e dependencias em conteineres.

## Kubernetes
Orquestra conteineres, define recursos, replicas e politicas de recuperacao.
A expansao dos recursos depende da capacidade e configuracao do cluster.

## Kubeflow
Oferece componentes especializados para fluxos de Machine Learning.
Permite construir pipelines de preparacao, treinamento e avaliacao.

## Conceitos-chave
- Container
- Cluster
- Pod
- Escalabilidade
- Resiliencia
- Infraestrutura declarativa
- Pipeline de Machine Learning

## Limites
Docker sozinho nao fornece orquestracao completa.
Kubernetes nao garante recuperacao do estado interno de um treinamento.
Checkpoints e armazenamento persistente podem ser necessarios.

## Checkpoint
Aula teorica registrada. Nenhum cluster instalado nesta etapa.
