# Databricks notebook source
# MAGIC %md
# MAGIC # Aula 3 - Treinamento de Modelos com MLflow
# MAGIC
# MAGIC Preparacao antecipada baseada no curso da Alura.
# MAGIC
# MAGIC Objetivos:
# MAGIC - Validar dataset Iris no Unity Catalog.
# MAGIC - Separar treino e teste.
# MAGIC - Treinar dois modelos de classificacao.
# MAGIC - Registrar parametros e metricas no MLflow.
# MAGIC - Comparar desempenho sem registrar modelos em producao.
# MAGIC
# MAGIC Execute somente no Databricks Free Edition,
# MAGIC depois de confirmar a existencia da tabela Iris.

# COMMAND ----------

import pandas as pd
import sklearn
import mlflow
import mlflow.sklearn

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score

print("===== AMBIENTE =====")
print("Scikit-learn:", sklearn.__version__)
print("MLflow:", mlflow.__version__)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Verificando o dataset Iris
# MAGIC
# MAGIC A tabela deve ter sido criada nas aulas anteriores.
# MAGIC Esta etapa nao cria nem modifica tabelas.

# COMMAND ----------

tabela_iris = "workspace.default.iris_dataset"

if not spark.catalog.tableExists(tabela_iris):
    raise RuntimeError(
        "Tabela Iris ausente no Unity Catalog. "
        "Conclua a ingestao anterior."
    )

df_spark = spark.table(tabela_iris)

colunas_features = [
    "sepal_length",
    "sepal_width",
    "petal_length",
    "petal_width"
]

coluna_target = "species"

obrigatorias = set(colunas_features + [coluna_target])

faltando = obrigatorias - set(df_spark.columns)

if faltando:
    raise RuntimeError(
        f"Colunas obrigatorias ausentes: {sorted(faltando)}"
    )

if df_spark.count() != 150:
    raise RuntimeError(
        "O dataset Iris deveria conter 150 registros."
    )

df_pandas = df_spark.select(
    *(colunas_features + [coluna_target])
).toPandas()

for coluna in colunas_features:
    df_pandas[coluna] = pd.to_numeric(
        df_pandas[coluna],
        errors="coerce"
    )

if df_pandas.isnull().any().any():
    raise RuntimeError("Existem dados nulos ou invalidos.")

if df_pandas[coluna_target].nunique() != 3:
    raise RuntimeError(
        "Esperadas tres especies de Iris."
    )

print("DATASET VALIDADO: 150 REGISTROS")
print("FEATURES:", colunas_features)
print("TARGET:", coluna_target)

display(df_spark.limit(5))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Separando treino e teste
# MAGIC
# MAGIC Utilizamos stratify para preservar a proporcao
# MAGIC das especies e random_state para reproducibilidade.

# COMMAND ----------

X = df_pandas[colunas_features]
y = df_pandas[coluna_target]

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

if len(X_train) != 120 or len(X_test) != 30:
    raise RuntimeError(
        "Divisao de treino e teste inesperada."
    )

print("TREINO:", len(X_train))
print("TESTE:", len(X_test))
print("CLASSES:", sorted(y.unique()))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Treinamento e rastreamento MLflow
# MAGIC
# MAGIC O MLflow registrara as execucoes no experimento
# MAGIC associado ao notebook no Databricks.
# MAGIC
# MAGIC Nao sera feito deploy nem registro no Model Registry.

# COMMAND ----------

modelos = {
    "iris_logistic_regression": make_pipeline(
        StandardScaler(),
        LogisticRegression(
            max_iter=1000,
            random_state=42
        )
    ),

    "iris_random_forest": RandomForestClassifier(
        n_estimators=100,
        max_depth=5,
        random_state=42,
        n_jobs=1
    )
}

resultados = []

for nome, modelo in modelos.items():

    with mlflow.start_run(run_name=nome) as run:

        modelo.fit(X_train, y_train)

        predicoes = modelo.predict(X_test)

        acuracia = accuracy_score(y_test, predicoes)
        f1_macro = f1_score(
            y_test,
            predicoes,
            average="macro"
        )

        mlflow.log_param("algoritmo", nome)
        mlflow.log_param("dataset", "Iris")
        mlflow.log_param("train_size", len(X_train))
        mlflow.log_param("test_size", len(X_test))
        mlflow.log_param("random_state", 42)

        mlflow.log_metric("accuracy", acuracia)
        mlflow.log_metric("f1_macro", f1_macro)

        resultados.append({
            "modelo": nome,
            "accuracy": acuracia,
            "f1_macro": f1_macro,
            "run_id": run.info.run_id
        })

        print(
            f"{nome}: "
            f"Accuracy={acuracia:.4f}, "
            f"F1={f1_macro:.4f}"
        )

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Comparando os modelos
# MAGIC
# MAGIC O desempenho sera analisado somente com os resultados
# MAGIC reais das execucoes, sem inventar metricas.

# COMMAND ----------

df_resultados = pd.DataFrame(resultados)

if len(df_resultados) != 2:
    raise RuntimeError(
        "Nem todos os modelos foram registrados."
    )

df_resultados = df_resultados.sort_values(
    ["f1_macro", "accuracy"],
    ascending=False
)

display(df_resultados)

print("===== TREINAMENTO CONCLUIDO =====")
print("MODELOS COMPARADOS: 2")
print("RUNS MLFLOW:", len(df_resultados))
print("REGISTRO EM PRODUCAO: NAO EXECUTADO")