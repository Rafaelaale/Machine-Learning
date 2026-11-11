# Databricks notebook source
# MAGIC %md
# MAGIC # Aula 3.4 - Modelos de propensao de compra
# MAGIC
# MAGIC Baselines, MLflow, Optuna e SHAP.
# MAGIC Baseado no notebook original da Alura.
# MAGIC
# MAGIC As features usam apenas dias anteriores.
# MAGIC Teste futuro: julho a dezembro de 2025.
# MAGIC
# MAGIC Execute no Databricks apos concluir a camada Gold.

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Bibliotecas e configuracao
# MAGIC
# MAGIC Caso alguma dependencia esteja ausente, instalar
# MAGIC em uma celula separada no Databricks:
# MAGIC
# MAGIC %pip install databricks-feature-engineering lightgbm xgboost optuna shap
# MAGIC
# MAGIC Depois reiniciar o Python e executar novamente.

# COMMAND ----------

import re
import numpy as np
import pandas as pd
import mlflow

from pyspark.sql import functions as F
from pyspark.sql.window import Window

from sklearn.base import clone
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import roc_auc_score, accuracy_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from databricks.feature_engineering import FeatureEngineeringClient, FeatureLookup

dbutils.widgets.text("catalogo", "workspace")
dbutils.widgets.text("n_trials_optuna", "20")

catalogo = dbutils.widgets.get("catalogo").strip()

if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", catalogo):
    raise ValueError("Catalogo invalido")

n_trials = int(dbutils.widgets.get("n_trials_optuna"))

if not 1 <= n_trials <= 100:
    raise ValueError("Use entre 1 e 100 trials")

origem_particionada = (
    f"{catalogo}.gold.base_eventos_produto_gold_particionada"
)

origem_basica = (
    f"{catalogo}.gold.base_eventos_produto_gold"
)

if spark.catalog.tableExists(origem_particionada):
    tabela_gold = origem_particionada
else:
    tabela_gold = origem_basica

if not spark.catalog.tableExists(tabela_gold):
    raise RuntimeError(
        "Gold ausente. Execute primeiro a ingestao no Databricks."
    )

nome_features = (
    f"{catalogo}.gold.base_features_modelo_aula34"
)

nome_observacao = (
    f"{catalogo}.gold.base_propensao_compra_observacao_aula34"
)

gold = spark.table(tabela_gold)

obrigatorias = {
    "id_usuario",
    "timestamp_registro",
    "tipo_evento",
    "categoria",
    "preco_reais",
    "idade",
    "genero",
    "regiao",
    "renda_mensal_estimada_k",
    "tempo_clique_segundos",
    "interacoes_chat_suporte",
    "cupons_ativos_conta",
    "score_satisfacao_nps",
    "dias_desde_ultima_visita"
}

faltantes = sorted(obrigatorias - set(gold.columns))

if faltantes:
    raise RuntimeError(f"Colunas ausentes na Gold: {faltantes}")

if gold.count() != 20000:
    raise RuntimeError(
        "A Gold nao possui os 20000 eventos esperados."
    )

print("GOLD VALIDADA:", tabela_gold)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Construindo o target e as agregacoes
# MAGIC
# MAGIC Target positivo:
# MAGIC finalizar_compra + categoria Eletronicos.
# MAGIC
# MAGIC Uma observacao representa um usuario em um dia.
# MAGIC O gasto acumulado considera somente compras anteriores.

# COMMAND ----------

base = gold.withColumn(
    "dia_prtc",
    F.to_date("timestamp_registro")
)

if base.filter(
    F.col("dia_prtc").isNull()
    | F.col("id_usuario").isNull()
).limit(1).count():
    raise RuntimeError("Data ou usuario invalido")

eh_compra = F.col("tipo_evento") == "finalizar_compra"
eh_eletronico = F.col("categoria") == "Eletrônicos"

diario = base.groupBy(
    "id_usuario", "dia_prtc"
).agg(
    F.max(
        F.when(eh_compra & eh_eletronico, 1).otherwise(0)
    ).alias("comprou_eletronico"),

    F.count(F.lit(1)).alias("n_eventos_dia"),

    F.sum(
        F.when(
            eh_compra,
            F.col("preco_reais").cast("double")
        ).otherwise(0.0)
    ).alias("gasto_compras_dia"),

    F.sum("tempo_clique_segundos").alias("soma_cliques"),
    F.count("tempo_clique_segundos").alias("qtd_cliques"),

    F.sum("interacoes_chat_suporte").alias("soma_chat"),
    F.count("interacoes_chat_suporte").alias("qtd_chat"),

    F.sum("cupons_ativos_conta").alias("soma_cupons"),
    F.count("cupons_ativos_conta").alias("qtd_cupons"),

    F.sum("score_satisfacao_nps").alias("soma_nps"),
    F.count("score_satisfacao_nps").alias("qtd_nps"),

    F.sum("dias_desde_ultima_visita").alias("soma_inatividade"),
    F.count("dias_desde_ultima_visita").alias("qtd_inatividade"),

    F.max_by("idade", "timestamp_registro").alias("idade_dia"),
    F.max_by("genero", "timestamp_registro").alias("genero_dia"),
    F.max_by("regiao", "timestamp_registro").alias("regiao_dia"),

    F.max_by(
        "renda_mensal_estimada_k",
        "timestamp_registro"
    ).alias("renda_dia")
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Features historicas sem vazamento temporal
# MAGIC
# MAGIC A janela termina no dia anterior.
# MAGIC Nenhuma interacao do dia atual entra nas features.

# COMMAND ----------

janela_passado = (
    Window.partitionBy("id_usuario")
    .orderBy("dia_prtc")
    .rowsBetween(Window.unboundedPreceding, -1)
)

def media_passada(soma, quantidade):
    total = F.sum(F.col(soma)).over(janela_passado)
    qtd = F.sum(F.col(quantidade)).over(janela_passado)

    return F.when(
        qtd > 0,
        total / qtd
    ).otherwise(F.lit(None)).cast("double")

df_features = diario.select(
    "id_usuario",
    "dia_prtc",

    F.last(
        "idade_dia", ignorenulls=True
    ).over(janela_passado).cast("double").alias("idade_cliente"),

    F.lower(F.trim(
        F.last(
            "genero_dia", ignorenulls=True
        ).over(janela_passado)
    )).alias("genero_cliente"),

    F.lower(F.trim(
        F.last(
            "regiao_dia", ignorenulls=True
        ).over(janela_passado)
    )).alias("regiao_cliente"),

    F.last(
        "renda_dia", ignorenulls=True
    ).over(janela_passado).cast("double").alias("renda_mensal_k"),

    media_passada(
        "soma_cliques", "qtd_cliques"
    ).alias("tempo_medio_clique_segundos"),

    media_passada(
        "soma_chat", "qtd_chat"
    ).alias("media_interacoes_suporte"),

    media_passada(
        "soma_cupons", "qtd_cupons"
    ).alias("media_cupons_ativos"),

    media_passada(
        "soma_nps", "qtd_nps"
    ).alias("media_score_nps_cliente"),

    media_passada(
        "soma_inatividade", "qtd_inatividade"
    ).alias("media_dias_inatividade"),

    F.coalesce(
        F.sum("gasto_compras_dia").over(janela_passado),
        F.lit(0.0)
    ).cast("double").alias("total_gasto_acumulado_reais"),

    F.coalesce(
        F.sum("n_eventos_dia").over(janela_passado),
        F.lit(0)
    ).cast("long").alias("total_eventos_anteriores")
)

df_observacao = diario.select(
    "id_usuario",
    "dia_prtc",
    "comprou_eletronico"
)

total_observacoes = df_observacao.count()

if total_observacoes != 19629:
    raise RuntimeError(
        "Quantidade usuario/dia diferente da base original."
    )

if df_features.count() != total_observacoes:
    raise RuntimeError("Perda de registros nas features")

if (
    df_features
    .groupBy("id_usuario", "dia_prtc")
    .count()
    .filter(F.col("count") > 1)
    .limit(1)
    .count()
):
    raise RuntimeError("Chave composta duplicada")

print("FEATURES PREPARADAS:", total_observacoes)
display(df_features.limit(10))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Registrando Feature Table e observacoes
# MAGIC
# MAGIC Nomes exclusivos da Aula 3.4.
# MAGIC Tabelas preexistentes nao serao sobrescritas.

# COMMAND ----------

fe = FeatureEngineeringClient()

if spark.catalog.tableExists(nome_features):
    existente = spark.table(nome_features)

    if (
        existente.count() != total_observacoes
        or set(existente.columns) != set(df_features.columns)
    ):
        raise RuntimeError(
            "Feature Table existente incompativel."
        )

    fe.get_table(name=nome_features)
    print("FEATURE TABLE PRESERVADA")

else:
    fe.create_table(
        name=nome_features,
        primary_keys=["id_usuario", "dia_prtc"],
        timeseries_columns=["dia_prtc"],
        df=df_features,
        description=(
            "Features comportamentais calculadas "
            "com dados de dias anteriores."
        )
    )

    print("FEATURE TABLE CRIADA")

if spark.catalog.tableExists(nome_observacao):
    existente = spark.table(nome_observacao)

    if (
        existente.count() != total_observacoes
        or set(existente.columns) != set(df_observacao.columns)
    ):
        raise RuntimeError(
            "Tabela de observacao existente incompativel."
        )

    print("TABELA DE OBSERVACAO PRESERVADA")

else:
    (
        df_observacao.write
        .format("delta")
        .mode("errorifexists")
        .saveAsTable(nome_observacao)
    )

    print("TABELA DE OBSERVACAO CRIADA")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. FeatureLookup e Training Set

# COMMAND ----------

lista_features = [
    coluna
    for coluna in df_features.columns
    if coluna not in {"id_usuario", "dia_prtc"}
]

recursos = [
    FeatureLookup(
        table_name=nome_features,
        feature_names=lista_features,
        lookup_key="id_usuario",
        timestamp_lookup_key="dia_prtc"
    )
]

training_set = fe.create_training_set(
    df=spark.table(nome_observacao),
    feature_lookups=recursos,
    label="comprou_eletronico"
)

frame = training_set.load_df().toPandas()

if len(frame) != total_observacoes:
    raise RuntimeError(
        "FeatureLookup alterou a quantidade de observacoes."
    )

print("TRAINING SET CRIADO:", len(frame))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6. Divisao temporal e pre-processamento
# MAGIC
# MAGIC Treino: janeiro a abril
# MAGIC Validacao: maio e junho
# MAGIC Teste: julho a dezembro

# COMMAND ----------

frame["dia_prtc"] = pd.to_datetime(frame["dia_prtc"])

frame["comprou_eletronico"] = pd.to_numeric(
    frame["comprou_eletronico"],
    errors="raise"
).astype(int)

frame = frame.sort_values(
    ["dia_prtc", "id_usuario"]
).reset_index(drop=True)

categoricas = [
    c for c in ["genero_cliente", "regiao_cliente"]
    if c in lista_features
]

numericas = [
    c for c in lista_features
    if c not in categoricas
]

for coluna in numericas:
    frame[coluna] = pd.to_numeric(
        frame[coluna],
        errors="coerce"
    ).astype(float)

for coluna in categoricas:
    frame[coluna] = (
        frame[coluna]
        .astype("object")
        .where(frame[coluna].notna(), "desconhecido")
    )

treino = frame[frame["dia_prtc"] < "2025-05-01"].copy()

validacao = frame[
    (frame["dia_prtc"] >= "2025-05-01")
    & (frame["dia_prtc"] < "2025-07-01")
].copy()

teste = frame[
    frame["dia_prtc"] >= "2025-07-01"
].copy()

if (
    len(treino),
    len(validacao),
    len(teste)
) != (6381, 3258, 9990):
    raise RuntimeError("Divisao temporal divergente")

for nome, conjunto in [
    ("treino", treino),
    ("validacao", validacao),
    ("teste", teste)
]:
    if conjunto["comprou_eletronico"].nunique() != 2:
        raise RuntimeError(
            f"Conjunto {nome} nao possui duas classes"
        )

X_train = treino[lista_features]
y_train = treino["comprou_eletronico"]

X_valid = validacao[lista_features]
y_valid = validacao["comprou_eletronico"]

X_test = teste[lista_features]
y_test = teste["comprou_eletronico"]

preprocessamento = ColumnTransformer([
    (
        "num",
        Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler())
        ]),
        numericas
    ),
    (
        "cat",
        Pipeline([
            (
                "imputer",
                SimpleImputer(
                    strategy="constant",
                    fill_value="desconhecido"
                )
            ),
            ("onehot", OneHotEncoder(handle_unknown="ignore"))
        ]),
        categoricas
    )
])

def criar_pipeline(classificador):
    return Pipeline([
        ("preprocessor", clone(preprocessamento)),
        ("classificador", classificador)
    ])

print("TREINO:", len(treino))
print("VALIDACAO:", len(validacao))
print("TESTE:", len(teste))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 7. Cinco algoritmos e MLflow
# MAGIC
# MAGIC A selecao usa exclusivamente a validacao.
# MAGIC O teste futuro fica reservado para o final.

# COMMAND ----------

from xgboost import XGBClassifier
from lightgbm import LGBMClassifier

modelos = {
    "LogisticRegression": LogisticRegression(
        max_iter=1000,
        random_state=42
    ),

    "RandomForest": RandomForestClassifier(
        n_estimators=80,
        max_depth=6,
        random_state=42,
        n_jobs=1
    ),

    "GradientBoosting": GradientBoostingClassifier(
        n_estimators=80,
        random_state=42
    ),

    "XGBoost": XGBClassifier(
        n_estimators=80,
        max_depth=5,
        random_state=42,
        eval_metric="logloss",
        n_jobs=1
    ),

    "LightGBM": LGBMClassifier(
        n_estimators=80,
        max_depth=6,
        random_state=42,
        verbosity=-1,
        n_jobs=1
    )
}

comparacoes = []

for nome, estimador in modelos.items():

    with mlflow.start_run(
        run_name="Aula34_baseline_" + nome
    ):

        modelo = criar_pipeline(estimador)
        modelo.fit(X_train, y_train)

        probabilidades = modelo.predict_proba(X_valid)[:, 1]

        auc = roc_auc_score(
            y_valid,
            probabilidades
        )

        acuracia = accuracy_score(
            y_valid,
            modelo.predict(X_valid)
        )

        mlflow.log_params({
            "modelo": nome,
            "treino": "2025-01_2025-04",
            "validacao": "2025-05_2025-06"
        })

        mlflow.log_metrics({
            "auc_validacao": auc,
            "accuracy_validacao": acuracia
        })

        comparacoes.append({
            "modelo": nome,
            "auc": auc,
            "acuracia": acuracia
        })

        print(
            f"{nome}: "
            f"AUC={auc:.4f} "
            f"ACCURACY={acuracia:.4f}"
        )

display(
    pd.DataFrame(comparacoes)
    .sort_values("auc", ascending=False)
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 8. Optuna com LightGBM
# MAGIC
# MAGIC 20 tentativas por padrao para economizar recursos.
# MAGIC O widget permite aumentar para ate 100.
# MAGIC A otimizacao nao consulta o conjunto de teste.

# COMMAND ----------

import optuna

with mlflow.start_run(
    run_name="Aula34_Optuna_LightGBM"
):

    def objetivo_optuna(trial):

        parametros = {
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
                "learning_rate", 0.01, 0.2, log=True
            ),
            "min_child_samples": trial.suggest_int(
                "min_child_samples", 10, 50
            ),
            "random_state": 42,
            "verbosity": -1,
            "n_jobs": 1
        }

        candidato = criar_pipeline(
            LGBMClassifier(**parametros)
        )

        candidato.fit(X_train, y_train)

        probabilidades = candidato.predict_proba(
            X_valid
        )[:, 1]

        auc = roc_auc_score(
            y_valid,
            probabilidades
        )

        with mlflow.start_run(
            run_name=f"trial_{trial.number}",
            nested=True
        ):
            mlflow.log_params({
                k: v
                for k, v in parametros.items()
                if k not in ("verbosity", "n_jobs")
            })

            mlflow.log_metric(
                "auc_validacao", auc
            )

        return auc

    estudo = optuna.create_study(
        direction="maximize",
        sampler=optuna.samplers.TPESampler(seed=42)
    )

    estudo.optimize(
        objetivo_optuna,
        n_trials=n_trials
    )

    mlflow.log_metric(
        "melhor_auc_validacao",
        estudo.best_value
    )

print("MELHOR AUC OPTUNA:", estudo.best_value)
print("PARAMETROS:", estudo.best_params)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 9. Escolha do modelo e teste futuro
# MAGIC
# MAGIC O melhor algoritmo sera escolhido pela validacao.
# MAGIC Depois treinamos com janeiro-junho e avaliamos
# MAGIC apenas uma vez em julho-dezembro.

# COMMAND ----------

melhor_baseline = max(
    comparacoes,
    key=lambda item: item["auc"]
)

if estudo.best_value > melhor_baseline["auc"]:
    nome_vencedor = "LightGBM_Optuna"
    estimador_final = LGBMClassifier(
        **estudo.best_params,
        random_state=42,
        verbosity=-1,
        n_jobs=1
    )
else:
    nome_vencedor = melhor_baseline["modelo"]
    estimador_final = clone(
        modelos[nome_vencedor]
    )

primeiro_semestre = frame[
    frame["dia_prtc"] < "2025-07-01"
]

X_primeiro_semestre = primeiro_semestre[lista_features]
y_primeiro_semestre = primeiro_semestre["comprou_eletronico"]

modelo_final = criar_pipeline(
    estimador_final
)

with mlflow.start_run(
    run_name="Aula34_FINAL_teste_futuro"
):

    modelo_final.fit(
        X_primeiro_semestre,
        y_primeiro_semestre
    )

    probabilidades_teste = modelo_final.predict_proba(
        X_test
    )[:, 1]

    auc_teste = roc_auc_score(
        y_test,
        probabilidades_teste
    )

    acuracia_teste = accuracy_score(
        y_test,
        modelo_final.predict(X_test)
    )

    mlflow.log_params({
        "modelo_escolhido": nome_vencedor,
        "periodo_treino": "2025-01_2025-06",
        "periodo_teste": "2025-07_2025-12"
    })

    mlflow.log_metrics({
        "auc_teste_futuro": auc_teste,
        "accuracy_teste_futuro": acuracia_teste
    })

print("MODELO ESCOLHIDO:", nome_vencedor)
print("AUC TESTE FUTURO:", round(auc_teste, 4))
print("ACURACIA TESTE FUTURO:", round(acuracia_teste, 4))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 10. Interpretabilidade SHAP
# MAGIC
# MAGIC O grafico sera gerado para LightGBM.
# MAGIC Se outro algoritmo vencer, usamos um LightGBM
# MAGIC treinado separadamente para a demonstracao.
# MAGIC
# MAGIC Interpretacoes sao associacoes do modelo,
# MAGIC e nao provas de causalidade.

# COMMAND ----------

import shap
import matplotlib.pyplot as plt

if nome_vencedor == "LightGBM_Optuna":
    modelo_shap = modelo_final
else:
    modelo_shap = criar_pipeline(
        LGBMClassifier(
            **estudo.best_params,
            random_state=42,
            verbosity=-1,
            n_jobs=1
        )
    )

    modelo_shap.fit(
        X_primeiro_semestre,
        y_primeiro_semestre
    )

amostra = X_test.head(150)

matriz = modelo_shap.named_steps[
    "preprocessor"
].transform(amostra)

if hasattr(matriz, "toarray"):
    matriz = matriz.toarray()

estimador = modelo_shap.named_steps[
    "classificador"
]

valores_shap = shap.TreeExplainer(
    estimador
).shap_values(matriz)

if isinstance(valores_shap, list):
    valores_shap = valores_shap[1]

if np.asarray(valores_shap).ndim == 3:
    valores_shap = np.asarray(
        valores_shap
    )[:, :, 1]

nomes_features = modelo_shap.named_steps[
    "preprocessor"
].get_feature_names_out()

shap.summary_plot(
    valores_shap,
    matriz,
    feature_names=nomes_features,
    max_display=12,
    show=False
)

plt.tight_layout()
plt.show()

print("===== AULA 3.4 EXECUTADA =====")
print("MODELOS BASELINE:", len(modelos))
print("TRIALS OPTUNA:", n_trials)
print("MODELO ESCOLHIDO:", nome_vencedor)
print("MLFLOW: METRICAS REGISTRADAS")
print("SHAP: GRAFICO GERADO")
print("NENHUM MODELO PROMOVIDO PARA PRODUCAO")