import json
import sqlite3
from pathlib import Path

base = Path(__file__).resolve().parent
pasta = base / "resultados"

arquivo = pasta / "RELATORIO_EXECUCAO.json"
banco = pasta / "catalogos_simulados.sqlite"

dados = json.loads(arquivo.read_text(encoding="utf-8-sig"))

if not isinstance(dados, list):
    raise AssertionError("Relatorio JSON nao contem uma lista")

esperados = {"dev", "stage", "prod"}

if len(dados) != 3:
    raise AssertionError(
        f"Esperados 3 ambientes, encontrados {len(dados)}"
    )

por_ambiente = {item["ambiente"]: item for item in dados}

if len(por_ambiente) != 3 or set(por_ambiente) != esperados:
    raise AssertionError("Ambientes ausentes ou duplicados no JSON")

print("JSON: 3 AMBIENTES CONFIRMADOS")

with sqlite3.connect(str(banco)) as conexao:
    for ambiente in ("dev", "stage", "prod"):
        tabela = f"{ambiente}_default_usuarios_bronze"

        existe = conexao.execute(
            "SELECT COUNT(*) FROM sqlite_master "
            "WHERE type = 'table' AND name = ?",
            (tabela,)
        ).fetchone()[0]

        if existe != 1:
            raise AssertionError(f"Tabela ausente: {tabela}")

        quantidade = conexao.execute(
            f"SELECT COUNT(*) FROM {tabela}"
        ).fetchone()[0]

        if quantidade != 2:
            raise AssertionError(
                f"{tabela}: esperado 2, encontrado {quantidade}"
            )

        registro = por_ambiente[ambiente]

        if registro["tabela"] != tabela:
            raise AssertionError(f"Nome incorreto: {ambiente}")

        if registro["registros"] != quantidade:
            raise AssertionError(f"JSON divergente: {ambiente}")

        print(f"OK: {ambiente.upper()} - {quantidade} registros")

print("SQLITE: 3 TABELAS CONFIRMADAS")
print("JSON E BANCO: CONSISTENTES")
print("AUDITORIA LOCAL: APROVADA")