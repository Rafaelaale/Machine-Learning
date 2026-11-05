# Aula 16 - Catalogando dados no Glue

## Objetivo

Configurar e executar um Crawler local para
registrar metadados do Data Lake hospitalar.

## Configuracao

Crawler: crawler-alura
Database: raw-data
Tabela: heart
Fonte: raw/heart.csv
Agendamento: sob demanda

## Conceitos

Crawler:
Descobre arquivos e esquemas de dados.

Database:
Agrupa tabelas no Data Catalog.

Table:
Registra metadados como colunas, tipos
de dados, formato e localizacao.

Schema:
Descreve a estrutura dos dados.

## Proximas etapas

- Transformar os dados com ETL.
- Salvar resultados na pasta processed/.
- Catalogar a camada processada.
- Consultar as tabelas com SQL.

## Observacao

Este exercicio e uma simulacao local.
Nao cria recursos no AWS Glue nem
configura permissoes IAM reais.

O catalogo hospital_db da Aula 15
permanece preservado.
