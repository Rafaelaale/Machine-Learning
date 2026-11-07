"""Execucao da Aula 22: Lakehouse Minishop."""

import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from src.aula22_arquitetura_lakehouse import executar, validar_catalogo


def main():
    origem = (
        BASE / "dados" / "processed"
        / "minishop_modelo_logico_aula05.db"
    )
    lake = BASE / "dados" / "lake"

    resultado = executar(origem, lake)
    pasta = resultado["lakehouse"]["pasta"]
    catalogo = validar_catalogo(pasta)

    print("===== AULA 22 - ARQUITETURA DO LAKEHOUSE =====")
    print("SNAPSHOT:", resultado["snapshot"]["snapshot_id"])
    print("CATALOGO:", list(catalogo["tabelas"]))
    print("PARQUET:", pasta)

    for nome in catalogo["tabelas"]:
        arquivo = Path(pasta) / f"{nome}.parquet"
        print("ARQUIVO:", arquivo.name, arquivo.stat().st_size, "bytes")

    for titulo in ("resumo", "mensal", "produtos", "clientes"):
        print(titulo.upper())
        print(json.dumps(
            resultado[titulo], indent=2, ensure_ascii=False
        ))

    print("RECONCILIACAO:", resultado["reconciliacao"]["reconciliado"])

    arquivo = (
        BASE / "resultados" / "aula22_arquitetura_lakehouse.json"
    )
    relatorio = {
        "aula": 22,
        "tema": "Arquitetura do Lakehouse",
        "snapshot_id": resultado["snapshot"]["snapshot_id"],
        "catalogo": catalogo,
        "resumo": resultado["resumo"],
        "mensal": resultado["mensal"],
        "produtos": resultado["produtos"],
        "clientes": resultado["clientes"],
        "reconciliacao": resultado["reconciliacao"],
        "novo_dw_persistente": False,
    }
    arquivo.write_text(
        json.dumps(relatorio, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print("RELATORIO:", arquivo)
    print("AULA 22 EXECUTADA COM SUCESSO!")


if __name__ == "__main__":
    main()
