# Databricks notebook source
# MAGIC %md
# MAGIC # Aula 4.2 - Modelo LightGBM e Unity Catalog
# MAGIC
# MAGIC Melhorias em relacao ao notebook original da Alura:
# MAGIC - Encoding no Spark
# MAGIC - Separacao temporal
# MAGIC - MLflow e Optuna
# MAGIC - Signature do modelo
# MAGIC - Registro opcional no Unity Catalog
# MAGIC
# MAGIC As tabelas das aulas anteriores serao preservadas.
# MAGIC
# MAGIC Requisito: executar a Aula 3.4 no Databricks antes desta aula.
# MAGIC
# MAGIC Caso faltem bibliotecas, instalar em uma celula separada:
# MAGIC
# MAGIC %pip install databricks-feature-engineering lightgbm optuna
# MAGIC
# MAGIC Reiniciar o Python e executar novamente.

# COMMAND ----------

import re
import mlflow
import mlflow.lightgbm
import pandas as pd
import optuna

from lightgbm import LGBMClassifier
from mlflow.models import infer_signature
from pyspark.sql import functions as F
from databricks.feature_engineering import (
    FeatureEngineeringClient,
    FeatureLookup
)
from sklearn.metrics import accuracy_score, roc_auc_score

dbutils.widgets.text("catalogo", "workspace")
dbutils.widgets.text("trials_optuna", "20")

dbutils.widgets.dropdown(
    "registrar_no_unity",
    "nao",
    ["nao", "sim"]
)

catalogo = dbutils.widgets.get("catalogo").strip()
trials = int(dbutils.widgets.get("trials_optuna"))
registrar = dbutils.widgets.get("registrar_no_unity") == "sim"

if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", catalogo):
    raise ValueError("Catalogo invalido")

if not 1 <= trials <= 100:
    raise ValueError("Use de 1 a 100 trials")

fonte = (
    f"{catalogo}.gold.base_features_modelo_aula34"
)

observacoes = (
    f"{catalogo}.gold.base_propensao_compra_observacao_aula34"
)

tabela_encoded = (
    f"{catalogo}.gold.base_features_modelo_encoded_aula42"
)

modelo_uc = (
    f"{catalogo}.gold.propensao_compra_modelo"
)

print("===== VERIFICANDO TABELAS =====")

for tabela in (fonte, observacoes):

    if not spark.catalog.tableExists(tabela):
        raise RuntimeError(
            f"Tabela ausente: {tabela}. "
            "Execute primeiro a Aula 3.4 no Databricks."
        )

origem = spark.table(fonte)

obrigatorias = {
    "id_usuario",
    "dia_prtc",
    "genero_cliente",
    "regiao_cliente",
    "idade_cliente",
    "renda_mensal_k",
    "tempo_medio_clique_segundos",
    "media_interacoes_suporte",
    "media_cupons_ativos",
    "media_score_nps_cliente",
    "media_dias_inatividade",
    "total_gasto_acumulado_reais",
    "total_eventos_anteriores"
}

faltantes = sorted(
    obrigatorias - set(origem.columns)
)

if faltantes:
    raise RuntimeError(
        f"Features anteriores incompletas: {faltantes}"
    )

if origem.schema["dia_prtc"].dataType.typeName() != "date":
    raise RuntimeError(
        "dia_prtc precisa estar no formato DATE"
    )

qtd = origem.count()

if qtd != 19629:
    raise RuntimeError(
        f"Esperadas 19629 observacoes, encontradas {qtd}"
    )

print("FONTE VALIDADA:", fonte)
print("REGISTROS:", qtd)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Encoding de features com PySpark
# MAGIC
# MAGIC Os valores categoricos sao normalizados para
# MAGIC permitir codificacao numerica consistente.
# MAGIC
# MAGIC Nao usamos pandas.get_dummies.
# MAGIC
# MAGIC Valores numericos nulos recebem zero.
# MAGIC Essa decisao deve ser revista em um projeto produtivo.

# COMMAND ----------

numericas = [
    "idade_cliente",
    "renda_mensal_k",
    "tempo_medio_clique_segundos",
    "media_interacoes_suporte",
    "media_cupons_ativos",
    "media_score_nps_cliente",
    "media_dias_inatividade",
    "total_gasto_acumulado_reais",
    "total_eventos_anteriores"
]

genero = F.lower(
    F.trim(F.col("genero_cliente"))
)

regiao = F.lower(
    F.trim(F.col("regiao_cliente"))
)

categorias = {
    "genero_cliente_f":
        genero.isin("f", "feminino"),

    "genero_cliente_m":
        genero.isin("m", "masculino"),

    "regiao_cliente_centro_oeste":
        regiao.isin("centro-oeste", "centro oeste"),

    "regiao_cliente_nordeste":
        regiao == "nordeste",

    "regiao_cliente_norte":
        regiao == "norte",

    "regiao_cliente_sudeste":
        regiao == "sudeste",

    "regiao_cliente_sul":
        regiao == "sul"
}

categoricas = list(categorias)
features = numericas + categoricas

colunas = [
    F.col("id_usuario"),
    F.col("dia_prtc")
]

colunas.extend(
    F.coalesce(
        F.col(nome).cast("double"),
        F.lit(0.0)
    ).alias(nome)
    for nome in numericas
)

colunas.extend(
    F.when(condicao, F.lit(1))
    .otherwise(F.lit(0))
    .cast("integer")
    .alias(nome)
    for nome, condicao in categorias.items()
)

encoded = origem.select(*colunas)

if encoded.count() != qtd:
    raise RuntimeError(
        "Encoding alterou a quantidade de registros"
    )

duplicados = (
    encoded
    .groupBy("id_usuario", "dia_prtc")
    .count()
    .filter("count > 1")
    .limit(1)
    .count()
)

if duplicados:
    raise RuntimeError(
        "Chaves usuario/dia duplicadas"
    )

print("ENCODING SPARK VALIDADO")
print("FEATURES NUMERICAS:", len(numericas))
print("FEATURES CATEGORICAS:", len(categoricas))

display(encoded.limit(10))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Registrando Feature Table codificada
# MAGIC
# MAGIC Utiliza uma tabela exclusiva da Aula 4.2.
# MAGIC Nao altera a Feature Table da Aula 3.4.

# COMMAND ----------

fe = FeatureEngineeringClient()

if spark.catalog.tableExists(tabela_encoded):

    atual = spark.table(tabela_encoded)

    esquema_atual = [
        (campo.name, campo.dataType.simpleString())
        for campo in atual.schema
    ]

    esquema_esperado = [
        (campo.name, campo.dataType.simpleString())
        for campo in encoded.schema
    ]

    if (
        esquema_atual != esquema_esperado
        or atual.count() != qtd
    ):
        raise RuntimeError(
            "Feature Table existente incompativel"
        )

    if encoded.exceptAll(
        atual.select(*encoded.columns)
    ).limit(1).count():
        raise RuntimeError(
            "Dados da Feature Table existente divergentes"
        )

    fe.get_table(name=tabela_encoded)

    print("FEATURE TABLE EXISTENTE PRESERVADA")

else:

    fe.create_table(
        name=tabela_encoded,
        primary_keys=[
            "id_usuario",
            "dia_prtc"
        ],
        timeseries_columns=[
            "dia_prtc"
        ],
        df=encoded,
        description=(
            "Features temporais codificadas com PySpark "
            "para o modelo LightGBM da Aula 4.2."
        )
    )

    print("FEATURE TABLE CRIADA:", tabela_encoded)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. FeatureLookup
# MAGIC
# MAGIC O target permanece separado das features.
# MAGIC A data sera utilizada para divisao temporal,
# MAGIC mas nao sera uma variavel de entrada do LightGBM.

# COMMAND ----------

df_obs = spark.table(observacoes)

campos_target = {
    "id_usuario",
    "dia_prtc",
    "comprou_eletronico"
}

if not campos_target.issubset(df_obs.columns):
    raise RuntimeError(
        "Tabela de observacoes incompleta"
    )

if df_obs.count() != qtd:
    raise RuntimeError(
        "Contagem das observacoes divergente"
    )

lookups = [
    FeatureLookup(
        table_name=tabela_encoded,
        feature_names=features,
        lookup_key="id_usuario",
        timestamp_lookup_key="dia_prtc"
    )
]

training_set = fe.create_training_set(
    df=df_obs,
    feature_lookups=lookups,
    label="comprou_eletronico",
    exclude_columns=["id_usuario"]
)

frame = training_set.load_df().toPandas()

campos_esperados = set(
    features + ["dia_prtc", "comprou_eletronico"]
)

if (
    len(frame) != qtd
    or not campos_esperados.issubset(frame.columns)
):
    raise RuntimeError(
        "FeatureLookup retornou dados incompletos"
    )

frame["dia_prtc"] = pd.to_datetime(
    frame["dia_prtc"]
)

frame["comprou_eletronico"] = pd.to_numeric(
    frame["comprou_eletronico"],
    errors="raise"
).astype("int32")

for nome in numericas:
    frame[nome] = pd.to_numeric(
        frame[nome],
        errors="raise"
    ).astype("float64")

for nome in categoricas:
    frame[nome] = pd.to_numeric(
        frame[nome],
        errors="raise"
    ).astype("int32")

if frame[features].isnull().any().any():
    raise RuntimeError(
        "Existem valores nulos apos o encoding"
    )

print("TRAINING SET VALIDADO:", len(frame))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Treino, validacao e teste cronologico
# MAGIC
# MAGIC Treino: janeiro a abril de 2025.
# MAGIC Validacao: maio e junho de 2025.
# MAGIC Teste futuro: julho a dezembro de 2025.

# COMMAND ----------

train = frame[
    frame.dia_prtc < "2025-05-01"
]

valid = frame[
    (frame.dia_prtc >= "2025-05-01")
    & (frame.dia_prtc < "2025-07-01")
]

test = frame[
    frame.dia_prtc >= "2025-07-01"
]

contagens = tuple(
    map(len, (train, valid, test))
)

if contagens != (6381, 3258, 9990):
    raise RuntimeError(
        f"Divisao temporal divergente: {contagens}"
    )

for parte in (train, valid, test):
    if parte.comprou_eletronico.nunique() != 2:
        raise RuntimeError(
            "Periodo sem ambas as classes do target"
        )

X_train = train[features]
y_train = train.comprou_eletronico

X_valid = valid[features]
y_valid = valid.comprou_eletronico

X_test = test[features]
y_test = test.comprou_eletronico

print("TREINAMENTO:", len(train))
print("VALIDACAO:", len(valid))
print("TESTE:", len(test))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Optuna e treinamento do LightGBM
# MAGIC
# MAGIC A busca utiliza somente treino e validacao.
# MAGIC O teste futuro fica reservado para avaliacao final.
# MAGIC
# MAGIC Por padrao sao 20 tentativas.
# MAGIC O widget permite aumentar ate 100.

# COMMAND ----------

mlflow.set_registry_uri("databricks-uc")

with mlflow.start_run(
    run_name="Aula42_Modelo_Final_LGBM"
) as run:

    def objetivo(trial):

        params = {
            "n_estimators": trial.suggest_int(
                "n_estimators", 50, 180
            ),
            "max_depth": trial.suggest_int(
                "max_depth", 3, 9
            ),
            "num_leaves": trial.suggest_int(
                "num_leaves", 10, 60
            ),
            "learning_rate": trial.suggest_float(
                "learning_rate",
                0.01,
                0.2,
                log=True
            ),
            "min_child_samples": trial.suggest_int(
                "min_child_samples", 10, 50
            )
        }

        candidato = LGBMClassifier(
            **params,
            random_state=42,
            verbosity=-1,
            n_jobs=1
        )

        candidato.fit(X_train, y_train)

        probabilidade = candidato.predict_proba(
            X_valid
        )[:, 1]

        auc = roc_auc_score(
            y_valid,
            probabilidade
        )

        return float(auc)

    estudo = optuna.create_study(
        direction="maximize",
        sampler=optuna.samplers.TPESampler(
            seed=42
        )
    )

    estudo.optimize(
        objetivo,
        n_trials=trials
    )

    melhores = estudo.best_params

    mlflow.log_params(melhores)

    mlflow.log_metric(
        "auc_validacao_optuna",
        float(estudo.best_value)
    )

    mlflow.log_param(
        "trials_optuna",
        trials
    )

    mlflow.log_param(
        "periodo_treino_e_tuning",
        "2025-01_a_2025-06"
    )

    mlflow.log_param(
        "periodo_teste",
        "2025-07_a_2025-12"
    )

    # Treinamento final com o primeiro semestre.

    primeiro_semestre = frame[
        frame.dia_prtc < "2025-07-01"
    ]

    X_final = primeiro_semestre[features]
    y_final = primeiro_semestre.comprou_eletronico

    modelo = LGBMClassifier(
        **melhores,
        random_state=42,
        verbosity=-1,
        n_jobs=1
    )

    modelo.fit(
        X_final,
        y_final
    )

    # Avaliacao com os dados futuros.

    pred_classes = modelo.predict(X_test)

    pred_prob = modelo.predict_proba(
        X_test
    )[:, 1]

    auc_teste = float(
        roc_auc_score(y_test, pred_prob)
    )

    acuracia_teste = float(
        accuracy_score(y_test, pred_classes)
    )

    mlflow.log_metrics({
        "auc_roc_teste_futuro": auc_teste,
        "accuracy_teste_futuro": acuracia_teste
    })

    # Assinatura de entrada e saida.

    exemplo = X_final.head(5).copy()

    signature = infer_signature(
        exemplo,
        modelo.predict(exemplo)
    )

    # Registra o artefato no MLflow.
    # O registro no Unity Catalog e opcional.

    argumentos_log = dict(
        lgb_model=modelo,
        artifact_path="model",
        signature=signature,
        input_example=exemplo
    )

    if registrar:
        argumentos_log[
            "registered_model_name"
        ] = modelo_uc

    modelo_logado = mlflow.lightgbm.log_model(
        **argumentos_log
    )

    print("===== RESULTADO DO TREINAMENTO =====")
    print("MLFLOW RUN:", run.info.run_id)
    print("MODELO ARTIFACT:", modelo_logado.model_uri)
    print("MELHOR AUC VALIDACAO:", round(estudo.best_value, 4))
    print("AUC TESTE FUTURO:", round(auc_teste, 4))
    print("ACURACIA TESTE FUTURO:", round(acuracia_teste, 4))

    print(
        "REGISTRO NO UNITY CATALOG:",
        "SIM" if registrar else "NAO"
    )

    if registrar:
        print("MODELO REGISTRADO:", modelo_uc)

    print("NENHUM ENDPOINT OU ALIAS FOI ATIVADO")