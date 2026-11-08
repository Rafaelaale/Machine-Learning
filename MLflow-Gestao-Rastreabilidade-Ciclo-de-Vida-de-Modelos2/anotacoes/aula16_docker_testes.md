# Aula 16 - Docker e smoke tests

Modelo: risco_credito_classifier_pyfunc
Alias: servingCandidate
Imagem: risco-credito-serving:latest
Conteiner: risco-credito-api
Mapeamento: 5002:8080

## Testes
- GET /ping
- GET /health
- GET /version
- POST /invocations
- Thresholds 0.30, 0.40 e 0.50
- Payload invalido sem score_interno
- Campos probabilidade_inadimplencia, classe_prevista e limiar_utilizado
- Consistencia do contrato de classificacao

## Comandos
docker logs risco-credito-api
docker stop risco-credito-api
docker images risco-credito-serving

## Nota
Ambiente didatico local, com base sintetica.
Aula seguinte: MLflow Projects.
