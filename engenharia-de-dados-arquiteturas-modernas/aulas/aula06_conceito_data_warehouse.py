"""Executa o primeiro Data Warehouse da Minishop."""

import json
import sys
from pathlib import Path


BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from src.aula06_data_warehouse import (
    carregar_dw,
    faturamento_mensal,
    faturamento_por_categoria,
    historico_cargas,
    indicadores_dw,
)


def main():
    oltp = (
        BASE / "dados" / "processed"
        / "minishop_modelo_logico_aula05.db"
    )

    dw = (
        BASE / "dados" / "processed"
        / "minishop_dw_aula06.db"
    )

    print("===== AULA 06 - DATA WAREHOUSE =====")

    print("\n1. EXTRAINDO DADOS DO OLTP")

    carga = carregar_dw(oltp, dw)

    print("Lote:", carga["lote_id"])
    print("Linhas:", carga["linhas"])
    print("Nova carga:", carga["nova_carga"])

    print("\n2. INDICADORES DO DW")

    metricas = indicadores_dw(dw)

    print(json.dumps(
        metricas,
        ensure_ascii=False,
        indent=2,
    ))

    print("\n3. FATURAMENTO POR CATEGORIA")

    categorias = faturamento_por_categoria(dw)

    for categoria in categorias:
        print(
            categoria["categoria"],
            "- R$",
            f'{categoria["faturamento_centavos"] / 100:.2f}',
        )

    print("\n4. FATURAMENTO MENSAL")

    meses = faturamento_mensal(dw)

    for mes in meses:
        print(
            f'{mes["ano"]}-{mes["mes"]:02d}',
            "- R$",
            f'{mes["faturamento_centavos"] / 100:.2f}',
        )

    print("\n5. HISTORICO DE CARGAS")

    lotes = historico_cargas(dw)

    for lote in lotes:
        print(
            "Lote", lote["lote_id"],
            "- registros:", lote["linhas"],
        )

    print("\n6. SALVANDO RELATORIO")

    resultado = {
        "aula": 6,
        "tema": "Conceito de Data Warehouse",
        "fonte": str(oltp),
        "destino": str(dw),
        "carga": carga,
        "indicadores": metricas,
        "faturamento_por_categoria": categorias,
        "faturamento_mensal": meses,
        "historico_cargas": lotes,
        "observacoes": [
            "Fonte OLTP aberta somente para leitura",
            "Data Warehouse em arquivo separado",
            "Fotografias preservadas por lote",
            "Uma unica fonte foi integrada nesta aula",
            "Modelo didatico de pequena escala",
        ],
    }

    arquivo = (
        BASE / "resultados"
        / "aula06_data_warehouse.json"
    )

    arquivo.write_text(
        json.dumps(
            resultado,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print("Relatorio:", arquivo)
    print("AULA 06 EXECUTADA COM SUCESSO!")


if __name__ == "__main__":
    main()
