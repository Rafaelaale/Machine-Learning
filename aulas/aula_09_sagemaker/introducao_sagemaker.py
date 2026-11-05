from pathlib import Path
from collections import Counter
import csv
import hashlib
import importlib.util
import json
import platform
import sys

BASE = Path(__file__).resolve().parents[2]

DADOS = BASE / "s3_local" / "hospital-dados" / "raw" / "heart.csv"
RESULTADOS = BASE / "resultados"

ETAPAS = [
    "Preparacao dos dados",
    "Analise exploratoria",
    "Treinamento",
    "Avaliacao",
    "Inferencia",
    "Monitoramento"
]


def verificar_bibliotecas():
    bibliotecas = [
        "pandas",
        "numpy",
        "sklearn",
        "matplotlib",
        "joblib",
        "jupyter"
    ]
    return {
        nome: importlib.util.find_spec(nome) is not None
        for nome in bibliotecas
    }


def verificar_dados():
    if not DADOS.is_file():
        raise FileNotFoundError(
            f"Arquivo nao encontrado: {DADOS}"
        )

    with DADOS.open("r", encoding="utf-8-sig", newline="") as f:
        leitor = csv.DictReader(f)
        colunas = leitor.fieldnames or []
        registros = list(leitor)

    if "HeartDisease" not in colunas:
        raise ValueError("Coluna HeartDisease ausente.")

    if len(registros) != 918:
        raise ValueError(
            f"Esperados 918 registros, encontrados {len(registros)}."
        )

    classes = Counter(
        linha["HeartDisease"] for linha in registros
    )

    if set(classes) != {"0", "1"}:
        raise ValueError("Classes inesperadas no dataset.")

    sha256 = hashlib.sha256(DADOS.read_bytes()).hexdigest()

    return {
        "registros": len(registros),
        "colunas": colunas,
        "classes": dict(classes),
        "sha256": sha256
    }


def main():
    print("===== SAGEMAKER - LABORATORIO LOCAL =====")
    print("AWS real: desativada")
    print("Treinamento nesta aula: nao")

    print("\n===== AMBIENTE PYTHON =====")
    print("Python:", sys.version.split()[0])
    print("Executavel:", sys.executable)
    print("Sistema:", platform.system())

    print("\n===== BIBLIOTECAS =====")
    bibliotecas = verificar_bibliotecas()

    for nome, instalada in bibliotecas.items():
        print(f"{nome}: {'OK' if instalada else 'NAO INSTALADA'}")

    print("\n===== DATA LAKE =====")
    dados = verificar_dados()

    print("Arquivo:", DADOS)
    print("Registros:", dados["registros"])
    print("Colunas:", len(dados["colunas"]))
    print("Distribuicao:", dados["classes"])
    print("Integridade SHA-256:", dados["sha256"])

    print("\n===== CICLO DE MACHINE LEARNING =====")
    for indice, etapa in enumerate(ETAPAS, start=1):
        print(f"{indice}. {etapa}")

    relatorio = {
        "aula": 9,
        "servico_estudado": "Amazon SageMaker",
        "modo": "local",
        "python": sys.version.split()[0],
        "bibliotecas": bibliotecas,
        "dataset": dados,
        "etapas_ml": ETAPAS,
        "modelos_treinados_nesta_aula": 0,
        "recursos_aws_criados": 0
    }

    RESULTADOS.mkdir(parents=True, exist_ok=True)

    destino = RESULTADOS / "aula_09_sagemaker.json"

    destino.write_text(
        json.dumps(relatorio, indent=4, ensure_ascii=False),
        encoding="utf-8"
    )

    assert dados["registros"] == 918
    assert sum(dados["classes"].values()) == 918
    assert len(ETAPAS) == 6

    print("\nTESTES: 3/3 APROVADOS")
    print("RELATORIO:", destino)
    print("AULA 09 - CONCLUIDA")


if __name__ == "__main__":
    main()
