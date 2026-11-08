# Aula 11 - Model Registry e versoes

## Objetivo

Registrar o classificador selecionado na
Aula 10 como uma versao gerenciada pelo MLflow.

## Registered model

risco_credito_classifier

## Nova run

aula06_register_champion

## Modelo

O algoritmo e recuperado da decisao da Aula 10.
Nao forcar outro algoritmo manualmente.

## Backend

SQLite ja existente: mlflow.db.

## Signature

Descreve o contrato de entrada e saida
do modelo MLflow.

## Input example

Cinco registros de treino, sem a variavel-alvo.

## Aliases

candidate
Nome do algoritmo selecionado

## Lifecycle

candidate

## Versionamento

A primeira inscricao cria a versao 1,
se o registered model ainda nao existir.

Inscricoes posteriores podem criar novas
versoes numeradas.

## Precaucoes

Nao promover para production nesta etapa.
Nao registrar dados sensiveis reais.
Dataset sintetico para aprendizagem.

## Proxima aula

Staging, Production e inferencia por alias.
