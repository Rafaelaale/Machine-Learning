# Aula 15 - AWS Glue

## Conceitos

ETL: extrair, transformar e carregar dados.

Data Catalog:
Repositorio de metadados sobre databases e tabelas.

Crawler:
Descobre o esquema e registra metadados.

Glue Jobs:
Executam a transformacao dos dados.

Glue Studio:
Interface visual para construir fluxos ETL.

## Nosso laboratorio

Database: hospital_db
Tabela: heart_raw
Fonte: raw/heart.csv
Registros: 918

## Proximas etapas

1. Executar transformacoes ETL.
2. Salvar arquivos em processed/.
3. Catalogar os dados processados.
4. Consultar os resultados utilizando SQL.

## Limites

Esta aula simula o Crawler e o Data Catalog.
Nao reproduz o Glue Studio visual.
Nenhum recurso AWS foi criado.
