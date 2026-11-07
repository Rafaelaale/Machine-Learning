"""Laboratorio da Aula 03: consulta e analise separadas."""

import json
import sys
from pathlib import Path


BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from src.aula03_comparador_oltp_olap import (
    CENARIOS,
    classificar_pergunta,
    comparar_totais,
    consultar_analise,
    consultar_operacao,
    medir_execucao,
)
from src.minishop_olap import carregar_olap


def main():
    origem = BASE / "dados" / "raw" / "minishop_aula01.db"
    destino = BASE / "dados" / "processed" / "minishop_olap.db"

    if not origem.is_file():
        raise FileNotFoundError(
            "Execute primeiro o laboratorio da Aula 01"
        )

    print("===== AULA 03 - OLTP VERSUS OLAP =====")

    print("\n1. CLASSIFICANDO AS OPERACOES")
    for operacao in CENARIOS:
        print(
            f"{operacao}: {classificar_pergunta(operacao)}"
        )

    print("\n2. ATUALIZANDO FOTOGRAFIA OLAP")
    itens = carregar_olap(origem, destino)
    print("Itens importados:", itens)

    print("\n3. CONSULTA OPERACIONAL")
    operacional = medir_execucao(
        lambda: consultar_operacao(origem, 1)
    )
    print(operacional)

    print("\n4. CONSULTA ANALITICA")
    analitico = medir_execucao(
        lambda: consultar_analise(destino)
    )
    print(
        json.dumps(
            analitico["resultado"]["indicadores"],
            ensure_ascii=False,
            indent=2,
        )
    )

    print("\n5. RECONCILIANDO OS AMBIENTES")
    comparacao = comparar_totais(origem, destino)
    print("Totais reconciliados:", comparacao["reconciliado"])

    if not comparacao["reconciliado"]:
        raise RuntimeError("Totais OLTP e OLAP divergentes")

    resultado = {
        "aula": 3,
        "tema": "Comparando OLTP e OLAP",
        "itens_carregados": itens,
        "operacional": operacional,
        "analitico": analitico,
        "comparacao": comparacao,
        "aviso": (
            "Tempos locais ilustrativos, nao comparaveis como "
            "benchmark de arquiteturas."
        ),
    }

    arquivo = (
        BASE / "resultados" / "aula03_comparacao.json"
    )
    arquivo.parent.mkdir(parents=True, exist_ok=True)

    arquivo.write_text(
        json.dumps(resultado, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print("\nRelatorio:", arquivo)
    print("AULA 03 EXECUTADA COM SUCESSO!")


if __name__ == "__main__":
    main()
