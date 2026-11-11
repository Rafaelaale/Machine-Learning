from pathlib import Path
from collections import Counter
from datetime import datetime
import ast
import csv
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "material-alura" / "6123-alura-ml-databricks" / "aula_1"
DATA = ROOT / "dados" / "upload_bronze"
NOTE = ROOT / "notebooks" / "aula_01_ingestao"
REPORT = ROOT / "relatorios" / "aula_projeto_ingestao.txt"

for pasta in (DATA, NOTE, REPORT.parent):
    pasta.mkdir(parents=True, exist_ok=True)


def hash_arquivo(path):
    h = hashlib.sha256()
    with path.open("rb") as arquivo:
        for bloco in iter(lambda: arquivo.read(1024 * 1024), b""):
            h.update(bloco)
    return h.hexdigest()


print("\n===== 1. VALIDANDO DATASETS ORIGINAIS =====")

arquivos = {
    "eventos": ("base_bronze_eventos.csv", ";", 20000, 5),
    "produtos": ("base_dim_produtos.csv", ",", 15, 4),
}

dados = {}

for chave, (nome, separador, esperado, colunas) in arquivos.items():

    origem = REF / nome

    if not origem.is_file():
        raise FileNotFoundError(f"Arquivo ausente: {origem}")

    with origem.open(encoding="utf-8-sig", newline="") as arquivo:
        leitor = csv.DictReader(arquivo, delimiter=separador)

        if not leitor.fieldnames or len(leitor.fieldnames) != colunas:
            raise ValueError(f"Cabecalho inesperado: {nome}")

        linhas = list(leitor)

    if len(linhas) != esperado:
        raise ValueError(
            f"{nome}: esperado {esperado}, encontrado {len(linhas)}"
        )

    dados[chave] = linhas

    destino = DATA / nome

    if destino.exists():
        if hash_arquivo(origem) != hash_arquivo(destino):
            raise RuntimeError(
                f"Copia de upload diferente do original: {destino}"
            )
        print("PRESERVADO:", nome)
    else:
        shutil.copy2(origem, destino)
        print("COPIADO:", nome)

eventos = dados["eventos"]
produtos = dados["produtos"]

ids_eventos = [evento["id_evento"] for evento in eventos]
ids_produtos = {produto["id_produto"] for produto in produtos}

if len(set(ids_eventos)) != len(eventos):
    raise ValueError("Existem IDs de eventos duplicados")

if len(ids_produtos) != len(produtos):
    raise ValueError("Existem IDs de produtos duplicados")

jsons = [
    json.loads(evento["dados_origem_json"])
    for evento in eventos
]

if not all(
    isinstance(payload, dict)
    and payload.get("id_produto") in ids_produtos
    for payload in jsons
):
    raise ValueError("JSON invalido ou produto nao encontrado")

if any(not produto["preco_reais"].strip() for produto in produtos):
    raise ValueError("Produto sem preco")

tipos = Counter(evento["tipo_evento"] for evento in eventos)

print("EVENTOS:", len(eventos))
print("PRODUTOS:", len(produtos))
print("JSONS VALIDOS:", len(jsons))
print("IDS UNICOS:", len(set(ids_eventos)))
print("COMPRAS FINALIZADAS:", tipos["finalizar_compra"])


def markdown(conteudo):
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": conteudo.strip().splitlines(True),
    }


def codigo(conteudo):
    conteudo = conteudo.strip()
    ast.parse(conteudo)

    return {
        "cell_type": "code",
        "metadata": {},
        "execution_count": None,
        "outputs": [],
        "source": conteudo.splitlines(True),
    }


print("\n===== 2. MONTANDO NOTEBOOK DATABRICKS =====")

celulas = [

    markdown("""
# Projeto de Ingestão — Bronze, Silver e Gold

Curso Databricks: Engenharia de Machine Learning e MLOps.

## Antes de executar no Databricks

1. Confirme que o catálogo `workspace` está disponível.
2. Crie o esquema `bronze`, se necessário.
3. Crie o Volume `workspace.bronze.raw`.
4. Envie os dois CSVs da pasta local `dados/upload_bronze`.
5. Importe este notebook e execute as células na ordem.

As tabelas existentes não serão sobrescritas.
"""),

    codigo("""
import re

from pyspark.sql import functions as F
from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    DecimalType,
    IntegerType
)

dbutils.widgets.text("catalogo", "workspace")
dbutils.widgets.text("volume", "raw")

catalogo = dbutils.widgets.get("catalogo").strip()
volume = dbutils.widgets.get("volume").strip()

for valor in (catalogo, volume):
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", valor):
        raise ValueError("Identificador invalido")

origem = f"/Volumes/{catalogo}/bronze/{volume}"

t_eventos = f"{catalogo}.bronze.tabela_eventos_bronze"
t_produtos = f"{catalogo}.bronze.dim_produtos"
t_silver = f"{catalogo}.silver.tabela_eventos_silver"
t_gold = f"{catalogo}.gold.base_eventos_produto_gold"

print("CATALOGO:", catalogo)
print("VOLUME:", origem)
print("BRONZE:", t_eventos, t_produtos)
print("SILVER:", t_silver)
print("GOLD:", t_gold)
"""),

    markdown("""
## Etapa 1 — Verificação dos arquivos no Volume

O notebook interrompe a execução caso os CSVs ainda não tenham
sido enviados ao Databricks.
"""),

    codigo("""
esperados = {
    "base_bronze_eventos.csv",
    "base_dim_produtos.csv"
}

try:
    encontrados = {
        item.name.rstrip("/")
        for item in dbutils.fs.ls(origem)
    }
except Exception as erro:
    raise RuntimeError(
        f"Volume indisponivel: {origem}. "
        "Crie o Volume e envie os CSVs."
    ) from erro

faltando = esperados - encontrados

if faltando:
    raise FileNotFoundError(
        f"Arquivos ausentes no Volume: {sorted(faltando)}"
    )

print("VOLUME VALIDADO: 2/2 ARQUIVOS")
"""),

    markdown("""
## Etapa 2 — Leitura dos CSVs com esquema explícito

A base de eventos utiliza ponto e vírgula.

A dimensão de produtos utiliza vírgula.

O Spark será configurado para interpretar as aspas escapadas
do JSON armazenado no CSV.
"""),

    codigo("""
schema_eventos = StructType([
    StructField("id_evento", StringType(), True),
    StructField("id_usuario", StringType(), True),
    StructField("tipo_evento", StringType(), True),
    StructField("timestamp_registro", StringType(), True),
    StructField("dados_origem_json", StringType(), True)
])

schema_produtos = StructType([
    StructField("id_produto", StringType(), True),
    StructField("nome_produto", StringType(), True),
    StructField("categoria", StringType(), True),
    StructField("preco_reais", DecimalType(10, 2), True)
])

df_eventos = (
    spark.read
    .option("header", "true")
    .option("sep", ";")
    .option("mode", "FAILFAST")
    .option("quote", '"')
    .option("escape", '"')
    .schema(schema_eventos)
    .csv(origem + "/base_bronze_eventos.csv")
)

df_produtos = (
    spark.read
    .option("header", "true")
    .option("sep", ",")
    .option("mode", "FAILFAST")
    .schema(schema_produtos)
    .csv(origem + "/base_dim_produtos.csv")
)

n_eventos = df_eventos.count()
n_produtos = df_produtos.count()

if (n_eventos, n_produtos) != (20000, 15):
    raise ValueError(
        f"Contagens incorretas: {n_eventos}, {n_produtos}"
    )

if df_eventos.select("id_evento").distinct().count() != n_eventos:
    raise ValueError("Eventos duplicados")

if df_produtos.select("id_produto").distinct().count() != n_produtos:
    raise ValueError("Produtos duplicados")

if df_produtos.filter(
    F.col("preco_reais").isNull()
).limit(1).count():
    raise ValueError("Preco invalido")

id_json = F.get_json_object(
    F.col("dados_origem_json"), "$.id_produto"
)

if df_eventos.filter(id_json.isNull()).limit(1).count():
    raise ValueError("JSON invalido ou sem id_produto")

print("EVENTOS VALIDADOS:", n_eventos)
print("PRODUTOS VALIDADOS:", n_produtos)
"""),

    markdown("""
## Etapa 3 — Criação das camadas e tabelas Bronze

A criação preserva tabelas existentes.

Se uma tabela preexistente tiver contagem ou colunas diferentes,
o notebook interromperá a execução para evitar sobrescritas.
"""),

    codigo("""
for esquema in ("bronze", "silver", "gold"):
    spark.sql(
        f"CREATE SCHEMA IF NOT EXISTS {catalogo}.{esquema}"
    )


def salvar_sem_sobrescrever(df, nome, esperado):

    if spark.catalog.tableExists(nome):

        existente = spark.table(nome)
        quantidade = existente.count()

        if quantidade != esperado:
            raise RuntimeError(
                f"Tabela existente divergente: {nome}"
            )

        if set(existente.columns) != set(df.columns):
            raise RuntimeError(
                f"Colunas diferentes na tabela: {nome}"
            )

        print("PRESERVADA:", nome, quantidade)
        return existente

    (
        df.write
        .format("delta")
        .mode("errorifexists")
        .saveAsTable(nome)
    )

    print("CRIADA:", nome, esperado)
    return spark.table(nome)


bronze_eventos = salvar_sem_sobrescrever(
    df_eventos, t_eventos, n_eventos
)

bronze_produtos = salvar_sem_sobrescrever(
    df_produtos, t_produtos, n_produtos
)

print("CAMADA BRONZE CONFERIDA")
"""),

    markdown("""
## Etapa 4 — Silver: tratamento e estruturação do JSON

O timestamp será convertido.

Os campos JSON serão transformados em colunas.

Não será realizada limpeza indiscriminada das aspas,
pois o leitor CSV já interpreta o escape do arquivo.
"""),

    codigo("""
schema_json = StructType([
    StructField("id_produto", StringType(), True),
    StructField("dispositivo", StringType(), True),
    StructField("sistema_operacional", StringType(), True),
    StructField("origem_trafego", StringType(), True),
    StructField("idade", IntegerType(), True),
    StructField("genero", StringType(), True),
    StructField("renda_mensal_estimada_k", DecimalType(18, 2), True),
    StructField("regiao", StringType(), True),
    StructField("tempo_clique_segundos", IntegerType(), True),
    StructField("interacoes_chat_suporte", IntegerType(), True),
    StructField("cupons_ativos_conta", IntegerType(), True),
    StructField("score_satisfacao_nps", IntegerType(), True),
    StructField("dias_desde_ultima_visita", IntegerType(), True)
])

tratado = (
    bronze_eventos
    .withColumn(
        "timestamp_registro",
        F.to_timestamp("timestamp_registro")
    )
    .withColumn(
        "payload",
        F.from_json(
            F.col("dados_origem_json"),
            schema_json
        )
    )
)

invalidos = tratado.filter(
    F.col("timestamp_registro").isNull()
    | F.col("payload.id_produto").isNull()
).limit(1).count()

if invalidos:
    raise ValueError(
        "Existem timestamps ou JSONs invalidos"
    )

df_silver = tratado.select(
    "id_evento",
    "id_usuario",
    "tipo_evento",
    "timestamp_registro",
    "payload.*"
).dropDuplicates(["id_evento"])

if df_silver.count() != n_eventos:
    raise RuntimeError("Perda de registros na Silver")

silver = salvar_sem_sobrescrever(
    df_silver, t_silver, n_eventos
)

print("CAMADA SILVER CONFERIDA")
"""),

    markdown("""
## Etapa 5 — Gold: integração com a dimensão de produtos

A tabela Gold será criada pelo JOIN entre a Silver
e a dimensão de produtos existente na Bronze.

O `id_produto` permanece na Gold para rastreabilidade.
"""),

    codigo("""
df_gold = (
    silver.alias("s")
    .join(
        bronze_produtos.alias("p"),
        F.col("s.id_produto") == F.col("p.id_produto"),
        "inner"
    )
    .select(
        "s.*",
        F.col("p.categoria"),
        F.col("p.preco_reais")
    )
)

n_gold = df_gold.count()

if n_gold != n_eventos:
    raise RuntimeError(
        f"JOIN divergente: {n_gold} de {n_eventos}"
    )

gold = salvar_sem_sobrescrever(
    df_gold, t_gold, n_gold
)

print("CAMADA GOLD CONFERIDA:", gold.count())
"""),

    markdown("""
## Etapa 6 — Auditoria final no Databricks

Confirma a existência e as contagens das quatro
tabelas Delta criadas ou reutilizadas.
"""),

    codigo("""
tabelas = [
    (t_eventos, 20000),
    (t_produtos, 15),
    (t_silver, 20000),
    (t_gold, 20000)
]

for tabela, esperado in tabelas:

    encontrado = spark.table(tabela).count()

    if encontrado != esperado:
        raise RuntimeError(
            f"Falha na validacao: {tabela}"
        )

    print("VALIDADA:", tabela, encontrado)

display(spark.table(t_gold).limit(20))

print("BRONZE, SILVER E GOLD: VALIDACAO CONCLUIDA")
""")
]

notebook = {
    "cells": celulas,
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "name": "python"
        }
    },
    "nbformat": 4,
    "nbformat_minor": 5
}

destino_notebook = NOTE / "03_ingestao_bronze_silver_gold.ipynb"

if destino_notebook.exists():
    json.loads(destino_notebook.read_text(encoding="utf-8"))
    print("NOTEBOOK EXISTENTE PRESERVADO")
else:
    destino_notebook.write_text(
        json.dumps(notebook, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8"
    )
    print("NOTEBOOK CRIADO:", destino_notebook)

print("\n===== 3. SALVANDO RELATORIO =====")

relatorio = [
    "AUDITORIA LOCAL - PROJETO DE INGESTAO",
    str(datetime.now()),
    "",
    f"Eventos: {len(eventos)}",
    f"Produtos: {len(produtos)}",
    f"IDs de eventos unicos: {len(set(ids_eventos))}",
    f"JSONs validos: {len(jsons)}",
    f"Compras finalizadas: {tipos['finalizar_compra']}",
    "",
    "CSV eventos: separador ;",
    "CSV produtos: separador ,",
    "Integridade referencial verificada",
    "",
    "Notebook Bronze, Silver e Gold preparado.",
    "Execucao remota no Databricks pendente.",
    "Nenhuma tabela remota foi alterada.",
    "Nenhuma publicacao realizada."
]

REPORT.write_text(
    "\n".join(relatorio) + "\n",
    encoding="utf-8"
)

print("RELATORIO:", REPORT)

print("\n===== RESULTADO FINAL =====")
print("EVENTOS VALIDADOS:", len(eventos))
print("PRODUTOS VALIDADOS:", len(produtos))
print("JSONS VALIDADOS:", len(jsons))
print("NOTEBOOK:", destino_notebook)
print("ARQUIVOS PARA UPLOAD:", DATA)
print("NENHUM DEPLOY OU PUBLICACAO.")
