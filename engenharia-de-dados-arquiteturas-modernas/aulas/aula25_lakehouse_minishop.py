"""Executa a arquitetura integrada da Aula 25."""

import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from src.aula25_lakehouse_minishop import executar


def main():
    oltp = (
        BASE / "dados" / "processed"
        / "minishop_modelo_logico_aula05.db"
    )

    lake = BASE / "dados" / "lake"

    resultado = executar(oltp, lake)

    print("===== AULA 25 - LAKEHOUSE NO MINISHOP =====")

    for nome in (
        "oltp",
        "bronze",
        "silver",
        "gold_original",
        "gold_analitica",
        "lakehouse_catalogo",
        "data_warehouse",
    ):
        print(nome.upper(), resultado[nome])

    print("\n===== RECONCILIACAO =====")
    print(json.dumps(
        resultado["reconciliacao"],
        indent=2,
        ensure_ascii=False,
    ))

    print("\n===== VENDAS POR CATEGORIA =====")
    print(json.dumps(
        resultado["categorias"],
        indent=2,
        ensure_ascii=False,
    ))

    print(
        "\nLAKEHOUSE USA ARQUIVOS DA GOLD:",
        resultado["lakehouse_usa_arquivos_gold"],
    )

    destino = (
        BASE / "resultados"
        / "aula25_lakehouse_minishop.json"
    )

    destino.write_text(
        json.dumps(
            resultado,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print("RELATORIO:", destino)
    print("AULA 25 EXECUTADA COM SUCESSO!")


if __name__ == "__main__":
    main()
