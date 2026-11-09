from pathlib import Path
import os
import shutil

import kagglehub
import pandas as pd


DATA_DIR = Path(
    os.environ.get(
        "CREDITCARD_DATA_DIR",
        r"F:\Kubeflow\Datasets\CreditCardFraud"
    )
)

DATA_DIR.mkdir(parents=True, exist_ok=True)

csv_destino = DATA_DIR / "creditcard.csv"

if not csv_destino.exists():
    print("Baixando dataset do Kaggle...")

    caminho = Path(
        kagglehub.dataset_download("mlg-ulb/creditcardfraud")
    )

    arquivos = list(caminho.rglob("creditcard.csv"))

    if not arquivos:
        raise FileNotFoundError("creditcard.csv nao encontrado")

    shutil.copy2(arquivos[0], csv_destino)

print("Dataset:", csv_destino)

df = pd.read_csv(csv_destino)

colunas_esperadas = (
    ["Time"]
    + [f"V{i}" for i in range(1, 29)]
    + ["Amount", "Class"]
)

assert df.columns.tolist() == colunas_esperadas, (
    "Colunas diferentes das esperadas"
)

assert set(df["Class"].unique()).issubset({0, 1})

total = len(df)
fraudes = int((df["Class"] == 1).sum())
normais = int((df["Class"] == 0).sum())
percentual = 100 * fraudes / total

resumo = f"""
AULA 05 - CREDIT CARD FRAUD DETECTION

Arquivo: {csv_destino}

REGISTROS: {total}
COLUNAS: {len(df.columns)}
VARIAVEIS DE ENTRADA: {len(df.columns) - 1}

TRANSACOES NORMAIS: {normais}
FRAUDES: {fraudes}
PERCENTUAL DE FRAUDE: {percentual:.4f}%

VALORES AUSENTES: {int(df.isna().sum().sum())}

COLUNAS:
{', '.join(df.columns)}

ESTATISTICAS:
{df[['Time', 'Amount', 'Class']].describe().to_string()}
"""

print(resumo)

saida = Path("anotacoes/aula05_analise_dataset.txt")
saida.write_text(resumo, encoding="utf-8")

print("ANALISE SALVA:", saida)
print("AULA 05 - DATASET VALIDADO")
