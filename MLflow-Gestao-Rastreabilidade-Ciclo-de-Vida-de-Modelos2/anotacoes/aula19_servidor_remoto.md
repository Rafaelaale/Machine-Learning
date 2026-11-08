# Aula 19 - Servidor remoto de MLflow

## Objetivo
Entender a comunicacao cliente-servidor e a separacao dos
armazenamentos de metadados e artefatos.

## Laboratorio
Tracking URI: http://127.0.0.1:5050

Backend Store:
aula19_servidor_remoto/tracking.db

Artifact Store:
aula19_servidor_remoto/artifacts/

Cliente:
src/aula19_cliente_remoto.py

## Diferenca entre componentes
- Tracking Server: API HTTP e interface de experimentos
- Backend Store: runs, experimentos, parametros, metricas e tags
- Artifact Store: arquivos e outros artefatos
- Cliente: envia requisicoes e recebe resultados

## Producao
- PostgreSQL ou outro banco relacional adequado
- S3, GCS ou Azure Blob para artefatos
- HTTPS, autenticacao, autorizacao e rede privada
- Segredos armazenados em gerenciador apropriado

## Limites deste laboratorio
Servidor acessivel somente na maquina local.
Sem AWS, PostgreSQL, credenciais de nuvem ou exposicao publica.

## Conclusao
O cliente Python registra um run via HTTP e baixa um
artefato pela API do MLflow, comprovando a comunicacao.
