from pathlib import Path
import csv
import hashlib
import json
import shutil

BASE = Path(__file__).resolve().parents[2]

MATERIAL = BASE / "material_alura" / "AWSCienciaDeDados-main"
BUCKET = BASE / "s3_local" / "hospital-dados"
RAW = BUCKET / "raw"
PROCESS = BUCKET / "process"
PREDICTIONS = BUCKET / "predictions"
RESULTADOS = BASE / "resultados"


def sha256(arquivo):
    digest = hashlib.sha256()

    with arquivo.open("rb") as f:
        for bloco in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(bloco)

    return digest.hexdigest()


def main():
    print("===== AULA 06 - SIMULADOR AMAZON S3 =====")
    print("Modo: armazenamento local, sem AWS")

    for pasta in (RAW, PROCESS, PREDICTIONS, RESULTADOS):
        pasta.mkdir(parents=True, exist_ok=True)

    candidatos = list(MATERIAL.rglob("heart.csv"))

    if not candidatos:
        raise FileNotFoundError("heart.csv nao encontrado.")

    if len(candidatos) != 1:
        raise RuntimeError("Mais de um heart.csv encontrado.")

    origem = candidatos[0]
    destino = RAW / "heart.csv"

    hash_origem = sha256(origem)

    if destino.exists():
        if sha256(destino) != hash_origem:
            raise RuntimeError(
                "Ja existe um heart.csv diferente na pasta raw."
            )
        print("Objeto ja armazenado. Copia preservada.")
    else:
        shutil.copy2(origem, destino)
        print("Objeto enviado ao bucket local.")

    hash_destino = sha256(destino)

    assert hash_origem == hash_destino

    with destino.open("r", encoding="utf-8-sig", newline="") as f:
        leitor = csv.DictReader(f)
        registros = list(leitor)
        colunas = leitor.fieldnames or []

    assert len(registros) == 918
    assert "HeartDisease" in colunas

    print("\n===== OBJETO =====")
    print("Bucket: hospital-dados")
    print("Key: raw/heart.csv")
    print("Registros:", len(registros))
    print("SHA-256:", hash_destino)
    print("Integridade: OK")

    print("\n===== AREAS DO DATA LAKE =====")
    for nome, pasta in (
        ("raw", RAW),
        ("process", PROCESS),
        ("predictions", PREDICTIONS),
    ):
        arquivos = [p.name for p in pasta.iterdir() if p.is_file()]
        print(f"{nome}: {arquivos}")

    relatorio = {
        "aula": 6,
        "modo": "local",
        "bucket": "hospital-dados",
        "key": "raw/heart.csv",
        "registros": len(registros),
        "sha256": hash_destino,
        "integridade": True,
        "custo_aws": 0,
        "areas": ["raw", "process", "predictions"]
    }

    arquivo = RESULTADOS / "aula_06_s3.json"

    arquivo.write_text(
        json.dumps(relatorio, indent=4, ensure_ascii=False),
        encoding="utf-8"
    )

    print("\nTESTES: 3/3 APROVADOS")
    print("RELATORIO:", arquivo)
    print("AULA 06 - CONCLUIDA")


if __name__ == "__main__":
    main()
