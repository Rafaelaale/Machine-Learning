"""Executa o laboratorio de Data Lake da Minishop."""

import json
import sys
from pathlib import Path


BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from src.aula17_data_lake import (
    ingerir,
    validar_snapshot,
    ler_pedidos_jsonl,
    materializar_curado,
    listar_snapshots,
)


def main():
    origem = (
        BASE / "dados" / "processed"
        / "minishop_modelo_logico_aula05.db"
    )

    lake = BASE / "dados" / "lake"

    print("===== AULA 17 - INTRODUCAO AO DATA LAKE =====")

    print("\n1. INGESTAO NA CAMADA RAW")

    ingestao = ingerir(origem, lake)

    print(json.dumps(
        ingestao, indent=2, ensure_ascii=False
    ))

    pasta = Path(ingestao["pasta"])

    print("\n2. INTEGRIDADE DO SNAPSHOT")
    print("Snapshot valido:", validar_snapshot(pasta))

    print("\n3. SCHEMA ON READ")
    pedidos = ler_pedidos_jsonl(
        pasta / "pedidos.jsonl"
    )
    print("Pedidos interpretados:", len(pedidos))

    print("\n4. MATERIALIZACAO CURATED")
    curado = materializar_curado(pasta, lake)

    print(json.dumps(
        curado["resumo"],
        indent=2,
        ensure_ascii=False,
    ))

    print("\n5. SNAPSHOTS DISPONIVEIS")
    snapshots = listar_snapshots(lake)

    print("Quantidade:", len(snapshots))

    print("\n6. SALVANDO RELATORIO")

    relatorio = {
        "aula": 17,
        "tema": "Introducao ao Data Lake",
        "ingestao": ingestao,
        "pedidos_jsonl": len(pedidos),
        "curated": curado,
        "quantidade_snapshots": len(snapshots),
        "limites": [
            "Data Lake local, nao distribuido",
            "Arquivos raw preservados por snapshot",
            "Manifest SHA-256 verifica integridade",
            "CSV e JSONL representam dados da origem",
            "Transformacoes aplicadas na leitura",
            "Nenhum servico de nuvem configurado",
        ],
    }

    arquivo = (
        BASE / "resultados"
        / "aula17_introducao_data_lake.json"
    )

    arquivo.write_text(
        json.dumps(
            relatorio, indent=2, ensure_ascii=False
        ),
        encoding="utf-8",
    )

    print("Relatorio:", arquivo)

    if not validar_snapshot(pasta):
        raise RuntimeError("Snapshot invalido")

    print("AULA 17 EXECUTADA COM SUCESSO!")


if __name__ == "__main__":
    main()
