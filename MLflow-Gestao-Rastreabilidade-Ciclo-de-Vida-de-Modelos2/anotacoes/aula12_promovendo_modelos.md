# Aula 12 - Promovendo modelos

## Objetivo

Simular o ciclo de vida de modelos registrados.

## Ciclo de vida

Candidate -> Staging -> Production

## Aliases

candidate
staging
production
champion

## Modelo

risco_credito_classifier

## Inferencia

mlflow.pyfunc.load_model
mlflow.sklearn.load_model

O pyfunc utiliza predict.
O sklearn permite predict_proba.

## Cliente sintetico

Idade: 34
Renda: R$ 4200
Emprego: 5 anos
Score: 620
Solicitacao: R$ 12000
Parcelas: 24
Regime: CLT
Restricao: nao

## Rollback

Alterar alias production para uma
versao anterior existente e aprovada.

## Arquivamento

Manter versoes anteriores ate que
uma politica de substituicao seja cumprida.

## Governanca

Esta promocao e uma simulacao educativa.
Nao autoriza uso para concessao de credito.

## Proxima etapa

Contratos de modelo, signature e serving.
