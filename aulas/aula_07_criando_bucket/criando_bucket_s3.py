from pathlib import Path
import hashlib
import json
import re

BASE = Path(__file__).resolve().parents[2]

BUCKET_NOME = "aws-alura-ds22-local"
REGIAO = "eu-north-1"

BUCKET = BASE / "s3_local" / "hospital-dados"
RAW = BUCKET / "raw"
PROCESS = BUCKET / "process"
PROCESSED = BUCKET / "processed"
PREDICTIONS = BUCKET / "predictions"
RESULTADOS = BASE / "resultados"


def sha256(arquivo):
    h = hashlib.sha256()
    with arquivo.open("rb") as f:
        for bloco in iter(lambda: f.read(1024 * 1024), b""):
            h.update(bloco)
    return h.hexdigest()


def main():
    print("===== AULA 07 - BUCKET S3 LOCAL =====")
    print("Ambiente: simulacao local")
    print("Nenhuma conexao com AWS")

    assert 3 <= len(BUCKET_NOME) <= 63
    assert re.fullmatch(
        r"[a-z0-9][a-z0-9.-]*[a-z0-9]",
        BUCKET_NOME
    )

    for pasta in (RAW, PROCESS, PROCESSED, PREDICTIONS, RESULTADOS):
        pasta.mkdir(parents=True, exist_ok=True)

    arquivo = RAW / "heart.csv"
    if not arquivo.exists():
        raise FileNotFoundError(
            "heart.csv nao encontrado. Execute a Aula 06."
        )

    import csv

    with arquivo.open("r", encoding="utf-8-sig", newline="") as f:
        leitor = csv.DictReader(f)
        total = sum(1 for _ in leitor)

    assert total == 918

    configuracao = {
        "nome_logico": BUCKET_NOME,
        "diretorio_local": str(BUCKET),
        "tipo": "general-purpose",
        "regiao_referencia": REGIAO,
        "acls_desabilitadas": True,
        "block_public_access": {
            "BlockPublicAcls": True,
            "IgnorePublicAcls": True,
            "BlockPublicPolicy": True,
            "RestrictPublicBuckets": True
        },
        "versionamento": "Disabled",
        "criptografia_referencia": "SSE-S3",
        "pastas": ["raw", "processed", "predictions"],
        "modo": "simulacao_local",
        "configuracoes_aws_aplicadas": False
    }

    config_path = RESULTADOS / "aula_07_bucket_config.json"
    config_path.write_text(
        json.dumps(configuracao, indent=4, ensure_ascii=False),
        encoding="utf-8"
    )

    relatorio = {
        "aula": 7,
        "bucket_simulado": BUCKET_NOME,
        "regiao": REGIAO,
        "objeto": "raw/heart.csv",
        "uri_s3_ilustrativa": f"s3://{BUCKET_NOME}/raw/heart.csv",
        "registros": total,
        "sha256": sha256(arquivo),
        "raw_existe": RAW.is_dir(),
        "processed_existe": PROCESSED.is_dir(),
        "predictions_existe": PREDICTIONS.is_dir(),
        "configuracao_aws_real": False,
        "recursos_aws_criados": 0
    }

    relatorio_path = RESULTADOS / "aula_07_bucket.json"
    relatorio_path.write_text(
        json.dumps(relatorio, indent=4, ensure_ascii=False),
        encoding="utf-8"
    )

    assert all((
        RAW.is_dir(),
        PROCESSED.is_dir(),
        PREDICTIONS.is_dir()
    ))

    assert arquivo.stat().st_size > 0

    print("\n===== CONFIGURACAO =====")
    print("Bucket simulado:", BUCKET_NOME)
    print("Regiao de referencia:", REGIAO)
    print("ACLs: desabilitadas (simulado)")
    print("Acesso publico: bloqueado (simulado)")
    print("Criptografia: SSE-S3 (referencia)")

    print("\n===== ESTRUTURA =====")
    print("raw/heart.csv:", total, "registros")
    print("processed/: OK")
    print("predictions/: OK")
    print("process/ antigo: preservado")

    print("\n===== VALIDACAO =====")
    print("TESTES: 3/3 APROVADOS")
    print("CONFIGURACAO:", config_path)
    print("RELATORIO:", relatorio_path)
    print("CUSTO AWS: ZERO")
    print("AULA 07 - CONCLUIDA")


if __name__ == "__main__":
    main()
