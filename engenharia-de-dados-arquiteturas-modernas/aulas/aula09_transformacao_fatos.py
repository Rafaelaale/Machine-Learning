"""Executa a Aula 09 da Minishop."""

import json
import sys
from pathlib import Path


BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from src.aula09_fatos_surrogate import (
    construir_modelo,
    consultar_dimensoes,
    reconciliar,
)


def main():
    origem = (
        BASE / "dados" / "processed"
        / "minishop_dw_aula06.db"
    )
    destino = (
        BASE / "dados" / "processed"
        / "minishop_fatos_aula09.db"
    )

    print("===== AULA 09 - FATOS E SURROGATE KEYS =====")

    print("\n1. CONSTRUINDO MODELO")
    carga = construir_modelo(origem, destino)
    print("Lote:", carga["lote_origem"])
    print("Itens importados:", carga["itens_origem"])

    print("\n2. INSPECIONANDO CHAVES SUBSTITUTAS")
    dimensoes = consultar_dimensoes(destino)

    print(json.dumps(
        dimensoes, indent=2, ensure_ascii=False
    ))

    print("\n3. COMPARANDO GRANULARIDADES")
    comparacao = reconciliar(destino)

    for nome in ("detalhe", "resumo"):
        item = comparacao[nome]

        print(
            nome,
            "- linhas:", item["linhas"],
            "- unidades:", item["unidades"],
            "- faturamento: R$",
            f'{item["faturamento_centavos"] / 100:.2f}',
        )

    print(
        "Totais reconciliados:",
        comparacao["totais_iguais"],
    )

    if not comparacao["totais_iguais"]:
        raise RuntimeError("Divergencia de faturamento")

    print("\n4. SALVANDO RELATORIO")

    resultado = {
        "aula": 9,
        "tema": "Transformando matriz em tabelas de fatos",
        "carga": carga,
        "dimensoes": dimensoes,
        "comparacao": comparacao,
        "observacoes": [
            "Chaves substitutas nas dimensoes",
            "Chaves naturais mantidas para rastreabilidade",
            "Numero do pedido como dimensao degenerada",
            "Fato detalhado por item do pedido",
            "Fato agregado por data, cliente e produto",
            "Fatos financeiros e de inventario ainda pendentes",
        ],
    }

    arquivo = (
        BASE / "resultados"
        / "aula09_fatos_surrogate_keys.json"
    )

    arquivo.write_text(
        json.dumps(
            resultado, indent=2, ensure_ascii=False
        ),
        encoding="utf-8",
    )

    print("Relatorio:", arquivo)
    print("AULA 09 EXECUTADA COM SUCESSO!")


if __name__ == "__main__":
    main()
