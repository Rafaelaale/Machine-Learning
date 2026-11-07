"""Aula 19 - EL e ETL com a Bronze como fonte."""

import json
import sys
from pathlib import Path


BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from src.aula17_data_lake import (
    validar_snapshot,
    hash_arquivo,
)

from src.aula19_fluxos_data_lake import (
    fluxo_el,
    fluxo_etl,
    intervalo_snapshot,
    reconciliar_gold_dw,
)


def main():
    oltp = (
        BASE / "dados" / "processed"
        / "minishop_modelo_logico_aula05.db"
    )

    lake = BASE / "dados" / "lake"

    dw = (
        BASE / "dados" / "processed"
        / "minishop_dw_lake_aula19.db"
    )

    print("===== AULA 19 - FLUXOS COM DATA LAKE =====")

    print("\n1. FLUXO EL: OLTP -> DATA LAKE")

    ingestao = fluxo_el(
        oltp, lake
    )

    print(json.dumps(
        ingestao,
        indent=2,
        ensure_ascii=False,
    ))

    pasta_bronze = Path(
        ingestao["pasta_bronze"]
    )

    print("\n2. VERIFICANDO PRESERVACAO RAW")

    integridade = validar_snapshot(
        pasta_bronze
    )

    hash_antes = hash_arquivo(
        pasta_bronze / "oltp.sqlite"
    )

    print("Integridade Bronze:", integridade)

    print("\n3. LENDO PERIODO DO DATA LAKE")

    inicio, fim = intervalo_snapshot(
        pasta_bronze
    )

    print("Data_Inicial:", inicio)
    print("Data_Final:", fim)

    print("\n4. FLUXO ETL: DATA LAKE -> DW")

    processamento = fluxo_etl(
        pasta_bronze,
        dw,
        inicio,
        fim,
        lake,
    )

    print(json.dumps(
        processamento["dw"],
        indent=2,
        ensure_ascii=False,
    ))

    print("\n5. CONFERINDO SILVER E GOLD")

    print(json.dumps(
        processamento["gold"],
        indent=2,
        ensure_ascii=False,
    ))

    print("\n6. RECONCILIACAO GOLD E DW")

    reconciliacao = reconciliar_gold_dw(
        processamento
    )

    print(json.dumps(
        reconciliacao,
        indent=2,
        ensure_ascii=False,
    ))

    if not reconciliacao["reconciliado"]:
        raise RuntimeError(
            "Gold e DW apresentam valores divergentes"
        )

    print("\n7. CONFERINDO BRONZE NOVAMENTE")

    hash_depois = hash_arquivo(
        pasta_bronze / "oltp.sqlite"
    )

    if hash_antes != hash_depois:
        raise RuntimeError(
            "Snapshot Raw foi modificado"
        )

    if not validar_snapshot(pasta_bronze):
        raise RuntimeError(
            "Integridade Bronze comprometida"
        )

    print("Bronze preservada: True")

    print("\n8. SALVANDO RELATORIO")

    arquivo = (
        BASE / "resultados"
        / "aula19_fluxos_data_lake.json"
    )

    relatorio = {
        "aula": 19,
        "tema": "Fluxos de Dados com Data Lake",
        "ingestao": ingestao,
        "processamento": processamento,
        "reconciliacao": reconciliacao,
        "bronze_preservada": True,
        "observacoes": [
            "Fluxo EL separado do ETL",
            "Fonte do ETL: snapshot no Data Lake",
            "OLTP original acessado apenas na ingestao",
            "Bronze preservada durante o processamento",
            "Silver e Gold reutilizadas da Aula 18",
            "DW carregado pelo orquestrador da Aula 16",
            "Implementacao local sem armazenamento distribuido",
        ],
    }

    arquivo.write_text(
        json.dumps(
            relatorio,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print("Relatorio:", arquivo)
    print("AULA 19 EXECUTADA COM SUCESSO!")


if __name__ == "__main__":
    main()
