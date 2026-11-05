from pathlib import Path
import csv
import hashlib
import json
import re

BASE = Path(r"F:\AWS-CIENCIA-DE-DADOS-SEGURANCA-CUSTOS")
RAW = BASE / "s3_local" / "hospital-dados" / "raw"
PROCESSED = BASE / "s3_local" / "hospital-dados" / "processed"
RESULTADOS = BASE / "resultados"

CATALOGO = RESULTADOS / "aula_15_glue_data_catalog.json"
RELATORIO = RESULTADOS / "aula_15_glue.json"

TIPOS = {
    "Age": "integer",
    "Sex": "string",
    "ChestPainType": "string",
    "RestingBP": "integer",
    "Cholesterol": "integer",
    "FastingBS": "integer",
    "RestingECG": "string",
    "MaxHR": "integer",
    "ExerciseAngina": "string",
    "Oldpeak": "double",
    "ST_Slope": "string",
    "HeartDisease": "integer",
}


def inferir_tipo(valores):
    valores = [v.strip() for v in valores if v.strip()]

    if not valores:
        return "string"

    if all(re.fullmatch(r"[+-]?\d+", v) for v in valores):
        return "integer"

    try:
        for valor in valores:
            float(valor)
        return "double"
    except ValueError:
        return "string"


def executar_crawler(arquivo):
    if not arquivo.is_file():
        raise FileNotFoundError(arquivo)

    with arquivo.open("r", encoding="utf-8-sig", newline="") as f:
        leitor = csv.DictReader(f)
        colunas = leitor.fieldnames or []
        registros = list(leitor)

    esquema = [
        {
            "nome": coluna,
            "tipo": inferir_tipo(
                [linha[coluna] for linha in registros]
            )
        }
        for coluna in colunas
    ]

    return {
        "database": "hospital_db",
        "table": "heart_raw",
        "formato": "csv",
        "localizacao": str(arquivo),
        "s3_uri_ilustrativa": (
            "s3://aws-alura-ds22-local/raw/heart.csv"
        ),
        "registros": len(registros),
        "colunas": esquema,
        "sha256": hashlib.sha256(
            arquivo.read_bytes()
        ).hexdigest(),
    }


def main():
    print("===== AULA 15 - AWS GLUE =====")
    print("Modo: 100% LOCAL")
    print("Nenhum servico AWS sera executado.")

    arquivo = RAW / "heart.csv"
    tabela = executar_crawler(arquivo)

    print("\n===== CRAWLER LOCAL =====")
    print("Fonte:", arquivo)
    print("Registros encontrados:", tabela["registros"])
    print("Colunas encontradas:", len(tabela["colunas"]))

    assert tabela["registros"] == 918
    assert len(tabela["colunas"]) == 12

    for coluna in tabela["colunas"]:
        print(
            f"{coluna['nome']}: {coluna['tipo']}"
        )

    print("\n===== VALIDANDO ESQUEMA =====")

    encontrados = {
        item["nome"]: item["tipo"]
        for item in tabela["colunas"]
    }

    assert encontrados == TIPOS

    catalogo = {
        "modo": "simulacao_local",
        "database": "hospital_db",
        "tables": {
            "heart_raw": tabela
        },
        "aws_catalog_real": False
    }

    RESULTADOS.mkdir(parents=True, exist_ok=True)

    CATALOGO.write_text(
        json.dumps(catalogo, indent=4, ensure_ascii=False),
        encoding="utf-8"
    )

    print("Database: hospital_db")
    print("Tabela: heart_raw")
    print("Esquema registrado: OK")

    print("\n===== PLANO DE ETL =====")

    etapas = [
        {
            "etapa": "Extract",
            "origem": "raw/heart.csv",
            "situacao": "fonte identificada"
        },
        {
            "etapa": "Transform",
            "descricao": "limpeza e padronizacao",
            "situacao": "planejada"
        },
        {
            "etapa": "Load",
            "destino": "processed/",
            "situacao": "planejada"
        }
    ]

    for etapa in etapas:
        print(
            etapa["etapa"],
            "-",
            etapa["situacao"]
        )

    relatorio = {
        "aula": 15,
        "database": "hospital_db",
        "table": "heart_raw",
        "total_registros": tabela["registros"],
        "total_colunas": len(tabela["colunas"]),
        "crawler_local_executado": True,
        "etl_executado_nesta_aula": False,
        "etapas_etl": etapas,
        "recursos_aws_criados": 0
    }

    RELATORIO.write_text(
        json.dumps(relatorio, indent=4, ensure_ascii=False),
        encoding="utf-8"
    )

    assert CATALOGO.is_file()
    assert RELATORIO.is_file()
    assert PROCESSED.is_dir()

    print("\n===== VALIDACAO FINAL =====")
    print("TESTES: 5/5 APROVADOS")
    print("CATALOGO:", CATALOGO)
    print("RELATORIO:", RELATORIO)
    print("CUSTO AWS: ZERO")
    print("AULA 15 - GLUE INTRODUCAO CONCLUIDA")


if __name__ == "__main__":
    main()
