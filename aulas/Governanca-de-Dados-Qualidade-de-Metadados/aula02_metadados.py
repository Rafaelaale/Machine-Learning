import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

PASTA_METADADOS = BASE_DIR / "metadados"

arquivos = sorted(PASTA_METADADOS.glob("*.json"))

print("\n===== AULA 02 - METADADOS =====")

total_tabelas = 0
total_colunas = 0

campos_coluna = [
    "type",
    "name",
    "datatype",
    "descricao",
    "privacidade",
    "confidencialidade"
]

for arquivo in arquivos:

    with open(
        arquivo,
        "r",
        encoding="utf-8"
    ) as file:
        metadados = json.load(file)

    total_tabelas += 1

    nome = metadados.get("name")
    banco = metadados.get("database")
    descricao = metadados.get("descricao")

    colunas = metadados.get("schema", [])

    total_colunas += len(colunas)

    print("\n" + "=" * 55)
    print(f"ARQUIVO: {arquivo.name}")
    print(f"TABELA: {nome}")
    print(f"DATABASE: {banco}")
    print(f"DESCRICAO: {descricao}")
    print(f"TOTAL DE COLUNAS: {len(colunas)}")

    print("\nCOLUNAS E QUALIDADE DOS METADADOS:")

    for coluna in colunas:

        nome_coluna = coluna.get("name")

        ausentes = [
            campo
            for campo in campos_coluna
            if not coluna.get(campo)
        ]

        print(f"\nColuna: {nome_coluna}")
        print(f"Tipo: {coluna.get('datatype')}")

        if ausentes:
            print(
                "Metadados ausentes: "
                + ", ".join(ausentes)
            )
        else:
            print("Metadados completos.")

    print("\nLINHAGEM:")

    linhagem = metadados.get("linhagem", [])

    if linhagem:
        for origem in linhagem:
            print(
                "Origem:",
                origem.get("referencia")
            )
    else:
        print("Nenhuma origem declarada.")

print("\n" + "=" * 55)
print("RESUMO FINAL")
print(f"Tabelas analisadas: {total_tabelas}")
print(f"Colunas analisadas: {total_colunas}")

print("\nAnalise concluida.")