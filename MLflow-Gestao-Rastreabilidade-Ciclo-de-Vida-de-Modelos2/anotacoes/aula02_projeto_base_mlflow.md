# Aula 02 — Projeto base

## Objetivo

Conhecer os componentes do MLflow e compreender
como eles serao utilizados no projeto de
classificacao de risco de credito.

## 1. O que o MLflow resolve?

Permite rastrear experimentos, comparar resultados,
organizar modelos e contribuir para a reprodutibilidade.

## 2. Experimentos e runs

Experimento: agrupa execucoes relacionadas.

Exemplo:
Credit Risk Baseline

Run: representa uma execucao especifica.

Uma run pode registrar:

- parametros;
- metricas;
- artefatos;
- metadados;
- modelo resultante.

## 3. Quatro componentes principais

### MLflow Tracking

Organiza e consulta experimentos e runs.

### MLflow Model Registry

Permite registrar modelos e controlar versoes.

### MLflow Models

Padroniza o empacotamento de modelos
para carregamento ou inferencia.

### MLflow Projects

Ajuda a organizar execucoes reproduziveis
com codigo, ambiente e parametros.

## 4. Diferenca entre os registros

### Parametros

Configuracoes utilizadas durante o treinamento.

Exemplos: max_depth, n_estimators e learning_rate.

### Metricas

Numeros utilizados para avaliar os resultados.

Exemplos: accuracy, precision, recall, F1 e AUC.

### Artefatos

Arquivos produzidos ou associados a uma run.

Exemplos: matriz de confusao, graficos e relatorios.

## 5. Projeto pratico

Problema: classificacao de risco de credito.

O projeto sera desenvolvido progressivamente
a partir de uma base e dos scripts fornecidos
nas proximas etapas do curso.

Nao foram criados dados ou treinamentos ficticios.

## 6. Criterios para comparar modelos

A escolha de um modelo depende do objetivo
e das caracteristicas do problema.

Em risco de credito, tambem sera importante
considerar explicabilidade, qualidade dos dados
e impacto de eventuais erros de classificacao.

## 7. Proximos passos

- Configurar o ambiente MLflow.
- Conhecer o dataset real do curso.
- Criar ou executar o baseline.
- Registrar a primeira run.
- Explorar a interface local.

## Status

Aula conceitual concluida.
Nenhum modelo treinado.
Nenhum experimento real registrado.
