from pathlib import Path
import csv
import hashlib
import json
import re
from datetime import datetime, timezone

BASE = Path(r"F:\AWS-CIENCIA-DE-DADOS-SEGURANCA-CUSTOS")
RAW = BASE / "s3_local" / "hospital-dados" / "raw"
RESULTADOS = BASE / "resultados"

CONFIG = RESULTADOS / "aula_16_crawler_config.json"
CATALOGO = RESULTADOS / "aula_16_raw_data_catalog.json"
RELATORIO = RESULTADOS / "aula_16_catalogacao.json"

CRAWLER = "crawler-alura"
DATABASE = "raw-data"


def inferir_tipo(valores):
    preenchidos = [
        str(valor).strip()
        for valor in valores
        if valor is not None and str(valor).strip()
    ]

    if not preenchidos:
        return "string"

    if all(re.fullmatch(r"[+-]?\d+", v) for v in preenchidos):
        return "integer"

    try:
        for valor in preenchidos:
            float(valor)
        return "double"
    except ValueError:
        return "string"


def catalogar_csv(caminho):
    with caminho.open("r", encoding="utf-8-sig", newline="") as arquivo:
        leitor = csv.DictReader(arquivo)
        colunas = leitor.fieldnames or []
        registros = list(leitor)

    if not colunas:
        raise ValueError(f"CSV sem cabecalho: {caminho}")

    if len(colunas) != len(set(colunas)):
        raise ValueError(f"Colunas duplicadas: {caminho}")

    esquema = [
        {
            "nome": coluna,
            "tipo": inferir_tipo(
                [registro.get(coluna) for registro in registros]
            ),
            "nulos_ou_vazios": sum(
                not (registro.get(coluna) or "").strip()
                for registro in registros
            )
        }
        for coluna in colunas
    ]

    return {
        "nome": caminho.stem.lower().replace("-", "_"),
        "formato": "csv",
        "localizacao_local": str(caminho),
        "uri_s3_ilustrativa": (
            f"s3://aws-alura-ds22-local/raw/{caminho.name}"
        ),
        "registros": len(registros),
        "colunas": esquema,
        "sha256": hashlib.sha256(
            caminho.read_bytes()
        ).hexdigest()
    }


def main():
    print("===== AULA 16 - AWS GLUE DATA CATALOG =====")
    print("Modo: CRAWLER LOCAL, SEM AWS")

    if not RAW.is_dir():
        raise FileNotFoundError(RAW)

    fontes = sorted(RAW.glob("*.csv"))

    if not fontes:
        raise FileNotFoundError(
            "Nenhum arquivo CSV encontrado em raw/"
        )

    RESULTADOS.mkdir(parents=True, exist_ok=True)

    print("\n===== CONFIGURANDO CRAWLER =====")

    config = {
        "crawler": CRAWLER,
        "database": DATABASE,
        "fonte_local": str(RAW),
        "s3_uri_ilustrativa": "s3://aws-alura-ds22-local/raw/",
        "agendamento": "ON_DEMAND",
        "role_referencia": "Glue",
        "modo": "simulacao_local",
        "aws_crawler_real": False
    }

    CONFIG.write_text(
        json.dumps(config, indent=4, ensure_ascii=False),
        encoding="utf-8"
    )

    print("Crawler:", CRAWLER)
    print("Database:", DATABASE)
    print("Fonte:", RAW)
    print("Agendamento: sob demanda")

    print("\n===== EXECUTANDO CRAWLER LOCAL =====")

    tabelas = {}

    for arquivo in fontes:
        tabela = catalogar_csv(arquivo)

        if tabela["nome"] in tabelas:
            raise ValueError("Nome de tabela duplicado.")

        tabelas[tabela["nome"]] = tabela

        print("Tabela:", tabela["nome"])
        print("Registros:", tabela["registros"])
        print("Colunas:", len(tabela["colunas"]))

        for coluna in tabela["colunas"]:
            print(
                f"  {coluna['nome']}: {coluna['tipo']}"
            )

    print("\n===== VALIDANDO HEART.CSV =====")

    if "heart" not in tabelas:
        raise ValueError("Tabela heart nao encontrada.")

    heart = tabelas["heart"]

    assert heart["registros"] == 918
    assert len(heart["colunas"]) == 12

    colunas = {
        item["nome"]: item["tipo"]
        for item in heart["colunas"]
    }

    assert colunas["Age"] == "integer"
    assert colunas["Cholesterol"] == "integer"
    assert colunas["Oldpeak"] == "double"
    assert colunas["HeartDisease"] == "integer"

    catalogo = {
        "database": DATABASE,
        "crawler": CRAWLER,
        "tabelas": tabelas,
        "modo": "local",
        "catalogo_aws_real": False
    }

    CATALOGO.write_text(
        json.dumps(catalogo, indent=4, ensure_ascii=False),
        encoding="utf-8"
    )

    print("\n===== EXECUCAO DO CRAWLER =====")
    print("Estado local: READY")
    print("Ultima execucao local: SUCESSO")
    print("Tabelas catalogadas:", len(tabelas))

    relatorio = {
        "aula": 16,
        "crawler": CRAWLER,
        "database": DATABASE,
        "agendamento": "ON_DEMAND",
        "estado_local": "READY",
        "ultima_execucao_local": "SUCESSO",
        "executado_em_utc": datetime.now(timezone.utc).isoformat(),
        "tabelas": list(tabelas.keys()),
        "total_tabelas": len(tabelas),
        "heart_registros": heart["registros"],
        "heart_colunas": len(heart["colunas"]),
        "recursos_aws_criados": 0
    }

    RELATORIO.write_text(
        json.dumps(relatorio, indent=4, ensure_ascii=False),
        encoding="utf-8"
    )

    assert CONFIG.is_file()
    assert CATALOGO.is_file()
    assert RELATORIO.is_file()

    print("\n===== VALIDACAO FINAL =====")
    print("TESTES: 7/7 APROVADOS")
    print("CONFIGURACAO:", CONFIG)
    print("CATALOGO:", CATALOGO)
    print("RELATORIO:", RELATORIO)
    print("CUSTO AWS: ZERO")
    print("AULA 16 - CATALOGACAO CONCLUIDA")


if __name__ == "__main__":
    main()
