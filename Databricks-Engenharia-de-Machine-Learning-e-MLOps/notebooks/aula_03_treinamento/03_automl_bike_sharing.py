# Databricks notebook source
# MAGIC %md
# MAGIC # Aula 3.2 - AutoML com Bike Sharing
# MAGIC
# MAGIC Exercicio complementar do curso da Alura.
# MAGIC
# MAGIC A criacao da tabela fica desativada por padrao.
# MAGIC
# MAGIC A disponibilidade do AutoML depende dos recursos
# MAGIC da edicao e do workspace Databricks.

# COMMAND ----------

import re
from pyspark.sql import functions as F

dbutils.widgets.text("catalogo", "workspace")

dbutils.widgets.dropdown(
    "criar_tabela",
    "nao",
    ["nao", "sim"]
)

catalogo = dbutils.widgets.get("catalogo").strip()
criar_tabela = dbutils.widgets.get("criar_tabela") == "sim"

if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", catalogo):
    raise ValueError("Catalogo invalido")

tabela_bike = f"{catalogo}.default.bike_sharing_forecast"

caminho = (
    "dbfs:/databricks-datasets/"
    "bikeSharing/data-001/day.csv"
)

print("TABELA:", tabela_bike)
print("ARQUIVO:", caminho)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Conferindo disponibilidade do dataset
# MAGIC
# MAGIC Se o conjunto de dados nao estiver disponivel
# MAGIC na Free Edition, nao sera criada nenhuma tabela.

# COMMAND ----------

if spark.catalog.tableExists(tabela_bike):

    df_bike = spark.table(tabela_bike)
    print("TABELA EXISTENTE PRESERVADA")

elif not criar_tabela:

    print(
        "CRIACAO DESATIVADA. "
        "Selecione criar_tabela=sim para continuar."
    )
    df_bike = None

else:

    try:
        df_bike = spark.read.csv(
            caminho,
            header=True,
            inferSchema=True
        )
    except Exception as erro:
        raise RuntimeError(
            "Dataset Bike Sharing nao acessivel "
            "neste workspace."
        ) from erro

    if not {"dteday", "cnt"}.issubset(df_bike.columns):
        raise RuntimeError(
            "CSV nao possui dteday ou cnt"
        )

    df_bike = (
        df_bike
        .withColumn(
            "dteday",
            F.to_date("dteday")
        )
        .withColumn(
            "cnt",
            F.col("cnt").cast("int")
        )
    )

    if df_bike.filter(
        F.col("dteday").isNull()
        | F.col("cnt").isNull()
    ).limit(1).count():
        raise RuntimeError("Datas ou contagens invalidas")

    (
        df_bike.write
        .format("delta")
        .mode("errorifexists")
        .saveAsTable(tabela_bike)
    )

    print("TABELA BIKE SHARING CRIADA")

# COMMAND ----------

if df_bike is not None:

    print("REGISTROS:", df_bike.count())

    display(
        df_bike.select(
            "dteday", "cnt"
        ).orderBy("dteday").limit(10)
    )

# COMMAND ----------

# MAGIC %md
# MAGIC ## AutoML na interface Databricks
# MAGIC
# MAGIC Se o workspace disponibilizar Forecasting:
# MAGIC
# MAGIC 1. Abrir Machine Learning / AutoML.
# MAGIC 2. Selecionar a tabela bike_sharing_forecast.
# MAGIC 3. Escolher previsao de serie temporal.
# MAGIC 4. Coluna temporal: dteday.
# MAGIC 5. Variavel alvo: cnt.
# MAGIC 6. Frequencia: mensal.
# MAGIC 7. Horizonte: 3 meses.
# MAGIC 8. Executar e comparar as metricas reais.
# MAGIC
# MAGIC Se o recurso estiver indisponivel, nao
# MAGIC contratar servicos pagos para replicar a aula.