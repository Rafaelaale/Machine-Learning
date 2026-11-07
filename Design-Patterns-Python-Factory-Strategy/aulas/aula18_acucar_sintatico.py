"""Laboratorio da Aula 18 - Acucar sintatico."""

import contextlib
import io
import json
import sys
from pathlib import Path


RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from src.aula18_acucar_sintatico import (
    somar_original,
    dividir_original,
    somar_explicita,
    dividir_explicita,
    somar,
    dividir,
    demonstrar_equivalencia,
    comparar_proxy_decorator,
    analisar_aula18,
)


def capturar(funcao, a, b):
    saida = io.StringIO()

    with contextlib.redirect_stdout(saida):
        resultado = funcao(a, b)

    return {
        "resultado": resultado,
        "log": saida.getvalue().strip(),
    }


def main():
    print("===== AULA 18 - ACUCAR SINTATICO =====")

    print("\n1. FUNCOES ORIGINAIS")
    print("Soma:", somar_original(3, 5))
    print("Divisao:", dividir_original(10, 2))

    print("\n2. DECORATOR APLICADO EXPLICITAMENTE")

    explicita_soma = capturar(
        somar_explicita, 3, 5
    )
    explicita_divisao = capturar(
        dividir_explicita, 10, 2
    )

    print(explicita_soma["log"])
    print(explicita_divisao["log"])

    print("\n3. DECORATOR COM @")

    arroba_soma = capturar(somar, 3, 5)
    arroba_divisao = capturar(dividir, 10, 2)

    print(arroba_soma["log"])
    print(arroba_divisao["log"])

    print("\n4. COMPROVANDO EQUIVALENCIA")

    versao_explicita, versao_arroba = (
        demonstrar_equivalencia()
    )

    equivalente_explicita = capturar(
        versao_explicita, 7, 8
    )

    equivalente_arroba = capturar(
        versao_arroba, 7, 8
    )

    print(
        "Aplicacao explicita:",
        equivalente_explicita["log"],
    )

    print(
        "Sintaxe com @:",
        equivalente_arroba["log"],
    )

    if equivalente_explicita != equivalente_arroba:
        raise RuntimeError(
            "As duas formas deveriam ser equivalentes."
        )

    if arroba_soma["resultado"] != 8:
        raise RuntimeError("Soma incorreta")

    if arroba_divisao["resultado"] != 5.0:
        raise RuntimeError("Divisao incorreta")

    print("\n5. PROXY X DECORATOR")

    comparacao = comparar_proxy_decorator()

    print(json.dumps(
        comparacao,
        indent=2,
        ensure_ascii=False,
    ))

    print("\n6. ANALISE")

    analise = analisar_aula18()

    relatorio = {
        "aula": 18,
        "titulo": "Uma pitada de acucar sintatico",
        "aplicacao_explicita": {
            "soma": explicita_soma,
            "divisao": explicita_divisao,
        },
        "sintaxe_arroba": {
            "soma": arroba_soma,
            "divisao": arroba_divisao,
        },
        "equivalencia": {
            "explicita": equivalente_explicita,
            "arroba": equivalente_arroba,
            "iguais": (
                equivalente_explicita
                == equivalente_arroba
            ),
        },
        "proxy_vs_decorator": comparacao,
        "analise": analise,
    }

    destino = (
        RAIZ / "resultados"
        / "aula18_acucar_sintatico.json"
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
    print("AULA 18 EXECUTADA COM SUCESSO!")


if __name__ == "__main__":
    main()
