# Aula 15 - Serving via REST

## Objetivo

Servir o PyFunc personalizado como uma API HTTP.

## Modelo

risco_credito_classifier_pyfunc

Alias real do projeto:
servingCandidate

## Servidores

Tracking Server: 127.0.0.1:5000
Serving REST: 127.0.0.1:5001

## Endpoints

GET /ping
GET /health
GET /version
POST /invocations

## Payload

Formato: dataframe_split

Corpo:
- columns
- data
- params.threshold

## Testes

Threshold 0.30
Threshold 0.40
Threshold 0.50

Coluna obrigatoria ausente:
score_interno

## Observabilidade

Consultar logs do servidor de serving.

## Diferenca entre APIs

Tracking Server:
Gerencia experimentos, modelos, versoes e aliases.

Inference Server:
Recebe dados e devolve predicoes.

## Proxima etapa

Docker e smoke tests.

## Seguranca

Servico limitado a localhost.
Base de dados sintetica.
Nao utilizar para decisoes reais de credito.
