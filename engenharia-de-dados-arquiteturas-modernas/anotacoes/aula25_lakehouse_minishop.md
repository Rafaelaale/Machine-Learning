# Aula 25 - Lakehouse no Minishop

## Objetivo

Integrar:
- OLTP
- Data Lake Bronze
- Data Lake Silver
- Data Lake Gold
- Lakehouse
- ETL
- Data Warehouse

## Arquitetura do laboratorio

OLTP:
Banco transacional SQLite da Minishop.

Bronze:
Captura dos dados originais da fonte.

Silver:
Clientes, produtos e vendas tratados.

Gold:
Vendas enriquecidas com nome do cliente,
produto e categoria.
Indicadores mensais em Parquet.

Lakehouse:
Catalogo JSON aponta para os proprios arquivos
da Gold analitica.
DuckDB cria views SQL sobre esses arquivos.

Data Warehouse:
ETL exclusivo a partir da Silver.
Tabelas:
dim_cliente
dim_produto
dim_tempo
fato_vendas

## Diferenca importante

Lakehouse e DW nao sao o mesmo ambiente.

Lakehouse:
Consulta diretamente os arquivos Parquet
da Gold, sem copia exclusiva para SQL.

DW:
Armazena modelo dimensional persistente
para indicadores corporativos.

## Reconciliacao

Comparar:
Faturamento Gold
Faturamento Lakehouse
Faturamento DW

Tambem comparar:
Quantidade de unidades
Quantidade de linhas de vendas
Quantidade de pedidos

## Governanca

Catalogo com esquema e localizacao.
Manifesto com hashes SHA-256.
Snapshots preservados.
Consultas do Lakehouse limitadas a SELECT.

## Limites didaticos

O catalogo JSON e local, nao Apache Hive
nem AWS Glue.

O DuckDB e local, nao um cluster distribuido.

A camada Gold analitica usa Parquet.
Nao implementa Delta, Hudi ou Iceberg.

O DW integrado e um modelo dimensional
didatico separado do DW desenvolvido
nas aulas anteriores.

O ETL de demonstracao utiliza a Silver
e nao substitui o orquestrador historico
das aulas 15 e 16.

## Proxima etapa

Estudar os mecanismos de produtividade
e governanca apresentados na proxima aula.
