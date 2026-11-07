"""Executa os modelos estrela, snowflake e pai-filho."""

import json
import sys
from pathlib import Path


BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from src.aula07_modelagem_dimensional import (
    comparar_modelos,
    consultar_hierarquia,
    gerar_modelos,
)


def main():
    origem = (
        BASE / "dados" / "processed"
        / "minishop_dw_aula06.db"
    )
    destino = (
        BASE / "dados" / "processed"
        / "minishop_modelagem_aula07.db"
    )

    print("===== AULA 07 - MATRIZ EM TABELAS =====")

    print("\n1. GERANDO MODELOS FISICOS")

    carga = gerar_modelos(origem, destino)

    print("Lote de origem:", carga["lote_origem"])
    print("Linhas importadas:", carga["linhas_importadas"])
    print("Categorias:", carga["categorias"])

    print("\n2. COMPARANDO ESTRELA E SNOWFLAKE")

    comparacao = comparar_modelos(destino)

    for nome in ("estrela", "snowflake"):
        item = comparacao[nome]
        print(
            nome,
            "- pedidos:", item["pedidos"],
            "- faturamento: R$",
            f'{item["faturamento_centavos"] / 100:.2f}',
        )

    print(
        "Agregacoes equivalentes:",
        comparacao["equivalentes"],
    )

    if not comparacao["equivalentes"]:
        raise RuntimeError(
            "Divergencia entre estrela e snowflake"
        )

    print("\n3. HIERARQUIAS GEOGRAFICAS")

    brasil = consultar_hierarquia(
        destino, "Salvador"
    )
    monaco = consultar_hierarquia(
        destino, "Monaco"
    )

    print("Regular:", brasil)
    print("Irregular:", monaco)

    assert "Brasil > Bahia > Salvador" in brasil
    assert "Monaco > Monaco" in monaco

    print("\n4. SALVANDO RELATORIO")

    relatorio = {
        "aula": 7,
        "tema": "Transformando matriz em tabelas",
        "carga": carga,
        "comparacao": comparacao,
        "hierarquia_regular": brasil,
        "hierarquia_irregular": monaco,
        "observacoes": [
            "Fonte Data Warehouse somente leitura",
            "Modelo estrela com categoria desnormalizada",
            "Modelo snowflake com categoria separada",
            "Hierarquia pai-filho demonstrada por CTE",
            "Geografia ficticia sem vinculo com vendas",
            "Nao foi realizado benchmark de desempenho",
        ],
    }

    arquivo = (
        BASE / "resultados"
        / "aula07_modelagem_dimensional.json"
    )

    arquivo.write_text(
        json.dumps(
            relatorio,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print("Relatorio:", arquivo)
    print("AULA 07 EXECUTADA COM SUCESSO!")


if __name__ == "__main__":
    main()
