"""Laboratorio da Aula 26 - Strategy com funcoes."""

import json
import sys
from pathlib import Path


RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from src.aula26_funcoes_lambdas import (
    calcular_preco,
    desconto_vip,
    desconto_novo,
    desconto_funcionario,
    sem_desconto,
    desconto_estudante,
    black_friday,
    parceria_empresa_x,
    parceria_empresa_y,
    soma,
    criar_estrategia_percentual,
    demonstrar_primeira_classe,
    demonstrar_lambda_direta,
    demonstrar_divergencia_black_friday,
    analisar_aula26,
)


def main():
    print("===== AULA 26 - FUNCOES E LAMBDAS =====")

    print("\n1. ESTRATEGIAS COMO FUNCOES")

    exemplos = [
        ("vip", 200, desconto_vip),
        ("novo", 200, desconto_novo),
        ("funcionario", 200, desconto_funcionario),
        ("sem_desconto", 200, sem_desconto),
        ("estudante", 200, desconto_estudante),
        ("black_friday", 600, black_friday),
        ("empresa_x", 200, parceria_empresa_x),
        ("empresa_y", 200, parceria_empresa_y),
    ]

    resultados = []

    for nome, total, estrategia in exemplos:
        preco = calcular_preco(total, estrategia)

        resultados.append({
            "estrategia": nome,
            "total": total,
            "preco": preco,
        })

        print(
            f"{nome}: R$ {total:.2f} "
            f"-> R$ {preco:.2f}"
        )

    print("\n2. EXPRESSAO LAMBDA PARA SOMA")
    resultado_soma = soma(3, 5)
    print("soma(3, 5):", resultado_soma)

    print("\n3. LAMBDA DIRETA")
    resultado_inline = demonstrar_lambda_direta()
    print("Compra de R$ 300:", resultado_inline)

    print("\n4. FUNCOES DE PRIMEIRA CLASSE")
    primeira_classe = demonstrar_primeira_classe()

    print(json.dumps(
        primeira_classe,
        indent=2,
        ensure_ascii=False,
    ))

    print("\n5. FUNCAO RETORNANDO OUTRA FUNCAO")
    desconto_especial = criar_estrategia_percentual(0.6)
    resultado_especial = calcular_preco(
        200, desconto_especial
    )

    print("Desconto especial:", resultado_especial)

    print("\n6. DIVERGENCIA NA BLACK FRIDAY")
    divergencia = demonstrar_divergencia_black_friday()

    print(json.dumps(
        divergencia,
        indent=2,
        ensure_ascii=False,
    ))

    print("\n7. ANALISE")
    analise = analisar_aula26()

    print(json.dumps(
        analise,
        indent=2,
        ensure_ascii=False,
    ))

    esperados = [
        160.0,
        180.0,
        140.0,
        200,
        170.0,
        540.0,
        160.0,
        165.0,
    ]

    obtidos = [item["preco"] for item in resultados]

    if len(obtidos) != len(esperados):
        raise RuntimeError("Quantidade de estrategias incorreta")

    for nome, obtido, esperado in zip(
        [item["estrategia"] for item in resultados],
        obtidos,
        esperados,
    ):
        if abs(obtido - esperado) > 1e-9:
            raise RuntimeError(
                f"Preco incorreto para {nome}: "
                f"{obtido} != {esperado}"
            )

    if resultado_soma != 8:
        raise RuntimeError("Lambda de soma incorreta")

    if resultado_inline != 225:
        raise RuntimeError("Lambda inline incorreta")

    if resultado_especial != 120:
        raise RuntimeError("Estrategia retornada incorreta")

    if primeira_classe["precos_lista"] != [
        160.0, 180.0, 200
    ]:
        raise RuntimeError("Funcoes na lista incorretas")

    if divergencia["valores_coincidem"]:
        raise RuntimeError(
            "Divergencia da transcricao nao identificada"
        )

    relatorio = {
        "aula": 26,
        "titulo": analise["titulo"],
        "estrategias": resultados,
        "soma_lambda": resultado_soma,
        "lambda_inline": resultado_inline,
        "funcoes_primeira_classe": primeira_classe,
        "estrategia_retornada": resultado_especial,
        "black_friday": divergencia,
        "analise": analise,
    }

    destino = (
        RAIZ / "resultados"
        / "aula26_funcoes_lambdas.json"
    )

    destino.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    destino.write_text(
        json.dumps(
            relatorio,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print("\nRELATORIO:", destino)
    print("AULA 26 EXECUTADA COM SUCESSO!")


if __name__ == "__main__":
    main()
