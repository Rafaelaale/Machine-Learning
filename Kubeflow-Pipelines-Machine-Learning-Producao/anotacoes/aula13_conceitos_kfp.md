# Aula 13 — Conceitos do KFP

## KFP e Argo Workflows

KFP é o orquestrador de pipelines de Machine Learning
do ecossistema Kubeflow.

A aula apresenta o Argo Workflows como mecanismo
de execução dos fluxos de trabalho.

## DAG

Directed Acyclic Graph:
grafo direcionado e sem ciclos.

Permite organizar tarefas sequenciais e paralelas.

## KFP versus scripts Python

| Recurso | Script comum | KFP |
|---|---|---|
| Reprodutibilidade | Depende do ambiente | Contêineres |
| Linhagem | Implementação manual | Rastreamento integrado |
| Cache | Implementação manual | Suporte nativo |
| Agendamento | Ferramentas externas | Execuções recorrentes |
| Observabilidade | Configuração própria | Estados e logs das etapas |

## Componentes

Cada componente representa uma tarefa.

Exemplos do nosso projeto:
1. Carregar o dataset de fraudes.
2. Executar Feature Engineering.
3. Treinar o XGBoost.
4. Avaliar o modelo.
5. Registrar artefatos e métricas.

Os componentes podem ser definidos com o SDK Python do KFP.

## Parâmetros

Valores simples utilizados para configurar componentes.

Exemplos:
- eta = 0.1
- max_depth = 5
- n_estimators = 200

## Artefatos

Arquivos e resultados produzidos ou consumidos por componentes.

Exemplos:
- Dataset processado.
- Modelo XGBoost.
- Métricas de avaliação.

## Cache

Permite reaproveitar resultados de etapas quando
as condições de reutilização são atendidas.

## Lineage

Registra relações entre entradas, execuções e saídas.

## Agendamento

Permite programar execuções recorrentes de pipelines.

## Observabilidade

Permite acompanhar:
- Estado das execuções.
- Etapas concluídas ou com falhas.
- Logs dos contêineres.
- Artefatos produzidos.

## Relação com nosso projeto

Arquivos já preparados:
- src/features.py
- src/model.py
- src/train.py

Modelos treinados:
- models/model.ubj
- models/model-v2.ubj

Próxima etapa:
Implementar os componentes da pipeline KFP.

Nenhum treinamento adicional nesta aula.
