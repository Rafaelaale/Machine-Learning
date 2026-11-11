# Databricks notebook source
# MAGIC %md
# MAGIC # Aula 3.2 - Treinamento com FeatureLookup e MLflow
# MAGIC
# MAGIC Baseado no notebook 3.2 da Alura.
# MAGIC
# MAGIC Algoritmos:
# MAGIC - Regressao Logistica
# MAGIC - Arvore de Decisao
# MAGIC - Random Forest
# MAGIC - Gradient Boosting
# MAGIC
# MAGIC Este notebook usa a Feature Table criada na Aula 2.
# MAGIC Nao recria IDs e nao sobrescreve tabelas.
# MAGIC
# MAGIC Se FeatureEngineeringClient estiver indisponivel,
# MAGIC instalar no Databricks em uma celula separada:
# MAGIC
# MAGIC %pip install databricks-feature-engineering
# MAGIC
# MAGIC Depois reiniciar o Python e executar novamente.

# COMMAND ----------

import re
import pandas as pd
import mlflow
import mlflow.sklearn

from pyspark.sql import functions as F
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score, f1_score
from mlflow.models import infer_signature

try:
    from databricks.feature_engineering import (
        FeatureEngineeringClient,
        FeatureLookup
    )
except ImportError as erro:
    raise RuntimeError(
        "Feature Engineering nao instalado neste ambiente Databricks. "
        "Instale o pacote indicado no inicio do notebook."
    ) from erro

dbutils.widgets.text("catalogo", "workspace")
dbutils.widgets.dropdown(
    "registrar_modelos",
    "nao",
    ["nao", "sim"]
)

catalogo = dbutils.widgets.get("catalogo").strip()
registrar = dbutils.widgets.get("registrar_modelos") == "sim"

if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", catalogo):
    raise ValueError("Catalogo invalido")

tabela_iris = f"{catalogo}.default.iris_dataset"
tabela_features = f"{catalogo}.default.iris_features_table"
nome_modelo_uc = f"{catalogo}.default.iris_model_prod"

features = [
    "sepal_length",
    "sepal_width",
    "petal_length",
    "petal_width"
]

print("===== CONFIGURACAO =====")
print("IRIS:", tabela_iris)
print("FEATURE STORE:", tabela_features)
print("MODELO UNITY CATALOG:", nome_modelo_uc)
print("REGISTRO DE MODELOS:", registrar)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Validando dados e Feature Store
# MAGIC
# MAGIC Evitamos recriar id_flor com ROW_NUMBER aleatorio.
# MAGIC A especie sera associada aos valores morfologicos
# MAGIC ja armazenados na Feature Table.
# MAGIC
# MAGIC Como Iris possui linhas morfologicas repetidas,
# MAGIC verificamos se alguma combinacao de features
# MAGIC corresponde a especies diferentes.

# COMMAND ----------

for tabela in (tabela_iris, tabela_features):
    if not spark.catalog.tableExists(tabela):
        raise RuntimeError(
            "Tabela ausente no Unity Catalog: " + tabela
        )

df_iris_raw = spark.table(tabela_iris)
df_features_raw = spark.table(tabela_features)

if df_iris_raw.count() != 150:
    raise RuntimeError("Iris deve conter 150 registros")

if df_features_raw.count() != 150:
    raise RuntimeError("Feature Table deve conter 150 registros")

if "species" in df_features_raw.columns:
    raise RuntimeError(
        "Target species nao deve estar na Feature Store"
    )

if not set(features + ["species"]).issubset(
    set(df_iris_raw.columns)
):
    raise RuntimeError("Colunas ausentes na tabela Iris")

if not set(features + ["id_flor"]).issubset(
    set(df_features_raw.columns)
):
    raise RuntimeError("Colunas ausentes na Feature Store")

if df_features_raw.select("id_flor").distinct().count() != 150:
    raise RuntimeError("Chaves id_flor duplicadas")

df_iris = df_iris_raw.select(
    *[
        F.col(c).cast("double").alias(c)
        for c in features
    ],
    F.col("species").cast("string").alias("species")
)

df_feature_keys = df_features_raw.select(
    "id_flor",
    *[
        F.col(c).cast("double").alias(c)
        for c in features
    ]
)

conflitos = (
    df_iris.groupBy(*features)
    .agg(
        F.countDistinct("species").alias("total_especies"),
        F.first("species", ignorenulls=True).alias("species")
    )
)

if conflitos.filter(
    F.col("total_especies") != 1
).limit(1).count():
    raise RuntimeError(
        "Mesmas features associadas a especies diferentes. "
        "Nao e seguro reconstruir o target."
    )

df_target = (
    df_feature_keys
    .join(
        conflitos.select(*features, "species"),
        on=features,
        how="left"
    )
    .select("id_flor", "species")
)

if df_target.count() != 150:
    raise RuntimeError("Erro na correspondencia das chaves")

if df_target.filter(
    F.col("species").isNull()
).limit(1).count():
    raise RuntimeError(
        "Existem IDs sem especie correspondente"
    )

distribuicao = {
    row["species"]: row["count"]
    for row in df_target.groupBy("species").count().collect()
}

if sorted(distribuicao.values()) != [50, 50, 50]:
    raise RuntimeError(
        "Distribuicao das especies ficou incorreta"
    )

print("===== INTEGRIDADE APROVADA =====")
print("CHAVES:", df_target.count())
print("ESPECIES:", distribuicao)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Criando o Training Set com FeatureLookup
# MAGIC
# MAGIC A Feature Store fornece as quatro colunas
# MAGIC preditoras e df_target fornece a especie.

# COMMAND ----------

fe = FeatureEngineeringClient()

fe.get_table(name=tabela_features)

lookups = [
    FeatureLookup(
        table_name=tabela_features,
        feature_names=features,
        lookup_key="id_flor"
    )
]

training_set = fe.create_training_set(
    df=df_target,
    feature_lookups=lookups,
    label="species",
    exclude_columns=["id_flor"]
)

df_train = training_set.load_df().toPandas()

if len(df_train) != 150:
    raise RuntimeError("Training Set nao possui 150 registros")

if not set(features + ["species"]).issubset(df_train.columns):
    raise RuntimeError("Training Set incompleto")

if df_train[features + ["species"]].isnull().any().any():
    raise RuntimeError("Training Set contem valores nulos")

X = df_train[features].copy()
y = df_train["species"].astype(str).copy()

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

if (len(X_train), len(X_test)) != (120, 30):
    raise RuntimeError("Divisao treino/teste incorreta")

print("TRAINING SET APROVADO")
print("TREINO:", len(X_train))
print("TESTE:", len(X_test))
print("FEATURES:", features)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Treinamento e rastreamento MLflow
# MAGIC
# MAGIC Todos os modelos recebem o mesmo conjunto de teste.
# MAGIC A padronizacao da Regressao Logistica fica
# MAGIC dentro do Pipeline sklearn, evitando diferencas
# MAGIC entre treinamento e inferencia.
# MAGIC
# MAGIC Se registrar_modelos = sim:
# MAGIC registra quatro versoes no Unity Catalog.
# MAGIC
# MAGIC O registro fica desativado por padrao para nao
# MAGIC criar modelos e consumir recursos sem autorizacao.

# COMMAND ----------

modelos = {
    "Logistic_Regression": make_pipeline(
        StandardScaler(),
        LogisticRegression(
            max_iter=1000,
            random_state=42
        )
    ),
    "Decision_Tree": DecisionTreeClassifier(
        max_depth=5,
        random_state=42
    ),
    "Random_Forest": RandomForestClassifier(
        n_estimators=100,
        max_depth=5,
        random_state=42,
        n_jobs=1
    ),
    "Gradient_Boosting": GradientBoostingClassifier(
        random_state=42
    )
}

mlflow.sklearn.autolog(log_models=False)

if registrar:
    mlflow.set_registry_uri("databricks-uc")

resultados = []

for nome, modelo in modelos.items():

    with mlflow.start_run(
        run_name=f"Alura_Iris_{nome}"
    ) as run:

        modelo.fit(X_train, y_train)

        predicoes = modelo.predict(X_test)

        acuracia = accuracy_score(y_test, predicoes)
        f1 = f1_score(
            y_test,
            predicoes,
            average="macro"
        )

        mlflow.log_metric("acuracia_teste", acuracia)
        mlflow.log_metric("f1_macro_teste", f1)
        mlflow.log_param("dataset", "Iris")
        mlflow.log_param("aula", "3.2")

        if registrar:

            assinatura = infer_signature(
                X_train,
                modelo.predict(X_train)
            )

            fe.log_model(
                model=modelo,
                artifact_path=f"modelo_{nome.lower()}",
                flavor=mlflow.sklearn,
                training_set=training_set,
                registered_model_name=nome_modelo_uc,
                signature=assinatura,
                input_example=X_train.head(3)
            )

            print("MODELO REGISTRADO:", nome)

        resultados.append({
            "modelo": nome,
            "acuracia": acuracia,
            "f1_macro": f1,
            "run_id": run.info.run_id
        })

        print(
            nome,
            "ACURACIA:", round(acuracia, 4),
            "F1:", round(f1, 4)
        )

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Comparacao final
# MAGIC
# MAGIC As metricas abaixo sao calculadas na execucao
# MAGIC real, sem valores predefinidos.

# COMMAND ----------

df_resultados = pd.DataFrame(resultados)

if len(df_resultados) != 4:
    raise RuntimeError("Nem todos os modelos foram treinados")

df_resultados = df_resultados.sort_values(
    ["f1_macro", "acuracia"],
    ascending=False
)

display(df_resultados)

print("===== TREINAMENTO CONCLUIDO =====")
print("MODELOS:", len(df_resultados))
print("MLFLOW RUNS:", len(df_resultados))
print("REGISTRO NO UNITY CATALOG:", registrar)