from pathlib import Path
import csv
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "material-alura" / "6123-alura-ml-databricks"
DEST = ROOT / "notebooks" / "aula_01_explorando"
REPORT = ROOT / "relatorios" / "aula_explorando_databricks.txt"

DEST.mkdir(parents=True, exist_ok=True)
REPORT.parent.mkdir(parents=True, exist_ok=True)

def markdown(source):
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": source.splitlines(keepends=True)
    }

def python(source):
    return {
        "cell_type": "code",
        "metadata": {},
        "execution_count": None,
        "outputs": [],
        "source": source.strip().splitlines(keepends=True)
    }

def notebook(name, cells):
    path = DEST / name

    doc = {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {"name": "python"}
        },
        "nbformat": 4,
        "nbformat_minor": 4
    }

    if not path.exists():
        path.write_text(
            json.dumps(doc, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        print("CRIADO:", path.name)
    else:
        print("PRESERVADO:", path.name)

    json.loads(path.read_text(encoding="utf-8"))
    print("JSON VALIDADO:", path.name)

print("\n===== 1. AUDITORIA DOS DATASETS =====")

datasets = {
    "iris_dataset.csv": (150, ",", 5),
    "Iris.csv": (150, ",", 6),
    "base_dim_produtos.csv": (15, ",", 4),
    "base_bronze_eventos.csv": (20000, ";", 5),
}

resultados = []

for nome, (esperado, separador, colunas) in datasets.items():
    path = REF / "aula_1" / nome

    if not path.is_file():
        raise RuntimeError(f"Arquivo ausente: {nome}")

    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f, delimiter=separador)
        cabecalho = next(reader)
        total = sum(1 for _ in reader)

    if total != esperado or len(cabecalho) != colunas:
        raise RuntimeError(
            f"Dataset inesperado: {nome}; "
            f"linhas={total}, colunas={len(cabecalho)}"
        )

    resultados.append(f"{nome}: {total} registros, {colunas} colunas")
    print("VALIDADO:", resultados[-1])

print("\n===== 2. CRIANDO NOTEBOOK DE EXPLORACAO =====")

notebook("01_ambiente_e_consultas.ipynb", [
    markdown("""
# Aula — Explorando Databricks

Notebook preparado com base no material original da Alura.

Execute as células no **Databricks Free Edition**.

Objetivos:
- Conhecer bibliotecas e recursos do ambiente.
- Consultar SQL e Spark.
- Explorar visualizações.
- Evitar instalações desnecessárias.
"""),

    python("""
import sys
import platform
import os
import shutil
from importlib import metadata

print("===== AMBIENTE DATABRICKS =====")
print("Python:", sys.version.split()[0])
print("Sistema:", platform.platform())
print("CPU disponivel:", os.cpu_count())

for pacote in [
    "scikit-learn",
    "mlflow",
    "pyspark",
    "torch",
    "xgboost",
    "psutil"
]:
    try:
        versao = metadata.version(pacote)
        print(f"{pacote}: {versao}")
    except metadata.PackageNotFoundError:
        print(f"{pacote}: NAO INSTALADO")

total, usado, livre = shutil.disk_usage("/")
print("Disco livre (GB):", round(livre / (1024 ** 3), 2))
"""),

    markdown("""
## Consultar uma tabela de demonstração

A tabela climática usada pelo instrutor pode ser acessada
se estiver disponível no catálogo `samples`.
"""),

    python("""
tabela_clima = "samples.accuweather.forecast_daily_calendar_imperial"

try:
    df_previsao = spark.read.table(tabela_clima).limit(100)
    print("TABELA CLIMATICA ENCONTRADA")
    display(df_previsao)
except Exception as erro:
    print("Tabela indisponivel ou sem permissao.")
    print(type(erro).__name__)
"""),

    markdown("""
## Estatísticas e visualização

O exemplo abaixo usa somente os dados limitados a 100 registros.
"""),

    python("""
if "df_previsao" in globals():
    df_previsao.show(5, truncate=False)
    display(df_previsao.summary())
else:
    print("Execute primeiro a leitura da tabela climatica.")
"""),

    markdown("""
## SQL no Databricks

Execute a consulta abaixo em uma célula SQL.
"""),

    python("""
%sql
SELECT *
FROM samples.accuweather.forecast_daily_calendar_imperial
LIMIT 100
""")
])

print("\n===== 3. CRIANDO NOTEBOOK DE INGESTAO SEGURA =====")

notebook("02_iris_produtos_e_time_travel.ipynb", [
    markdown("""
# Ingestão Iris, Produtos e Time Travel

Este notebook utiliza o Databricks Free Edition.

**Antes de executar:**
1. Carregue `iris_dataset.csv` como tabela `workspace.default.iris_dataset`.
2. Crie um Volume chamado `workspace` em `workspace.default`.
3. Envie `base_dim_produtos.csv` para esse Volume.

Nenhuma tabela existente será sobrescrita automaticamente.
A demonstração de Time Travel utiliza uma tabela separada.
"""),

    python("""
dbutils.widgets.text("catalogo", "workspace")
dbutils.widgets.text("esquema", "default")
dbutils.widgets.text("volume", "workspace")

catalogo = dbutils.widgets.get("catalogo").strip()
esquema = dbutils.widgets.get("esquema").strip()
volume = dbutils.widgets.get("volume").strip()

import re

for nome in [catalogo, esquema, volume]:
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", nome):
        raise ValueError("Identificador invalido: " + nome)

tabela_iris = f"{catalogo}.{esquema}.iris_dataset"
tabela_produtos = f"{catalogo}.{esquema}.dim_produtos"
tabela_lab = f"{catalogo}.{esquema}.dim_produtos_time_travel_lab"

caminho_produtos = (
    f"/Volumes/{catalogo}/{esquema}/{volume}/base_dim_produtos.csv"
)

print("Tabela Iris:", tabela_iris)
print("Tabela Produtos:", tabela_produtos)
print("CSV no Volume:", caminho_produtos)
"""),

    markdown("""
## 1. Consultar a tabela Iris

A tabela deve ter sido criada pela interface do Databricks.
"""),

    python("""
try:
    df_iris = spark.table(tabela_iris)
    print("Registros Iris:", df_iris.count())
    display(df_iris.limit(10))
except Exception as erro:
    print("Tabela Iris ainda nao encontrada.")
    print("Crie a tabela pela interface de ingestao.")
    print(type(erro).__name__)
"""),

    markdown("""
## 2. Ingestão de produtos com tipagem explícita

Não utilizamos a sintaxe incorreta `SELECT id_produto STRING`.

O esquema é definido com `StructType`, utilizando PySpark.
"""),

    python("""
from pyspark.sql.types import (
    StructType, StructField,
    StringType, DecimalType
)

esquema_produtos = StructType([
    StructField("id_produto", StringType(), False),
    StructField("nome_produto", StringType(), True),
    StructField("categoria", StringType(), True),
    StructField("preco_reais", DecimalType(10, 2), True)
])

try:
    df_produtos = (
        spark.read
        .option("header", "true")
        .option("sep", ",")
        .schema(esquema_produtos)
        .csv(caminho_produtos)
    )

    quantidade = df_produtos.count()

    print("Produtos encontrados:", quantidade)

    if quantidade != 15:
        raise ValueError(
            f"Esperados 15 produtos; encontrados {quantidade}"
        )

    display(df_produtos)

except Exception as erro:
    print("Leitura ainda nao concluida.")
    print("Confirme o upload do CSV para o Volume.")
    print(type(erro).__name__)
    df_produtos = None
"""),

    markdown("""
## 3. Gravar a dimensão de produtos

Cria a tabela somente se ela ainda não existir.
Preserva tabelas existentes.
"""),

    python("""
if df_produtos is None:
    print("Sem dados validos. Gravacao ignorada.")

elif spark.catalog.tableExists(tabela_produtos):
    print("Tabela existente preservada:", tabela_produtos)
    display(spark.table(tabela_produtos).limit(15))

else:
    (
        df_produtos.write
        .format("delta")
        .mode("errorifexists")
        .saveAsTable(tabela_produtos)
    )

    print("Tabela Delta criada:", tabela_produtos)
    display(spark.table(tabela_produtos))
"""),

    markdown("""
## 4. Laboratório isolado de Time Travel

A tabela original `dim_produtos` não será modificada.

O exemplo usa outra tabela, exclusiva do laboratório.
Execute as próximas células em ordem.
"""),

    python("""
if not spark.catalog.tableExists(tabela_produtos):
    print("Crie primeiro a tabela de produtos.")
else:
    spark.sql(f'''
        CREATE TABLE IF NOT EXISTS {tabela_lab}
        USING DELTA
        AS SELECT * FROM {tabela_produtos}
    ''')

    print("Laboratorio disponivel:", tabela_lab)

    display(spark.sql(f"DESCRIBE HISTORY {tabela_lab}"))

    versao_base = spark.sql(
        f"DESCRIBE HISTORY {tabela_lab}"
    ).selectExpr("max(version) AS versao").first()["versao"]

    print("Versao anterior ao teste:", versao_base)
"""),

    markdown("""
## 5. Simular erro somente no laboratório

O preço de um único produto será alterado para zero.
A tabela principal não será afetada.
"""),

    python("""
if "versao_base" not in globals():
    print("Execute a criacao da tabela de laboratorio primeiro.")
else:
    spark.sql(f'''
        UPDATE {tabela_lab}
        SET preco_reais = CAST(0 AS DECIMAL(10,2))
        WHERE id_produto = 'prod_101'
    ''')

    print("Alteracao de teste realizada no laboratorio.")
    display(spark.table(tabela_lab).limit(15))
"""),

    markdown("""
## 6. Consultar o histórico e restaurar

A versão anterior foi capturada antes da alteração.

A restauração afeta apenas a tabela de laboratório.
"""),

    python("""
if "versao_base" not in globals():
    print("Execute primeiro as etapas do laboratorio.")
else:
    print("Historico antes da restauracao:")
    display(spark.sql(f"DESCRIBE HISTORY {tabela_lab}"))

    try:
        spark.sql(
            f"RESTORE TABLE {tabela_lab} VERSION AS OF {versao_base}"
        )

        print("Laboratorio restaurado.")
        display(spark.table(tabela_lab).limit(15))

    except Exception as erro:
        print("Restauracao nao concluida.")
        print("Verifique permissoes e retencao Delta.")
        print(type(erro).__name__)
""")
])

print("\n===== 4. SALVANDO CHECKLIST DA AULA =====")

checklist = """# Aula — Explorando Databricks

## Arquivos locais

- [x] Referência original da Alura disponível
- [x] Iris Dataset validado
- [x] Dimensão de produtos validada
- [x] Base Bronze validada
- [x] Notebook de ambiente preparado
- [x] Notebook de ingestão preparado
- [x] Exemplo de Time Travel isolado

## Etapas no Databricks Free Edition

- [ ] Confirmar acesso ao workspace
- [ ] Explorar SQL, Compute e Unity Catalog
- [ ] Vincular GitHub, somente se desejar
- [ ] Importar notebooks preparados
- [ ] Criar tabela workspace.default.iris_dataset
- [ ] Criar Volume workspace.default.workspace
- [ ] Enviar base_dim_produtos.csv ao Volume
- [ ] Executar o notebook de ingestão
- [ ] Testar Time Travel na tabela de laboratório

## Segurança

Não utilizar o workspace do instrutor.
Não ativar os workflows de deploy do repositório original.
Não sobrescrever tabelas de produção.
Não salvar tokens em notebooks.
"""

path = ROOT / "aulas" / "aula_explorando_databricks.md"
path.parent.mkdir(parents=True, exist_ok=True)

if not path.exists():
    path.write_text(checklist, encoding="utf-8")
    print("CHECKLIST CRIADO")
else:
    print("CHECKLIST EXISTENTE PRESERVADO")

REPORT.write_text(
    "\n".join(resultados)
    + "\n\nNotebooks preparados: 2"
    + "\nNenhum notebook executado na nuvem."
    + "\nNenhum arquivo original alterado.\n",
    encoding="utf-8"
)

print("\n===== RESULTADO FINAL =====")
print("DATASETS VALIDADOS: 4/4")
print("NOTEBOOKS PREPARADOS: 2/2")
print("CHECKLIST:", path)
print("RELATORIO:", REPORT)
print("NENHUM DEPLOY OU PUBLICACAO.")