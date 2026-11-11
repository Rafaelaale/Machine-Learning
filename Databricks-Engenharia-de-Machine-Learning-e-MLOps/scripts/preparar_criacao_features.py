from pathlib import Path
from collections import Counter
import ast
import csv
import json

ROOT = Path(__file__).resolve().parents[1]
ORIGEM = ROOT / "notebooks/aula_02_feature_store/02_feature_store_iris_seguro.ipynb"
DESTINO = ROOT / "notebooks/aula_02_feature_store/03_criando_features_databricks.ipynb"
ALURA = ROOT / "material-alura/6123-alura-ml-databricks"
RELATORIO = ROOT / "relatorios/aula_criando_features.txt"

print("\n===== 1. CONFERINDO MATERIAL ORIGINAL =====")

referencia = ALURA / "aula_2/aula_2_2_features_databricks.ipynb"
original = json.loads(referencia.read_text(encoding="utf-8-sig"))

print("CELULAS DA ALURA:", len(original["cells"]))

iris = ALURA / "aula_1/iris_dataset.csv"

with iris.open(encoding="utf-8-sig", newline="") as arquivo:
    registros = list(csv.DictReader(arquivo))

if len(registros) != 150:
    raise ValueError("Dataset Iris diferente do esperado")

especies = Counter(x["species"] for x in registros)
if sorted(especies.values()) != [50, 50, 50]:
    raise ValueError("Distribuicao das especies inesperada")

distintos = len({
    tuple(sorted(linha.items()))
    for linha in registros
})

print("IRIS:", len(registros))
print("ESPECIES:", len(especies))
print("LINHAS DISTINTAS:", distintos)
print("LINHAS REPETIDAS:", len(registros) - distintos)

print("\n===== 2. APROVEITANDO NOTEBOOK ANTERIOR =====")

notebook = json.loads(ORIGEM.read_text(encoding="utf-8-sig"))

codigo_anterior = "\n".join(
    "".join(c["source"])
    for c in notebook["cells"]
    if c["cell_type"] == "code"
)

for variavel in ("tabela_features", "df_ratio", "fe"):
    if variavel not in codigo_anterior:
        raise RuntimeError(
            f"Notebook anterior nao possui: {variavel}"
        )

def markdown(texto):
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": (texto.strip() + "\n").splitlines(True)
    }

def code(texto):
    texto = texto.strip() + "\n"
    ast.parse(texto)

    return {
        "cell_type": "code",
        "metadata": {},
        "execution_count": None,
        "outputs": [],
        "source": texto.splitlines(True)
    }

notebook["cells"].append(markdown("""
# Continuação — Criando e atualizando Features

Nesta etapa utilizaremos o FeatureEngineeringClient
criado nas células anteriores.

A nova feature `petal_ratio` será gravada por MERGE.

O notebook preserva a tabela existente e impede a
exclusão acidental da feature oficial.
"""))

notebook["cells"].append(code("""
print("===== CONFERINDO FEATURE TABLE =====")

if "fe" not in globals() or "df_ratio" not in globals():
    raise RuntimeError(
        "Execute as celulas anteriores deste notebook primeiro."
    )

if not spark.catalog.tableExists(tabela_features):
    raise RuntimeError(
        "Feature Table ainda nao criada."
    )

tabela_atual = spark.table(tabela_features)

if tabela_atual.count() != 150:
    raise RuntimeError("Feature Table com contagem incorreta")

if "species" in tabela_atual.columns:
    raise RuntimeError("Target species presente nas features")

if tabela_atual.select("id_flor").distinct().count() != 150:
    raise RuntimeError("Chaves duplicadas")

fe.get_table(name=tabela_features)

print("FEATURE TABLE VALIDADA:", tabela_features)
"""))

notebook["cells"].append(markdown("""
## Adicionando `petal_ratio` com MERGE

O método `write_table` atualiza a Feature Table
utilizando `id_flor` como chave primária.

Se a coluna já estiver preenchida, não repetiremos
a gravação.
"""))

notebook["cells"].append(code("""
print("===== ADICIONANDO PETAL_RATIO =====")

tabela_atual = spark.table(tabela_features)

if "petal_ratio" in tabela_atual.columns:
    nulos = tabela_atual.filter(
        tabela_atual["petal_ratio"].isNull()
    ).limit(1).count()
else:
    nulos = 1

if nulos == 0:
    print("PETAL_RATIO JA EXISTE: GRAVACAO DISPENSADA")
else:
    fe.write_table(
        name=tabela_features,
        df=df_ratio,
        mode="merge"
    )
    print("FEATURE ADICIONADA COM MERGE")

resultado = spark.table(tabela_features)

if "petal_ratio" not in resultado.columns:
    raise RuntimeError("Feature nao encontrada apos MERGE")

display(
    resultado.select(
        "id_flor", "petal_length",
        "petal_width", "petal_ratio"
    ).limit(10)
)
"""))

notebook["cells"].append(markdown("""
## Histórico Delta Lake

Consultar as alterações realizadas na Feature Table.

O Time Travel permite consultar versões preservadas,
mas o controle de vazamento temporal também exige
considerar a data de disponibilidade das features.
"""))

notebook["cells"].append(code("""
print("===== HISTORICO DELTA =====")

display(
    spark.sql(
        f"DESCRIBE HISTORY {tabela_features}"
    )
)

print("HISTORICO CONSULTADO")
"""))

notebook["cells"].append(markdown("""
## Demonstração de DROP COLUMN

Esta demonstração é opcional.

Por segurança, a remoção ocorrerá somente em uma
tabela de laboratório, não na Feature Store principal.

Para executar, altere o widget `demonstrar_drop`
para `sim`.
"""))

notebook["cells"].append(code("""
dbutils.widgets.dropdown(
    "demonstrar_drop",
    "nao",
    ["nao", "sim"]
)

if dbutils.widgets.get("demonstrar_drop") == "nao":
    print("DROP NAO EXECUTADO")

else:
    partes = tabela_features.rsplit(".", 1)
    tabela_lab = partes[0] + ".iris_features_drop_lab"

    if not spark.catalog.tableExists(tabela_lab):
        spark.sql(
            f"CREATE TABLE {tabela_lab} USING DELTA AS "
            f"SELECT id_flor, petal_ratio FROM {tabela_features}"
        )

    if "petal_ratio" in spark.table(tabela_lab).columns:
        spark.sql(
            f"ALTER TABLE {tabela_lab} "
            "SET TBLPROPERTIES "
            "('delta.columnMapping.mode' = 'name')"
        )

        spark.sql(
            f"ALTER TABLE {tabela_lab} "
            "DROP COLUMN petal_ratio"
        )

        print("COLUNA REMOVIDA SOMENTE DO LABORATORIO")
    else:
        print("COLUNA JA AUSENTE NO LABORATORIO")

    display(spark.table(tabela_lab).limit(5))
    print("FEATURE STORE PRINCIPAL PRESERVADA")
"""))

notebook["cells"].append(markdown("""
## Validação final

A tabela oficial deve continuar com 150 registros,
chaves únicas, sem o target e com `petal_ratio`.
"""))

notebook["cells"].append(code("""
final = spark.table(tabela_features)

if final.count() != 150:
    raise RuntimeError("Contagem final invalida")

if "species" in final.columns:
    raise RuntimeError("Target presente indevidamente")

if "petal_ratio" not in final.columns:
    raise RuntimeError("Feature petal_ratio ausente")

if final.select("id_flor").distinct().count() != 150:
    raise RuntimeError("Chaves duplicadas")

print("===== FEATURE STORE VALIDADA =====")
print("TABELA:", tabela_features)
print("REGISTROS: 150")
print("COLUNAS:", final.columns)
print("TARGET EXCLUIDO")
print("PETAL_RATIO PRESENTE")
"""))

print("\n===== 3. VALIDANDO NOTEBOOK COMPLETO =====")

# Compatibilidade com arquivos de notebook sem cell IDs.
notebook["nbformat_minor"] = 4

for celula in notebook["cells"]:
    if celula["cell_type"] == "code":
        ast.parse("".join(celula["source"]))

if not DESTINO.exists():
    DESTINO.write_text(
        json.dumps(
            notebook,
            ensure_ascii=False,
            indent=2
        ) + "\n",
        encoding="utf-8"
    )
    print("NOVO NOTEBOOK CRIADO")
else:
    print("NOTEBOOK EXISTENTE PRESERVADO")

verificacao = json.loads(
    DESTINO.read_text(encoding="utf-8-sig")
)

for celula in verificacao["cells"]:
    if celula["cell_type"] == "code":
        ast.parse("".join(celula["source"]))

print("CELULAS:", len(verificacao["cells"]))
print("SINTAXE DAS CELULAS: APROVADA")

print("\n===== 4. SALVANDO RELATORIO =====")

RELATORIO.parent.mkdir(parents=True, exist_ok=True)

conteudo = f"""AULA - CRIANDO FEATURES NO DATABRICKS

Dataset Iris: {len(registros)} registros
Especies: {len(especies)}
Linhas distintas: {distintos}
Linhas repetidas: {len(registros) - distintos}

Notebook anterior: preservado
Novo notebook: {DESTINO}

Conteudos:
- Chave primaria
- FeatureEngineeringClient
- Feature Table
- petal_ratio
- write_table(mode=merge)
- Delta History
- DROP COLUMN isolado
- Validacao final

Auditoria local: concluida
Execucao no Databricks: pendente
Publicacao: nenhuma
"""

RELATORIO.write_text(conteudo, encoding="utf-8")

print("\n===== RESULTADO FINAL =====")
print("IRIS: 150 REGISTROS")
print("NOTEBOOK:", DESTINO)
print("RELATORIO:", RELATORIO)
print("EXECUCAO REMOTA: PENDENTE")