"""Executa Bronze, Silver e Gold da Minishop."""

import json
import sys
from pathlib import Path


BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from src.aula17_data_lake import validar_snapshot
from src.aula18_arquitetura_data_lake import (
    executar_arquitetura,
    validar_camada,
    ler_silver,
)


def main():
    origem = (
        BASE / "dados" / "processed"
        / "minishop_modelo_logico_aula05.db"
    )

    lake = BASE / "dados" / "lake"

    print("===== AULA 18 - ARQUITETURA DATA LAKE =====")

    print("\n1. BRONZE - RAW")
    resultado = executar_arquitetura(
        origem, lake
    )

    bronze = resultado["bronze"]
    silver = resultado["silver"]
    gold = resultado["gold"]

    print("Snapshot:", bronze["snapshot_id"])
    print("Novo:", bronze["novo"])
    print(
        "Integridade:",
        validar_snapshot(bronze["pasta"]),
    )

    print("\n2. SILVER - STAGED")
    print("Pasta:", silver["pasta"])
    print("Nova carga:", silver["novo"])

    manifesto_silver = validar_camada(
        silver["pasta"], "silver"
    )

    vendas = ler_silver(
        silver["pasta"]
    )

    print("Registros padronizados:", len(vendas))
    print(
        "Arquivos:",
        list(manifesto_silver["arquivos"]),
    )

    print("\n3. GOLD - CURATED")
    print("Pasta:", gold["pasta"])
    print("Nova carga:", gold["novo"])

    manifesto_gold = validar_camada(
        gold["pasta"], "gold"
    )

    print(json.dumps(
        gold["resumo"],
        indent=2,
        ensure_ascii=False,
    ))

    print("\n4. RECONCILIACAO")

    total_silver = sum(
        item["valor_centavos"]
        for item in vendas
    )

    total_gold = gold["resumo"][
        "faturamento_centavos"
    ]

    if total_silver != total_gold:
        raise RuntimeError(
            "Divergencia entre Silver e Gold"
        )

    print("Silver:", total_silver)
    print("Gold:", total_gold)
    print("Reconciliacao: OK")

    print("\n5. SALVANDO RELATORIO")

    relatorio = {
        "aula": 18,
        "tema": "Arquitetura do Data Lake",
        "snapshot_id": bronze["snapshot_id"],
        "bronze": bronze,
        "silver": silver,
        "gold": gold,
        "integridade_silver": bool(
            manifesto_silver
        ),
        "integridade_gold": bool(
            manifesto_gold
        ),
        "reconciliacao": {
            "silver_centavos": total_silver,
            "gold_centavos": total_gold,
            "igual": total_silver == total_gold,
        },
        "observacoes": [
            "Bronze preservada a partir da Aula 17",
            "Silver criada por Schema on Read",
            "Gold criada exclusivamente da Silver",
            "Nenhum banco anterior foi alterado",
            "Implementacao local sem servico de nuvem",
        ],
    }

    arquivo = (
        BASE / "resultados"
        / "aula18_arquitetura_data_lake.json"
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
    print("AULA 18 EXECUTADA COM SUCESSO!")


if __name__ == "__main__":
    main()
