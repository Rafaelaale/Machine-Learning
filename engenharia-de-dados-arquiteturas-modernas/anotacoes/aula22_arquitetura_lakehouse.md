# Aula 22 — Arquitetura do Lakehouse

Componentes estudados:

1. Armazenamento em arquivos no Data Lake.
2. Parquet como formato colunar analitico.
3. Catalogo de metadados com esquema, arquivos e localizacao.
4. DuckDB como motor SQL que le Parquet diretamente.

Na Minishop:

- A Bronze preserva o snapshot operacional.
- A Silver disponibiliza dados tratados.
- O Lakehouse armazena tabelas Parquet.
- O catalogo.json descreve as tabelas.
- O manifest.json registra os hashes SHA-256.
- O DuckDB consulta Parquet sem novo DW persistente.
- A Gold permite reconciliar indicadores.

Exemplo SQL:

SELECT
    produto_id,
    SUM(quantidade) AS unidades
FROM vendas
GROUP BY produto_id;

Limites:

- Catalogo local didatico, nao Hive Metastore nem AWS Glue.
- Sem transacoes ACID de tabelas.
- Sem time travel transacional.
- Sem Iceberg, Delta Lake ou Hudi.
- Sem armazenamento distribuido.

Proxima aula: papeis da Gold, DW e Lakehouse.
