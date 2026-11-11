# Aula 4 - Deploy de Modelos no Databricks

## Objetivo

Compreender como implantar modelos de Machine Learning
e manter governanca de versoes com MLflow e Unity Catalog.

## Ciclo de vida do modelo

1. Definir o problema de negocio.
2. Preparar os dados.
3. Desenvolver as features.
4. Treinar os modelos.
5. Validar os resultados.
6. Registrar e implantar o modelo.
7. Monitorar e realizar retreinamentos.

## Tipos de deploy

### Batch
Predicoes por lotes, em horarios programados.
Exemplo: atualizar diariamente a propensao de compra.

### Streaming
Processamento continuo conforme chegam novos dados.
Exemplo: atualizacao de recomendacoes a partir de eventos.

### Tempo real
Inferencia por requisicao, com baixa latencia.
Exemplo: avaliacao de fraude durante uma transacao.

### Edge
Inferencia executada no dispositivo.
Exemplos: Raspberry Pi, robotica e sistemas embarcados.

## MLflow

- Tracking: registra experimentos e metricas.
- Artifacts: armazena arquivos produzidos pelos runs.
- Models: registra formatos e dependencias do modelo.
- Model Registry: gerencia versoes e aliases.
- Unity Catalog: aplica governanca e permissoes.

## Flavor

Define como um modelo e salvo e carregado.

Exemplos:
- mlflow.sklearn
- mlflow.pyfunc
- mlflow.lightgbm
- mlflow.xgboost

O ambiente do modelo pode incluir:
- versao do Python;
- bibliotecas e dependencias;
- assinatura de entrada e saida;
- exemplo de entrada;
- artefatos de inferencia.

## Champion e aliases

Champion e um nome convencional para indicar
a versao selecionada para uso produtivo.

Um alias permite apontar para uma versao especifica
sem alterar o codigo de todos os consumidores.

Um alias nao realiza deploy automaticamente.

## Cuidados com o projeto

- O treinamento no Databricks ainda nao foi confirmado.
- Nao presumir que existe um modelo registrado.
- Nao criar endpoint antes de validar o Model Registry.
- Nao alterar alias Champion automaticamente.
- Nao sobrescrever tabelas de predicoes.
- Nao executar jobs ou pipelines produtivos nesta aula.
- Confirmar recursos disponiveis na Free Edition.

## Status

Introducao teorica preparada localmente.
Deploy real pendente.