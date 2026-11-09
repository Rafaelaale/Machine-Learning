# Aula 02 - Conceitos essenciais de Kubernetes

## Pod
Menor unidade executavel do Kubernetes.
Um Pod pode conter um ou mais conteineres.

## Deployment
Controla replicas e atualizacoes de aplicacoes persistentes.
Exemplo: servidor de inferencia.

## Job
Executa uma tarefa ate sua conclusao.
Exemplo: treinamento de um modelo.
backoffLimit controla falhas e novas tentativas.

## Namespace
Organiza recursos logicamente no cluster.
Nesta aula usamos kubeflow-aula02 para isolamento.

## Requests e Limits
Requests participam do agendamento de recursos.
Limits restringem o consumo de CPU e memoria.
CPU pode sofrer throttling e memoria pode provocar OOM.

## CRD
Custom Resource Definition.
Permite estender a API Kubernetes com recursos personalizados.

## Exemplos
- kubernetes/01_namespace.yaml
- kubernetes/02_pod.yaml
- kubernetes/03_deployment.yaml
- kubernetes/04_job.yaml

## Observacoes
Os manifests sao exemplos didaticos.
Nenhum recurso foi implantado em cluster.
O Job executa uma simulacao, nao um treinamento real.
A recuperacao do progresso de ML pode exigir checkpoints.
