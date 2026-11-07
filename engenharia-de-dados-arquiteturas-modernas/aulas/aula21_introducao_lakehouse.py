"""Executa a Aula 21 - Introducao ao Lakehouse."""

import json
import sys
from pathlib import Path


BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from src.aula21_introducao_lakehouse import (
    executar_laboratorio,
)


def main():
    origem = (
        BASE / "dados" / "processed"
        / "minishop_modelo_logico_aula05.db"
    )

    lake = BASE / "dados" / "lake"

    print("===== AULA 21 - INTRODUCAO AO LAKEHOUSE =====")

    print("\n1. PREPARANDO CAMADAS EXISTENTES")

    resultado = executar_laboratorio(
        origem, lake
    )

    print(
        "Snapshot:",
        resultado["snapshot_id"],
    )

    print("\n2. CONSULTA SQL SOBRE A SILVER")

    print(json.dumps(
        resultado["consultas"]["indicadores"],
        indent=2,
        ensure_ascii=False,
    ))

    print("\n3. CONSULTA POR MES")

    print(json.dumps(
        resultado["consultas"]["mensal"],
        indent=2,
        ensure_ascii=False,
    ))

    print("\n4. CONSULTA POR PRODUTO")

    print(json.dumps(
        resultado["consultas"]["produtos"],
        indent=2,
        ensure_ascii=False,
    ))

    print("\n5. CONSULTA POR CLIENTE")

    print(json.dumps(
        resultado["consultas"]["clientes"],
        indent=2,
        ensure_ascii=False,
    ))

    print("\n6. RECONCILIACAO SQL X GOLD")

    print(json.dumps(
        resultado["reconciliacao"],
        indent=2,
        ensure_ascii=False,
    ))

    print("\n7. SALVANDO RELATORIO")

    relatorio = {
        "aula": 21,
        "tema": "Introducao ao Lakehouse",
        "snapshot_id": resultado["snapshot_id"],
        "indicadores": resultado["consultas"]["indicadores"],
        "mensal": resultado["consultas"]["mensal"],
        "produtos": resultado["consultas"]["produtos"],
        "clientes": resultado["consultas"]["clientes"],
        "reconciliacao": resultado["reconciliacao"],
        "dw_persistente_criado": False,
        "observacoes": [
            "Consultas SQL sobre dados da Silver",
            "SQLite utilizado somente em memoria",
            "Nenhum novo Data Warehouse persistente",
            "Reutilizacao de snapshots historicos",
            "Gold e SQL reconciliados",
            "Nao implementa tabela Delta ou Iceberg",
            "Nao oferece ACID e time travel de tabelas",
        ],
    }

    arquivo = (
        BASE / "resultados"
        / "aula21_introducao_lakehouse.json"
    )

    arquivo.write_text(
        json.dumps(
            relatorio,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print("Relatorio:", arquivo)
    print("AULA 21 EXECUTADA COM SUCESSO!")


if __name__ == "__main__":
    main()
