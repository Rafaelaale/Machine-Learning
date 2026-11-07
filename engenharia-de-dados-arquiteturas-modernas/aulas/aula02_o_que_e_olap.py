"""Executa a primeira carga OLAP do e-commerce Minishop."""

import json
import sys
from pathlib import Path


BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from src.minishop_olap import (
    carregar_olap,
    faturamento_mensal,
    faturamento_por_produto,
    indicadores,
)


def main():
    oltp = BASE / "dados" / "raw" / "minishop_aula01.db"
    olap = BASE / "dados" / "processed" / "minishop_olap.db"

    print("===== AULA 02 - OLTP VERSUS OLAP =====")

    print("\n1. CARREGANDO DADOS TRANSACIONAIS")
    quantidade = carregar_olap(oltp, olap)
    print("Itens carregados:", quantidade)

    print("\n2. INDICADORES ANALITICOS")
    metricas = indicadores(olap)

    print(json.dumps(
        metricas, indent=2, ensure_ascii=False
    ))

    print("\n3. FATURAMENTO POR PRODUTO")
    produtos = faturamento_por_produto(olap)

    for produto in produtos:
        print(
            produto["produto"],
            "- unidades:",
            produto["unidades"],
            "- R$",
            f'{produto["faturamento_centavos"] / 100:.2f}',
        )

    print("\n4. FATURAMENTO MENSAL")
    meses = faturamento_mensal(olap)

    for mes in meses:
        print(
            f'{mes["ano"]}-{mes["mes"]:02d}',
            "- R$",
            f'{mes["faturamento_centavos"] / 100:.2f}',
        )

    print("\n5. SALVANDO RELATORIO")

    resultado = {
        "aula": 2,
        "tema": "OLAP",
        "origem": str(oltp),
        "destino": str(olap),
        "linhas_carregadas": quantidade,
        "indicadores": metricas,
        "faturamento_por_produto": produtos,
        "faturamento_mensal": meses,
        "observacoes": [
            "Ambiente analitico separado do transacional",
            "Somente pedidos confirmados e pagos",
            "Carga integral por fotografia do OLTP",
            "Categoria e regiao nao disponiveis na origem",
        ],
    }

    caminho = (
        BASE / "resultados" / "aula02_olap_minishop.json"
    )

    caminho.write_text(
        json.dumps(
            resultado, indent=2, ensure_ascii=False
        ),
        encoding="utf-8",
    )

    print("Relatorio:", caminho)
    print("\nAULA 02 EXECUTADA COM SUCESSO!")


if __name__ == "__main__":
    main()
