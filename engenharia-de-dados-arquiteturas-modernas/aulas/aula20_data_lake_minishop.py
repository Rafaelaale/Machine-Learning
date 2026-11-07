"""Aula 20 - Data Lake Minishop por dominios."""

import json
import sys
from pathlib import Path


BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from src.aula20_data_lake_minishop import (
    executar,
    ler_silver,
    ler_jsonl,
    validar_camada,
)


def main():
    oltp = (
        BASE / "dados" / "processed"
        / "minishop_modelo_logico_aula05.db"
    )
    lake = BASE / "dados" / "lake"
    dw = (
        BASE / "dados" / "processed"
        / "minishop_dw_silver_aula20.db"
    )

    print("===== AULA 20 - DATA LAKE MINISHOP =====")

    resultado = executar(oltp, lake, dw)

    bronze = resultado["bronze"]
    silver = resultado["silver"]
    gold = resultado["gold"]

    print("\n1. BRONZE POR DOMINIO")
    print("Pasta:", bronze["pasta"])
    print("Integridade:", bool(
        validar_camada(bronze["pasta"], "bronze")
    ))

    print("\n2. SILVER DESNORMALIZADA")
    dados = ler_silver(silver["pasta"])

    print("Clientes:", len(dados["clientes"]))
    print("Produtos:", len(dados["produtos"]))
    print("Itens de vendas:", len(dados["vendas"]))
    print("Movimentos:", len(dados["movimentos"]))
    print("Faturas:", len(dados["faturas"]))

    formatos = json.loads(
        (
            Path(silver["pasta"])
            / "formatos.json"
        ).read_text(encoding="utf-8")
    )

    print("Formatos binarios:", formatos)

    print("\n3. GOLD MENSAL")

    mensal = ler_jsonl(
        Path(gold["pasta"])
        / "indicadores_mensais.jsonl"
    )

    print(json.dumps(
        mensal, indent=2, ensure_ascii=False
    ))

    print("\n4. DATA WAREHOUSE ALIMENTADO PELA SILVER")

    metricas = resultado["dw"]["indicadores"]

    print(json.dumps(
        metricas, indent=2, ensure_ascii=False
    ))

    total_gold = sum(
        linha["faturamento_centavos"]
        for linha in mensal
    )
    total_dw = metricas["faturamento_centavos"]

    if total_gold != total_dw:
        raise RuntimeError(
            "Gold e DW apresentam faturamento diferente"
        )

    print("\n5. RECONCILIACAO")
    print("Gold:", total_gold)
    print("DW:", total_dw)
    print("Reconciliacao: OK")

    print("\n6. SALVANDO RELATORIO")

    relatorio = {
        "aula": 20,
        "tema": "Criando o Data Lake no Minishop",
        "snapshot_id": resultado["snapshot"]["snapshot_id"],
        "bronze": bronze,
        "silver": silver,
        "gold": gold,
        "formatos_binarios": formatos,
        "mensal": mensal,
        "dw": resultado["dw"],
        "reconciliado": total_gold == total_dw,
        "limitacoes": [
            "Dados demograficos e geograficos indisponiveis",
            "Canal e promocao por pedido indisponiveis",
            "Faturas sem vencimento e saldo aberto",
            "Data de estoque associada ao pedido",
            "Implementacao local, sem buckets de nuvem",
            "Parquet e Avro dependem de bibliotecas reais",
        ],
    }

    arquivo = (
        BASE / "resultados"
        / "aula20_data_lake_minishop.json"
    )

    arquivo.write_text(
        json.dumps(
            relatorio, indent=2, ensure_ascii=False
        ),
        encoding="utf-8",
    )

    print("Relatorio:", arquivo)
    print("AULA 20 EXECUTADA COM SUCESSO!")


if __name__ == "__main__":
    main()
