from pathlib import Path
import csv
import json

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "material-alura/6123-alura-ml-databricks"
DEST = ROOT / "notebooks/aula_02_feature_store"
NOTAS = ROOT / "aulas/aula_feature_store.md"

DEST.mkdir(parents=True, exist_ok=True)
NOTAS.parent.mkdir(parents=True, exist_ok=True)

print("\n===== 1. VALIDANDO MATERIAL ALURA =====")

original = REF / "aula_2/aula_2_2_features_databricks.ipynb"
dados = REF / "aula_1/iris_dataset.csv"

nb_original = json.loads(original.read_text(encoding="utf-8-sig"))

with dados.open(encoding="utf-8-sig", newline="") as f:
    leitor = csv.DictReader(f)
    linhas = list(leitor)

colunas = {
    "sepal_length", "sepal_width",
    "petal_length", "petal_width", "species"
}

if len(linhas) != 150 or set(linhas[0]) != colunas:
    raise RuntimeError("Dataset Iris diferente do esperado")

especies = sorted(set(linha["species"] for linha in linhas))

print("NOTEBOOK ORIGINAL: VALIDADO")
print("REGISTROS IRIS:", len(linhas))
print("ESPECIES:", len(especies))
print("CELULAS ORIGINAIS:", len(nb_original["cells"]))

def md(texto):
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": texto.strip().splitlines(True)
    }

def code(texto):
    return {
        "cell_type": "code",
        "metadata": {},
        "execution_count": None,
        "outputs": [],
        "source": texto.strip().splitlines(True)
    }

print("\n===== 2. PREPARANDO NOTEBOOK FEATURE STORE =====")

celulas = [
    md("""
# Aula — Feature Store no Databricks

Versão preparada a partir do material da Alura.

Objetivos:
1. Verificar o catálogo e a tabela Iris.
2. Construir identificadores para as flores.
3. Separar as quatro features da variável `species`.
4. Registrar a Feature Table, se ainda não existir.
5. Preparar a característica `petal_ratio`.

Execute as células no Databricks Free Edition.
"""),

    code("""
from pyspark.sql import functions as F
from pyspark.sql.window import Window

dbutils.widgets.text("catalogo", "workspace")

catalogo = dbutils.widgets.get("catalogo").strip()

import re
if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", catalogo):
    raise ValueError("Catalogo invalido")

tabela_iris = f"{catalogo}.default.iris_dataset"
tabela_features = f"{catalogo}.default.iris_features_table"

print("ORIGEM:", tabela_iris)
print("DESTINO:", tabela_features)

if not spark.catalog.tableExists(tabela_iris):
    raise RuntimeError(
        "Tabela Iris ausente. Importe iris_dataset.csv "
        "no catalogo antes de continuar."
    )

df_iris = spark.table(tabela_iris)

colunas = [
    "sepal_length", "sepal_width",
    "petal_length", "petal_width", "species"
]

faltando = set(colunas) - set(df_iris.columns)

if faltando:
    raise RuntimeError(f"Colunas ausentes: {faltando}")

quantidade = df_iris.count()

if quantidade != 150:
    raise RuntimeError(
        f"Esperados 150 registros, encontrados {quantidade}"
    )

print("DATASET IRIS VALIDADO:", quantidade)
display(df_iris.limit(5))
"""),

    md("""
## Criando a chave da Feature Store

A ordenação usa os dados das flores, evitando a ordenação
arbitrária do exemplo original.

Se houver linhas idênticas, seus IDs podem ser intercambiados
entre execuções. Não utilize esse método para identificar
entidades reais em produção.
"""),

    code("""
ordenacao = [
    F.col("sepal_length"),
    F.col("sepal_width"),
    F.col("petal_length"),
    F.col("petal_width"),
    F.col("species")
]

janela = Window.orderBy(*ordenacao)

df_identificado = df_iris.withColumn(
    "id_flor",
    F.concat(
        F.lit("flor_"),
        F.row_number().over(janela).cast("string")
    )
)

df_features = df_identificado.select(
    "id_flor",
    "sepal_length",
    "sepal_width",
    "petal_length",
    "petal_width"
)

if "species" in df_features.columns:
    raise RuntimeError("Target indevidamente incluido")

if df_features.select("id_flor").distinct().count() != 150:
    raise RuntimeError("Chaves duplicadas")

print("FEATURES PREPARADAS:", df_features.columns)
print("TARGET SPECIES: EXCLUIDO")
display(df_features.limit(10))
"""),

    md("""
## Registrando no Unity Catalog

Esta etapa cria a tabela somente se ela não existir.

Se já houver uma Feature Table, o código a preserva.
O Databricks precisa permitir o uso do FeatureEngineeringClient.
"""),

    code("""
try:
    from databricks.feature_engineering import FeatureEngineeringClient
except ImportError as erro:
    raise RuntimeError(
        "Biblioteca databricks-feature-engineering ausente. "
        "Instale-a no notebook com %pip e reinicie o Python."
    ) from erro

fe = FeatureEngineeringClient()

if spark.catalog.tableExists(tabela_features):

    existente = spark.table(tabela_features)

    if existente.count() != 150:
        raise RuntimeError(
            "Feature Table existente possui contagem diferente"
        )

    obrigatorias = set(df_features.columns)

    if not obrigatorias.issubset(set(existente.columns)):
        raise RuntimeError(
            "Feature Table existente tem esquema incompatível"
        )

    print("FEATURE TABLE EXISTENTE PRESERVADA")

else:

    fe.create_table(
        name=tabela_features,
        primary_keys=["id_flor"],
        df=df_features,
        schema=df_features.schema,
        description="Features morfologicas do dataset Iris."
    )

    print("FEATURE TABLE CRIADA")

display(spark.table(tabela_features).limit(10))
"""),

    md("""
## Preparando a feature petal_ratio

Calcula a razão entre comprimento e largura da pétala.

Esta etapa é somente de visualização: não atualiza nem
remove colunas da tabela original.
"""),

    code("""
df_atual = spark.table(tabela_features)

df_ratio = df_atual.select(
    "id_flor",
    F.when(
        F.col("petal_width") > 0,
        F.col("petal_length") / F.col("petal_width")
    ).alias("petal_ratio")
)

if df_ratio.filter(
    F.col("petal_ratio").isNull()
).limit(1).count():
    raise RuntimeError("Razao invalida ou divisao por zero")

print("NOVA FEATURE CALCULADA: petal_ratio")
print("TABELA ORIGINAL PRESERVADA")
display(df_ratio.limit(10))
"""),

    md("""
## Próxima atividade

Estudar a atualização da Feature Table com `write_table`.

Antes dessa operação:
- Conferir se `petal_ratio` já existe.
- Validar a compatibilidade do esquema.
- Conferir as permissões de escrita.
- Evitar o `DROP COLUMNS` do notebook do professor.

Nenhuma alteração destrutiva foi incluída.
""")
]

novo = {
    "cells": celulas,
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        },
        "language_info": {"name": "python"}
    },
    "nbformat": 4,
    "nbformat_minor": 5
}

arquivo = DEST / "02_feature_store_iris_seguro.ipynb"

if not arquivo.exists():
    arquivo.write_text(
        json.dumps(novo, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    print("NOTEBOOK CRIADO:", arquivo)
else:
    print("NOTEBOOK EXISTENTE PRESERVADO")

json.loads(arquivo.read_text(encoding="utf-8"))

conteudo = """# Aula — Databricks Feature Store

## Validação local
- Dataset Iris: 150 registros.
- Cinco colunas originais.
- Três espécies.
- Notebook da Alura analisado.
- Notebook seguro preparado.

## Conceitos
- Feature Engineering Client.
- Unity Catalog.
- Chave primária.
- Consistência treino/inferência.
- Data leakage.
- Feature Store.
- petal_ratio.

## Pendências no Databricks
- Confirmar a tabela Iris no Unity Catalog.
- Executar o notebook preparado.
- Validar permissões da Feature Store.
- Confirmar a criação da tabela.

Nenhuma operação remota foi executada.
"""

if not NOTAS.exists():
    NOTAS.write_text(conteudo, encoding="utf-8")

print("\n===== RESULTADO FINAL =====")
print("IRIS:", len(linhas))
print("NOTEBOOK:", arquivo)
print("NOTAS:", NOTAS)
print("ORIGINAIS ALURA: PRESERVADOS")
print("EXECUCAO DATABRICKS: PENDENTE")