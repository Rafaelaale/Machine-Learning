# Databricks notebook source
# Notebook da aula: ingestao de teste por catalogo.
# Este arquivo depende de Spark e dbutils no Databricks.

from pyspark.sql import SparkSession

spark = SparkSession.builder.getOrCreate()

dbutils.widgets.text("env_catalog", "dev")
catalogo = dbutils.widgets.get("env_catalog")

if catalogo not in {"dev", "stage", "prod"}:
    raise ValueError("Catalogo invalido")

spark.sql(f"CREATE CATALOG IF NOT EXISTS `{catalogo}`")
spark.sql(f"CREATE SCHEMA IF NOT EXISTS `{catalogo}`.default")

linhas = [
    (1, "1", "usuario1@exemplo.invalid", "cliente"),
    (2, "2", "usuario2@exemplo.invalid", "admin"),
]

colunas = ["id", "nome", "email", "perfil"]

df = spark.createDataFrame(linhas, colunas)

tabela = f"`{catalogo}`.`default`.`usuarios_bronze`"

df.write.format("delta").mode("overwrite").saveAsTable(tabela)

print("Tabela criada:", tabela)
print("Registros:", df.count())