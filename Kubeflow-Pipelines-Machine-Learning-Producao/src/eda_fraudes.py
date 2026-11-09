import sys
import subprocess
import importlib.util

pacotes = {
    "pandas": "pandas",
    "numpy": "numpy",
    "sklearn": "scikit-learn",
    "matplotlib": "matplotlib"
}

for modulo, pacote in pacotes.items():
    if importlib.util.find_spec(modulo) is None:
        print(f"Instalando dependencia: {pacote}", flush=True)
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", pacote
        ])

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

print("\n===== CARREGANDO DATASET =====", flush=True)

df = pd.read_csv("/home/jovyan/dados/creditcard.csv")

print("Dimensoes:", df.shape)
print("Valores ausentes:", df.isnull().sum().sum())
print("Duplicados:", df.duplicated().sum())

print("\n===== DISTRIBUICAO DAS CLASSES =====")
print(df["Class"].value_counts())

print("\n===== PERCENTUAIS =====")
print(df["Class"].value_counts(normalize=True) * 100)

print("\n===== ESTATISTICAS =====")
print(df[["Time", "Amount", "Class"]].describe())

print("\n===== GRAFICO =====")

df["Class"].value_counts().sort_index().plot(
    kind="bar",
    title="Transacoes legitimas x fraudulentas"
)

plt.xlabel("Classe")
plt.ylabel("Quantidade")
plt.tight_layout()
plt.savefig("/tmp/grafico_fraudes.png")
plt.close()

print("Grafico gerado.")

print("\n===== ENGENHARIA DE ATRIBUTOS =====")

df["Hour"] = (df["Time"] // 3600) % 24
df["LogAmount"] = np.log1p(df["Amount"])

X = df.drop(columns=["Class"])
y = df["Class"]

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

scaler = StandardScaler()
colunas = ["Time", "Amount", "Hour", "LogAmount"]

X_train = X_train.copy()
X_test = X_test.copy()

X_train[colunas] = scaler.fit_transform(X_train[colunas])
X_test[colunas] = scaler.transform(X_test[colunas])

print("\n===== RESULTADOS =====")
print("Treino:", X_train.shape)
print("Teste:", X_test.shape)

print("\n===== AULA EXECUTADA COM SUCESSO =====")
