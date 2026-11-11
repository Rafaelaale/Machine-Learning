# Databricks notebook source
# MAGIC %md
# MAGIC # Aula 4.3 - Deploy Batch com MLflow
# MAGIC
# MAGIC Modelo: propensao_compra_modelo
# MAGIC Catalogo: Unity Catalog
# MAGIC
# MAGIC Conteudo:
# MAGIC - Consulta de versoes
# MAGIC - Alias Champion
# MAGIC - Validacao de Signature
# MAGIC - Inferencia Spark UDF
# MAGIC - Predicao de 13 clientes
# MAGIC
# MAGIC Nenhum alias sera alterado por padrao.
# MAGIC Nenhuma tabela sera gravada por padrao.
# MAGIC
# MAGIC Execute somente depois de registrar o
# MAGIC modelo da Aula 4.2 no Databricks.

# COMMAND ----------

import re
from datetime import date

import mlflow
import mlflow.pyfunc

from mlflow.tracking import MlflowClient
from mlflow.models import get_model_info
from mlflow.exceptions import MlflowException

from pyspark.sql import functions as F

from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    DateType,
    DoubleType,
    IntegerType
)

mlflow.set_registry_uri("databricks-uc")

dbutils.widgets.text("catalogo", "workspace")
dbutils.widgets.text("versao_modelo", "")

dbutils.widgets.dropdown(
    "atribuir_champion",
    "nao",
    ["nao", "sim"]
)

dbutils.widgets.text(
    "confirmacao_champion",
    ""
)

dbutils.widgets.dropdown(
    "salvar_predicoes",
    "nao",
    ["nao", "sim"]
)

catalogo = dbutils.widgets.get(
    "catalogo"
).strip()

if not re.fullmatch(
    r"[A-Za-z_][A-Za-z0-9_]*",
    catalogo
):
    raise ValueError("Nome de catalogo invalido")

nome_modelo = (
    f"{catalogo}.gold.propensao_compra_modelo"
)

cliente = MlflowClient()

print("===== UNITY CATALOG =====")
print("MODELO:", nome_modelo)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Consultando as versoes
# MAGIC
# MAGIC A versao mais recente nao significa
# MAGIC necessariamente o melhor modelo.
# MAGIC
# MAGIC Antes de utilizar Champion, conferir
# MAGIC metricas e aprovacao da versao.

# COMMAND ----------

try:
    cliente.get_registered_model(
        nome_modelo
    )

except MlflowException as erro:

    raise RuntimeError(
        "Modelo nao encontrado ou sem permissao: "
        + nome_modelo
        + ". Confirme o registro da Aula 4.2."
    ) from erro

versoes = list(
    cliente.search_model_versions(
        f"name='{nome_modelo}'"
    )
)

if not versoes:
    raise RuntimeError(
        "Modelo ainda nao possui versoes registradas"
    )

versoes = sorted(
    versoes,
    key=lambda v: int(v.version),
    reverse=True
)

disponiveis = {
    int(v.version) for v in versoes
}

for item in versoes:

    print(
        "VERSAO:",
        item.version,
        "ESTADO:",
        getattr(item, "status", "nao informado")
    )

try:
    atual = cliente.get_model_version_by_alias(
        nome_modelo,
        "Champion"
    )

    print(
        "CHAMPION ATUAL:",
        atual.version
    )

except MlflowException as erro:

    mensagem = str(erro).upper()

    if (
        "RESOURCE_DOES_NOT_EXIST" in mensagem
        or "NOT_FOUND" in mensagem
    ):
        print("CHAMPION AINDA NAO DEFINIDO")
    else:
        raise

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Selecionando a versao
# MAGIC
# MAGIC Preencha o widget versao_modelo
# MAGIC com uma versao existente.
# MAGIC
# MAGIC Sem essa escolha, o processamento
# MAGIC sera interrompido por seguranca.

# COMMAND ----------

escolhida = dbutils.widgets.get(
    "versao_modelo"
).strip()

if (
    not escolhida.isdigit()
    or int(escolhida) not in disponiveis
):

    raise RuntimeError(
        "Informe no widget versao_modelo "
        "uma versao existente listada acima."
    )

versao = int(escolhida)

uri_versao = (
    f"models:/{nome_modelo}/{versao}"
)

info = get_model_info(uri_versao)

if (
    info.signature is None
    or info.signature.inputs is None
):
    raise RuntimeError(
        "Modelo sem Signature. "
        "Revise o registro da Aula 4.2."
    )

entradas = info.signature.inputs.inputs

colunas_assinatura = [
    entrada.name
    for entrada in entradas
]

if (
    not colunas_assinatura
    or any(
        nome is None
        for nome in colunas_assinatura
    )
):
    raise RuntimeError(
        "Signature sem nomes de colunas validos"
    )

if len(colunas_assinatura) != len(
    set(colunas_assinatura)
):
    raise RuntimeError(
        "Signature com nomes duplicados"
    )

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Validando as features da Aula 4.2
# MAGIC
# MAGIC Sao esperadas 16 features:
# MAGIC 9 numericas e 7 indicadores categoricos.

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

indicadores = [
    "genero_cliente_f",
    "genero_cliente_m",
    "regiao_cliente_centro_oeste",
    "regiao_cliente_nordeste",
    "regiao_cliente_norte",
    "regiao_cliente_sudeste",
    "regiao_cliente_sul"
]

esperadas = numericas + indicadores

if set(colunas_assinatura) != set(esperadas):

    raise RuntimeError(
        "Signature diferente da Aula 4.2. "
        "Nao e seguro executar a inferencia. "
        f"Colunas encontradas: {colunas_assinatura}"
    )

def tipo_assinatura(campo):

    return str(
        campo.type
    ).lower().split(".")[-1]

for campo in entradas:

    tipo = tipo_assinatura(campo)

    if (
        campo.name in numericas
        and tipo != "double"
    ):
        raise RuntimeError(
            f"Tipo incorreto: {campo.name}: {tipo}"
        )

    if (
        campo.name in indicadores
        and tipo not in ("integer", "long")
    ):
        raise RuntimeError(
            f"Tipo incorreto: {campo.name}: {tipo}"
        )

print("SIGNATURE VALIDADA")
print("FEATURES:", len(colunas_assinatura))
print("ORDEM:", colunas_assinatura)
print("VERSAO SELECIONADA:", versao)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Criando 13 clientes ficticios
# MAGIC
# MAGIC Sao dados exclusivamente demonstrativos.
# MAGIC
# MAGIC O Spark recebera um schema explicito.
# MAGIC ID e data nao entram nas features do modelo.

# COMMAND ----------

schema = StructType(
    [
        StructField(
            "id_usuario",
            StringType(),
            False
        ),
        StructField(
            "dia_prtc",
            DateType(),
            False
        )
    ]
    + [
        StructField(
            nome,
            DoubleType(),
            False
        )
        for nome in numericas
    ]
    + [
        StructField(
            nome,
            IntegerType(),
            False
        )
        for nome in indicadores
    ]
)

regioes = [
    "nordeste",
    "sudeste",
    "sul",
    "norte",
    "centro_oeste"
]

linhas = []

for i in range(13):

    regiao = regioes[
        i % len(regioes)
    ]

    genero = (
        "f" if i % 2 == 0 else "m"
    )

    dados = {
        "id_usuario": f"usr_batch_{i + 1:02d}",
        "dia_prtc": date(2026, 7, 5),

        "idade_cliente": float(22 + i * 4),
        "renda_mensal_k": float(1.5 + i * 0.35),
        "tempo_medio_clique_segundos": float(80 + i * 5),
        "media_interacoes_suporte": float(i % 3),
        "media_cupons_ativos": float(1 + i % 4),
        "media_score_nps_cliente": float(6 + i % 5),
        "media_dias_inatividade": float(1 + i % 6),
        "total_gasto_acumulado_reais": float(200 + i * 250),
        "total_eventos_anteriores": float(i + 2),

        "genero_cliente_f": int(genero == "f"),
        "genero_cliente_m": int(genero == "m"),

        "regiao_cliente_centro_oeste": int(
            regiao == "centro_oeste"
        ),
        "regiao_cliente_nordeste": int(
            regiao == "nordeste"
        ),
        "regiao_cliente_norte": int(
            regiao == "norte"
        ),
        "regiao_cliente_sudeste": int(
            regiao == "sudeste"
        ),
        "regiao_cliente_sul": int(
            regiao == "sul"
        )
    }

    linhas.append(dados)

novos_clientes = spark.createDataFrame(
    linhas,
    schema=schema
)

novos_clientes = novos_clientes.select(
    "id_usuario",
    "dia_prtc",
    *colunas_assinatura
)

if novos_clientes.count() != 13:
    raise RuntimeError(
        "Quantidade de clientes ficticios incorreta"
    )

# Ajusta apenas o tipo int/long previsto na Signature.

for campo in entradas:

    nome = campo.name
    tipo = tipo_assinatura(campo)

    tipo_real = (
        novos_clientes.schema[nome]
        .dataType.simpleString()
    )

    if tipo == "long" and tipo_real == "int":

        novos_clientes = novos_clientes.withColumn(
            nome,
            F.col(nome).cast("long")
        )

    elif tipo == "integer" and tipo_real == "int":

        pass

    elif tipo != tipo_real:

        raise RuntimeError(
            f"Tipo incompatível: {nome}. "
            f"Spark={tipo_real}, Signature={tipo}"
        )

print("13 CLIENTES FICTICIOS VALIDADOS")

display(
    novos_clientes.limit(13)
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Executando a inferencia batch
# MAGIC
# MAGIC mlflow.pyfunc.spark_udf utiliza a
# MAGIC versao escolhida explicitamente.
# MAGIC
# MAGIC As colunas sao entregues na ordem
# MAGIC da assinatura do modelo.

# COMMAND ----------

try:

    predict_udf = mlflow.pyfunc.spark_udf(
        spark,
        model_uri=uri_versao,
        result_type="long"
    )

    previsoes = (
        novos_clientes

        .withColumn(
            "vai_comprar",

            predict_udf(
                F.struct(
                    *[
                        F.col(c)
                        for c in colunas_assinatura
                    ]
                )
            ).cast("int")
        )

        .select(
            "id_usuario",
            "dia_prtc",
            "vai_comprar"
        )

        .withColumn(
            "versao_modelo",
            F.lit(versao)
        )
    )

    saida = previsoes.collect()

except Exception as erro:

    raise RuntimeError(
        "Falha ao executar o batch. "
        "Verifique as bibliotecas do modelo "
        "e o suporte a Spark UDF neste workspace. "
        "Nenhum alias foi alterado."
    ) from erro

if (
    len(saida) != 13
    or any(
        registro["vai_comprar"] not in (0, 1)
        for registro in saida
    )
):
    raise RuntimeError(
        "Resultado batch inesperado. "
        "Nenhum alias foi alterado."
    )

print("===== RESULTADO BATCH =====")
print("MODELO:", nome_modelo)
print("VERSAO:", versao)
print("PREDICOES:", len(saida))

display(
    previsoes.orderBy("id_usuario")
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6. Alias Champion
# MAGIC
# MAGIC ALTERACAO DESATIVADA POR PADRAO.
# MAGIC
# MAGIC Para atribuir:
# MAGIC 1. Revisar metricas da versao selecionada.
# MAGIC 2. Definir atribuir_champion = sim.
# MAGIC 3. Digitar CHAMPION VERSAO N no widget
# MAGIC    confirmacao_champion.
# MAGIC
# MAGIC Substituir N pela versao escolhida.

# COMMAND ----------

solicitar_alias = (
    dbutils.widgets.get(
        "atribuir_champion"
    ) == "sim"
)

confirmacao = dbutils.widgets.get(
    "confirmacao_champion"
).strip()

if solicitar_alias:

    esperado = (
        f"CHAMPION VERSAO {versao}"
    )

    if confirmacao != esperado:

        raise RuntimeError(
            "Alias NAO alterado. "
            "Para confirmar, informe exatamente: "
            + esperado
        )

    cliente.set_registered_model_alias(
        name=nome_modelo,
        alias="Champion",
        version=str(versao)
    )

    confirmado = (
        cliente.get_model_version_by_alias(
            nome_modelo,
            "Champion"
        )
    )

    if int(confirmado.version) != versao:

        raise RuntimeError(
            "Falha ao confirmar o novo Champion"
        )

    print(
        "CHAMPION ATRIBUIDO:",
        versao
    )

else:

    print(
        "CHAMPION PRESERVADO: "
        "nenhuma alteracao solicitada"
    )

# COMMAND ----------

# MAGIC %md
# MAGIC ## 7. Persistencia opcional no Delta Lake
# MAGIC
# MAGIC Por padrao, mostra as predicoes
# MAGIC sem criar tabela.
# MAGIC
# MAGIC Se habilitada, cria tabela exclusiva
# MAGIC para a versao selecionada.
# MAGIC Nunca utiliza overwrite.

# COMMAND ----------

if (
    dbutils.widgets.get(
        "salvar_predicoes"
    ) == "sim"
):

    destino = (
        f"{catalogo}.gold."
        f"predicoes_batch_aula43_v{versao}"
    )

    if spark.catalog.tableExists(destino):

        raise RuntimeError(
            "Tabela ja existe. "
            "Nao sera sobrescrita: "
            + destino
        )

    (
        previsoes.write
        .format("delta")
        .mode("errorifexists")
        .saveAsTable(destino)
    )

    print(
        "PREDICOES SALVAS:",
        destino
    )

else:

    print(
        "PREDICOES NAO GRAVADAS"
    )

print("===== AULA 4.3 EXECUTADA =====")
print("MODELO:", nome_modelo)
print("VERSAO:", versao)
print("13 CLIENTES FICTICIOS")
print("NENHUM ENDPOINT CRIADO")
print("NENHUM JOB AUTOMATICO CRIADO")