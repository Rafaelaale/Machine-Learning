"""Executa o laboratorio da matriz dimensional."""

import csv
import json
import sys
from collections import Counter
from pathlib import Path


BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from src.aula08_matriz_dimensional import (
    DIMENSOES,
    INDICADORES,
    REQUISITOS_PENDENTES,
    consultar_vendas,
    definicao_aging,
    matriz,
    validar_matriz,
)


def main():
    banco = (
        BASE / "dados" / "processed"
        / "minishop_dw_aula06.db"
    )

    resultados = BASE / "resultados"
    resultados.mkdir(parents=True, exist_ok=True)

    print("===== AULA 08 - CRIANDO DW MINISHOP =====")

    erros = validar_matriz()

    if erros:
        raise RuntimeError("; ".join(erros))

    print("\n1. MATRIZ DIMENSAO-INDICADOR")

    linhas = matriz()
    contagem = Counter(
        linha["situacao"] for linha in linhas
    )

    print("Indicadores:", len(INDICADORES))
    print("Dimensoes:", len(DIMENSOES))
    print("Cruzamentos:", len(linhas))
    print("Disponiveis:", contagem["disponivel"])
    print("Pendentes:", contagem["pendente"])
    print("Nao aplicaveis:", contagem["nao_aplicavel"])

    arquivo_csv = (
        resultados / "aula08_matriz_dimensao_indicador.csv"
    )

    with arquivo_csv.open(
        "w", newline="", encoding="utf-8-sig"
    ) as arquivo:
        escritor = csv.DictWriter(
            arquivo,
            fieldnames=[
                "indicador", "dimensao", "situacao"
            ],
        )
        escritor.writeheader()
        escritor.writerows(linhas)

    print("\n2. FATURAMENTO POR CATEGORIA")

    faturamento = consultar_vendas(
        banco, "valor_vendido", "categoria"
    )

    for registro in faturamento:
        print(
            registro["grupo"],
            "R$",
            f'{registro["valor"] / 100:.2f}',
        )

    print("\n3. QUANTIDADE POR PRODUTO")

    quantidade = consultar_vendas(
        banco, "quantidade", "produto"
    )

    for registro in quantidade:
        print(registro["grupo"], registro["valor"])

    print("\n4. PRECO MEDIO UNITARIO")

    preco_medio = consultar_vendas(
        banco, "preco_medio", "produto"
    )

    for registro in preco_medio:
        print(
            registro["grupo"],
            "R$",
            f'{registro["valor"] / 100:.2f}',
        )

    print("\n5. AGING LIST")

    aging = definicao_aging()
    print("Implementado:", aging["implementado"])
    print("Motivo:", aging["motivo"])

    print("\n6. REQUISITOS PENDENTES")

    for item in REQUISITOS_PENDENTES:
        print(item["campo"], "-", item["motivo"])

    relatorio = {
        "aula": 8,
        "tema": "Criando o DW da Minishop",
        "indicadores": INDICADORES,
        "dimensoes": DIMENSOES,
        "matriz": linhas,
        "resumo_situacoes": dict(contagem),
        "faturamento_categoria": faturamento,
        "quantidade_produto": quantidade,
        "preco_medio_produto": preco_medio,
        "aging_list": aging,
        "requisitos_pendentes": REQUISITOS_PENDENTES,
        "observacao": (
            "Somente os cruzamentos disponiveis foram "
            "calculados. Nenhum dado demografico, "
            "promocional ou financeiro foi inventado."
        ),
    }

    destino = (
        resultados / "aula08_matriz_dw_minishop.json"
    )

    destino.write_text(
        json.dumps(
            relatorio, ensure_ascii=False, indent=2
        ),
        encoding="utf-8",
    )

    print("\n7. RELATORIOS")
    print("CSV:", arquivo_csv)
    print("JSON:", destino)
    print("AULA 08 EXECUTADA COM SUCESSO!")


if __name__ == "__main__":
    main()
