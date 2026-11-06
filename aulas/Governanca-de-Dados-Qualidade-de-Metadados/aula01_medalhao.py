import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

BRONZE = BASE_DIR / "bronze"
SILVER = BASE_DIR / "silver"
GOLD = BASE_DIR / "gold"

# ==========================================
# CAMADA BRONZE - DADOS ORIGINAIS
# ==========================================

dados = {
    "id_venda": [1, 2, 3, 3, 4, 5, 6],
    "produto": [
        "Cereal Infantil",
        "Cereal Infantil",
        "Cereal Chocolate",
        "Cereal Chocolate",
        "Cereal Infantil",
        "Cereal Chocolate",
        "Cereal Infantil"
    ],
    "quantidade": [10, 15, 8, 8, -5, 20, 12],
    "preco_unitario": [12.5, 12.5, 15.0, 15.0, 12.5, 15.0, 12.5]
}

df_bronze = pd.DataFrame(dados)

df_bronze.to_csv(
    BRONZE / "vendas_originais.csv",
    index=False
)

print("\n===== CAMADA BRONZE =====")
print(df_bronze)

# ==========================================
# CAMADA SILVER - TRATAMENTO
# ==========================================

df_silver = pd.read_csv(
    BRONZE / "vendas_originais.csv"
)

# Remover duplicidades de venda
df_silver = df_silver.drop_duplicates(
    subset=["id_venda"]
)

# Remover quantidades invalidas
df_silver = df_silver[
    df_silver["quantidade"] > 0
].copy()

# Calcular receita
df_silver["receita"] = (
    df_silver["quantidade"] *
    df_silver["preco_unitario"]
)

df_silver.to_csv(
    SILVER / "vendas_tratadas.csv",
    index=False
)

print("\n===== CAMADA SILVER =====")
print(df_silver)

# ==========================================
# CAMADA GOLD - INDICADORES
# ==========================================

df_gold = (
    df_silver
    .groupby("produto", as_index=False)
    .agg(
        total_vendido=("quantidade", "sum"),
        receita_total=("receita", "sum"),
        numero_vendas=("id_venda", "count")
    )
)

df_gold.to_csv(
    GOLD / "indicadores_vendas.csv",
    index=False
)

print("\n===== CAMADA GOLD =====")
print(df_gold)

print("\nPipeline Bronze -> Silver -> Gold concluido.")