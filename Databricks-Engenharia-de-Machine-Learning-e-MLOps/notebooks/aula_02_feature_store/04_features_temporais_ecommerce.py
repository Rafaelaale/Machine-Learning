# Databricks notebook source
# MAGIC %md
# MAGIC # Aula 2 - Features temporais do e-commerce
# MAGIC
# MAGIC Projeto Databricks - Engenharia de Machine Learning e MLOps.
# MAGIC
# MAGIC Executar no Databricks Free Edition somente depois da
# MAGIC ingestao Bronze, Silver e Gold.
# MAGIC
# MAGIC Este notebook preserva a Gold original e utiliza apenas
# MAGIC eventos anteriores para calcular as medias historicas.

# COMMAND ----------

import re
from pyspark.sql import functions as F
from pyspark.sql.window import Window

dbutils.widgets.text("catalogo", "workspace")

catalogo = dbutils.widgets.get("catalogo").strip()

if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", catalogo):
    raise ValueError("Nome de catalogo invalido")

tabela_gold = f"{catalogo}.gold.base_eventos_produto_gold"

tabela_gold_particionada = (
    f"{catalogo}.gold.base_eventos_produto_gold_particionada"
)

tabela_features = (
    f"{catalogo}.gold.user_profile_features_temporal"
)

print("===== VERIFICACAO INICIAL =====")

if not spark.catalog.tableExists(tabela_gold):
    raise RuntimeError(
        "Tabela Gold nao encontrada. "
        "Execute primeiro a ingestao no Databricks."
    )

df_origem = spark.table(tabela_gold)

colunas_obrigatorias = {
    "id_usuario",
    "timestamp_registro",
    "tipo_evento",
    "idade",
    "genero",
    "regiao",
    "renda_mensal_estimada_k",
    "tempo_clique_segundos",
    "interacoes_chat_suporte",
    "cupons_ativos_conta",
    "score_satisfacao_nps",
    "dias_desde_ultima_visita",
    "preco_reais"
}

faltando = sorted(
    colunas_obrigatorias - set(df_origem.columns)
)

if faltando:
    raise RuntimeError(
        f"Colunas ausentes na Gold: {faltando}"
    )

total_eventos = df_origem.count()

if total_eventos != 20000:
    raise RuntimeError(
        f"Esperados 20000 eventos, encontrados {total_eventos}"
    )

df_gold = df_origem.withColumn(
    "timestamp_registro",
    F.col("timestamp_registro").cast("timestamp")
)

if df_gold.filter(
    F.col("id_usuario").isNull()
    | F.col("timestamp_registro").isNull()
).limit(1).count():
    raise RuntimeError("Usuario ou timestamp invalido")

duplicadas = (
    df_gold.groupBy("id_usuario", "timestamp_registro")
    .count()
    .filter(F.col("count") > 1)
    .limit(1)
    .count()
)

if duplicadas:
    raise RuntimeError(
        "Chave usuario + timestamp repetida"
    )

print("GOLD ORIGINAL VALIDADA:", total_eventos)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Gold particionada
# MAGIC Cria uma nova tabela sem sobrescrever a Gold original.

# COMMAND ----------

if spark.catalog.tableExists(tabela_gold_particionada):

    gold_part = spark.table(tabela_gold_particionada)

    if (
        "dia_prtc" not in gold_part.columns
        or gold_part.count() != total_eventos
    ):
        raise RuntimeError(
            "Gold particionada existente divergente"
        )

    print("GOLD PARTICIONADA PRESERVADA")

else:

    gold_part = df_gold.withColumn(
        "dia_prtc",
        F.date_format(
            "timestamp_registro", "yyyyMMdd"
        ).cast("int")
    )

    if gold_part.filter(
        F.col("dia_prtc").isNull()
    ).limit(1).count():
        raise RuntimeError("Data de particao invalida")

    (
        gold_part.write
        .format("delta")
        .mode("errorifexists")
        .partitionBy("dia_prtc")
        .saveAsTable(tabela_gold_particionada)
    )

    gold_part = spark.table(tabela_gold_particionada)

    print("GOLD PARTICIONADA CRIADA")

print("REGISTROS:", gold_part.count())

gold_part.select(
    F.min("timestamp_registro").alias("inicio"),
    F.max("timestamp_registro").alias("fim")
).show(truncate=False)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Engenharia de features temporais
# MAGIC
# MAGIC As medias consideram somente eventos anteriores do mesmo
# MAGIC usuario. O evento atual e eventos futuros ficam de fora.
# MAGIC
# MAGIC As primeiras observacoes sem historico recebem zero.

# COMMAND ----------

base = gold_part.withColumn(
    "__ts_unix",
    F.col("timestamp_registro").cast("long")
)

janela_passado = (
    Window.partitionBy("id_usuario")
    .orderBy("__ts_unix")
    .rangeBetween(Window.unboundedPreceding, -1)
)

def media_historica(coluna):
    return F.coalesce(
        F.avg(F.col(coluna)).over(janela_passado),
        F.lit(0.0)
    ).cast("double")

valor_compra = F.when(
    F.col("tipo_evento") == "finalizar_compra",
    F.col("preco_reais").cast("double")
).otherwise(F.lit(0.0))

df_features = base.select(
    "id_usuario",
    "timestamp_registro",

    F.col("idade").cast("int").alias(
        "idade_cliente"
    ),

    F.lower(F.trim(F.col("genero"))).alias(
        "genero_cliente"
    ),

    F.lower(F.trim(F.col("regiao"))).alias(
        "regiao_cliente"
    ),

    F.col("renda_mensal_estimada_k").cast("double").alias(
        "renda_mensal_k"
    ),

    media_historica("tempo_clique_segundos").alias(
        "tempo_medio_clique_segundos"
    ),

    media_historica("interacoes_chat_suporte").alias(
        "media_interacoes_suporte"
    ),

    media_historica("cupons_ativos_conta").alias(
        "media_cupons_ativos"
    ),

    media_historica("score_satisfacao_nps").alias(
        "media_score_nps_cliente"
    ),

    media_historica("dias_desde_ultima_visita").alias(
        "media_dias_inatividade"
    ),

    F.coalesce(
        F.sum(valor_compra).over(janela_passado),
        F.lit(0.0)
    ).cast("double").alias(
        "total_gasto_acumulado_reais"
    ),

    F.count("tipo_evento").over(janela_passado).alias(
        "num_eventos_historicos"
    )
)

if df_features.count() != total_eventos:
    raise RuntimeError(
        "Perda de registros na engenharia de features"
    )

chaves_repetidas = (
    df_features.groupBy(
        "id_usuario", "timestamp_registro"
    )
    .count()
    .filter(F.col("count") > 1)
    .limit(1)
    .count()
)

if chaves_repetidas:
    raise RuntimeError(
        "Chaves duplicadas nas features temporais"
    )

colunas_proibidas = {
    "tipo_evento", "categoria", "preco_reais"
}

if colunas_proibidas & set(df_features.columns):
    raise RuntimeError(
        "Variavel do evento ou target incluida indevidamente"
    )

print("FEATURES VALIDADAS:", df_features.count())

display(df_features.limit(10))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Registro no Unity Catalog
# MAGIC
# MAGIC Se a tabela ja existir, ela sera preservada.
# MAGIC
# MAGIC Caso a biblioteca esteja ausente, instalar em uma
# MAGIC celula separada no Databricks:
# MAGIC
# MAGIC %pip install databricks-feature-engineering
# MAGIC
# MAGIC Depois reiniciar o Python e executar novamente.

# COMMAND ----------

try:
    from databricks.feature_engineering import (
        FeatureEngineeringClient
    )
except ImportError as erro:
    raise RuntimeError(
        "Instale databricks-feature-engineering "
        "no ambiente Databricks."
    ) from erro

fe = FeatureEngineeringClient()

if spark.catalog.tableExists(tabela_features):

    existente = spark.table(tabela_features)

    if existente.count() != total_eventos:
        raise RuntimeError(
            "Feature Table existente com contagem divergente"
        )

    if not set(df_features.columns).issubset(
        set(existente.columns)
    ):
        raise RuntimeError(
            "Feature Table com colunas divergentes"
        )

    if (
        existente.groupBy(
            "id_usuario", "timestamp_registro"
        )
        .count()
        .filter(F.col("count") > 1)
        .limit(1)
        .count()
    ):
        raise RuntimeError(
            "Chave composta duplicada na Feature Table"
        )

    fe.get_table(name=tabela_features)

    print("FEATURE TABLE EXISTENTE PRESERVADA")

else:

    fe.create_table(
        name=tabela_features,
        primary_keys=[
            "id_usuario",
            "timestamp_registro"
        ],
        timeseries_columns=[
            "timestamp_registro"
        ],
        df=df_features,
        description=(
            "Historico comportamental dos usuarios "
            "com agregacoes de eventos anteriores."
        )
    )

    print("FEATURE TABLE REGISTRADA:", tabela_features)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Validacao temporal e historico Delta
# MAGIC
# MAGIC A tabela tem snapshots temporais.
# MAGIC O treinamento posterior devera respeitar a data de corte.
# MAGIC O Time Travel sozinho nao impede vazamento de dados.

# COMMAND ----------

print("===== HISTORICO DELTA =====")

display(
    spark.sql(
        f"DESCRIBE HISTORY {tabela_features}"
    )
)

resumo = (
    spark.table(tabela_features)
    .withColumn(
        "semestre",
        F.when(
            F.month("timestamp_registro") <= 6, 1
        ).otherwise(2)
    )
    .groupBy("semestre")
    .count()
    .orderBy("semestre")
)

display(resumo)

print("===== AULA CONCLUIDA NO NOTEBOOK =====")
print("GOLD ORIGINAL PRESERVADA")
print("FEATURE TABLE:", tabela_features)
print("NENHUM DEPLOY DE MODELOS")