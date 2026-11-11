# Databricks notebook source
# MAGIC %md
# MAGIC # Aula 4.4 - Endpoint e inferencia em tempo real
# MAGIC
# MAGIC Preparado com base no notebook 4.4 da Alura.
# MAGIC
# MAGIC Este notebook NAO cria endpoints, NAO altera aliases
# MAGIC e NAO envia requisicoes por padrao.
# MAGIC
# MAGIC Primeiro registre o modelo da Aula 4.2 no Unity Catalog,
# MAGIC crie o endpoint na interface Model Serving e aguarde READY.
# MAGIC
# MAGIC Autenticacao: Databricks SDK.
# MAGIC Nenhum token sera incluido no codigo ou nos logs.

# COMMAND ----------

import re
import time
import mlflow

from mlflow.models import get_model_info
from mlflow.tracking import MlflowClient
from databricks.sdk import WorkspaceClient

mlflow.set_registry_uri("databricks-uc")

dbutils.widgets.text("catalogo", "workspace")
dbutils.widgets.text("endpoint", "modelo_propensao")
dbutils.widgets.text("versao_modelo", "")

dbutils.widgets.dropdown(
    "enviar_cinco_testes",
    "nao",
    ["nao", "sim"]
)

dbutils.widgets.text(
    "confirmacao_envio",
    ""
)

catalogo = dbutils.widgets.get("catalogo").strip()
endpoint_nome = dbutils.widgets.get("endpoint").strip()
versao_texto = dbutils.widgets.get("versao_modelo").strip()

enviar = (
    dbutils.widgets.get("enviar_cinco_testes") == "sim"
)

confirmacao = dbutils.widgets.get(
    "confirmacao_envio"
).strip()

if not re.fullmatch(
    r"[A-Za-z_][A-Za-z0-9_]*",
    catalogo
):
    raise ValueError("Catalogo invalido")

if not re.fullmatch(
    r"[A-Za-z0-9][A-Za-z0-9_-]{0,62}",
    endpoint_nome
):
    raise ValueError("Nome de endpoint invalido")

nome_modelo = (
    f"{catalogo}.gold.propensao_compra_modelo"
)

client_ml = MlflowClient()

versoes = sorted([
    int(v.version)
    for v in client_ml.search_model_versions(
        f"name='{nome_modelo}'"
    )
])

if not versoes:
    raise RuntimeError(
        "Nenhuma versao registrada no Unity Catalog. "
        "Execute a Aula 4.2 na nuvem antes de continuar."
    )

print("MODELO:", nome_modelo)
print("VERSOES DISPONIVEIS:", versoes)

if (
    not versao_texto.isdigit()
    or int(versao_texto) not in versoes
):
    raise RuntimeError(
        "Preencha versao_modelo com uma versao listada acima"
    )

versao = int(versao_texto)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Validando a Signature
# MAGIC
# MAGIC O modelo da Aula 4.2 utiliza 16 features.
# MAGIC A inferencia precisa respeitar essas entradas.

# COMMAND ----------

uri = f"models:/{nome_modelo}/{versao}"

assinatura = get_model_info(uri).signature

if (
    assinatura is None
    or assinatura.inputs is None
):
    raise RuntimeError(
        "Modelo sem Signature. Revise a Aula 4.2."
    )

campos = assinatura.inputs.inputs

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

nomes = [
    campo.name
    for campo in campos
]

if (
    len(nomes) != 16
    or set(nomes) != set(esperadas)
):
    raise RuntimeError(
        "Signature diferente das 16 features da Aula 4.2. "
        f"Colunas encontradas: {nomes}"
    )

for campo in campos:

    tipo = str(
        campo.type
    ).lower().split(".")[-1]

    if (
        campo.name in numericas
        and tipo != "double"
    ):
        raise RuntimeError(
            f"Tipo inesperado: {campo.name}: {tipo}"
        )

    if (
        campo.name in indicadores
        and tipo not in ("integer", "long")
    ):
        raise RuntimeError(
            f"Tipo inesperado: {campo.name}: {tipo}"
        )

print("SIGNATURE APROVADA: 16 FEATURES")
print("ORDEM DAS COLUNAS:", nomes)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Verificando o endpoint
# MAGIC
# MAGIC Confirma o estado READY e a versao servida.
# MAGIC
# MAGIC Alterar o alias Champion nao atualiza
# MAGIC automaticamente um endpoint existente.

# COMMAND ----------

w = WorkspaceClient()

try:
    detalhes = w.serving_endpoints.get(
        name=endpoint_nome
    )

except Exception as erro:
    raise RuntimeError(
        "Endpoint nao encontrado, indisponivel ou sem permissao. "
        "Crie-o na interface Model Serving e aguarde Ready."
    ) from erro

estado = getattr(
    detalhes, "state", None
)

pronto = getattr(
    estado, "ready", None
)

valor_pronto = str(
    getattr(pronto, "value", pronto)
).upper()

if valor_pronto != "READY":
    raise RuntimeError(
        f"Endpoint ainda nao esta READY: {valor_pronto}"
    )

config = getattr(
    detalhes, "config", None
)

entidades = (
    getattr(config, "served_entities", None)
    or getattr(config, "served_models", None)
)

if not entidades:
    raise RuntimeError(
        "Nao foi possivel confirmar o modelo servido."
    )

identificacoes = []

for entidade in entidades:

    nome = (
        getattr(entidade, "entity_name", None)
        or getattr(entidade, "model_name", None)
    )

    v = (
        getattr(entidade, "entity_version", None)
        or getattr(entidade, "model_version", None)
    )

    identificacoes.append(
        (str(nome), str(v))
    )

if (
    len(identificacoes) != 1
    or identificacoes[0] != (
        nome_modelo, str(versao)
    )
):
    raise RuntimeError(
        "O endpoint nao serve exclusivamente a versao escolhida. "
        f"Configuracao encontrada: {identificacoes}"
    )

print("ENDPOINT VALIDADO:", endpoint_nome)
print("MODELO E VERSAO:", identificacoes[0])

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Criando cinco clientes ficticios
# MAGIC
# MAGIC Renda mensal expressa em milhares de reais.
# MAGIC Nenhum dado real de cliente sera utilizado.

# COMMAND ----------

regioes = [
    "nordeste",
    "sudeste",
    "sul",
    "norte",
    "centro_oeste"
]

clientes = []

for i in range(5):

    genero = (
        "f" if i % 2 == 0 else "m"
    )

    regiao = regioes[i]

    registro = {
        "idade_cliente": float(22 + 9 * i),

        "renda_mensal_k": float(
            round(2.5 + 2.2 * i, 2)
        ),

        "tempo_medio_clique_segundos": float(
            35 + 20 * i
        ),

        "media_interacoes_suporte": float(
            i % 3
        ),

        "media_cupons_ativos": float(
            1 + i % 3
        ),

        "media_score_nps_cliente": float(
            6 + i % 5
        ),

        "media_dias_inatividade": float(
            2 + 4 * i
        ),

        "total_gasto_acumulado_reais": float(
            100 + 450 * i
        ),

        "total_eventos_anteriores": float(
            3 + 2 * i
        ),

        "genero_cliente_f": int(
            genero == "f"
        ),

        "genero_cliente_m": int(
            genero == "m"
        ),

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

    if set(registro) != set(nomes):
        raise RuntimeError(
            "Registro sintetico diferente da Signature"
        )

    clientes.append({
        campo: registro[campo]
        for campo in nomes
    })

print("CLIENTES SINTETICOS:", len(clientes))
print("REQUISICOES HABILITADAS:", enviar)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Predicao em tempo real
# MAGIC
# MAGIC Para executar:
# MAGIC
# MAGIC enviar_cinco_testes = sim
# MAGIC
# MAGIC confirmacao_envio = ENVIAR 5 TESTES
# MAGIC
# MAGIC Por padrao, nenhuma requisicao e enviada.

# COMMAND ----------

if not enviar:

    print(
        "MODO SEGURO: NENHUMA REQUISICAO ENVIADA"
    )

else:

    if confirmacao != "ENVIAR 5 TESTES":
        raise RuntimeError(
            "Nenhum envio realizado. "
            "Preencha confirmacao_envio com ENVIAR 5 TESTES."
        )

    for posicao, cliente in enumerate(
        clientes, 1
    ):

        inicio = time.perf_counter()

        try:
            resposta = w.serving_endpoints.query(
                name=endpoint_nome,
                dataframe_records=[cliente]
            )

        except Exception as erro:
            raise RuntimeError(
                f"Falha na requisicao do cliente {posicao}. "
                "Confira status, permissoes e compatibilidade."
            ) from erro

        ms = (
            time.perf_counter() - inicio
        ) * 1000

        predicoes = getattr(
            resposta, "predictions", None
        )

        if (
            predicoes is None
            or len(predicoes) != 1
        ):
            raise RuntimeError(
                "Resposta inesperada do endpoint"
            )

        previsao = predicoes[0]

        if previsao not in (0, 1):
            raise RuntimeError(
                f"Classe inesperada: {previsao}"
            )

        print(
            f"CLIENTE FICTICIO {posicao}: "
            f"PREDICAO={previsao} "
            f"LATENCIA_CLIENTE_MS={ms:.0f}"
        )

    print(
        "CINCO REQUISICOES CONCLUIDAS"
    )

print("NENHUM TOKEN EXIBIDO OU SALVO")
print("NENHUM ENDPOINT CRIADO OU ALTERADO")
print("NENHUM ALIAS MODIFICADO")