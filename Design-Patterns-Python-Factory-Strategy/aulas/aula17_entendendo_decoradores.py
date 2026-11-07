"""Laboratorio da Aula 17 - Decorator."""

import contextlib
import io
import json
import sys
from pathlib import Path


RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from src.aula17_entendendo_decoradores import (
    somar,
    dividir,
    somar_com_log,
    somar_com_log_2,
    dividir_com_log,
    adicionar_log,
    soma_com_log2,
    dividir_com_log2,
    analisar_decorator,
)


def executar(funcao, a, b):
    saida = io.StringIO()

    with contextlib.redirect_stdout(saida):
        resultado = funcao(a, b)

    return {
        "resultado": resultado,
        "log": saida.getvalue().strip(),
    }


def main():
    print("===== AULA 17 - DECORATOR =====")

    originais = {
        "somar": executar(somar, 3, 5),
        "dividir": executar(dividir, 10, 2),
    }

    print("\n1. FUNCOES ORIGINAIS")
    print("somar(3, 5) =", originais["somar"]["resultado"])
    print("dividir(10, 2) =", originais["dividir"]["resultado"])

    print("\n2. LOGS MANUAIS")

    manuais = {
        "somar_com_log": executar(somar_com_log, 3, 5),
        "somar_com_log_2": executar(somar_com_log_2, 3, 5),
        "dividir_com_log": executar(dividir_com_log, 10, 2),
    }

    for item in manuais.values():
        print(item["log"])

    print("\n3. DECORATOR REUTILIZAVEL")

    decoradas = {
        "somar": executar(soma_com_log2, 3, 5),
        "dividir": executar(dividir_com_log2, 10, 2),
    }

    for item in decoradas.values():
        print(item["log"])

    print("\n4. DECORACAO DINAMICA")

    outra_soma = adicionar_log(somar)
    dinamica = executar(outra_soma, 7, 8)

    print(dinamica["log"])

    if decoradas["somar"]["resultado"] != 8:
        raise RuntimeError("Resultado da soma incorreto")

    if decoradas["dividir"]["resultado"] != 5.0:
        raise RuntimeError("Resultado da divisao incorreto")

    if decoradas["somar"]["log"] != "Executando somar(3, 5) = 8":
        raise RuntimeError("Log da soma incorreto")

    if decoradas["dividir"]["log"] != "Executando dividir(10, 2) = 5.0":
        raise RuntimeError("Log da divisao incorreto")

    relatorio = {
        "aula": 17,
        "titulo": "Entendendo o que sao decoradores",
        "originais": originais,
        "manuais": manuais,
        "decoradas": decoradas,
        "dinamica": dinamica,
        "analise": analisar_decorator(),
    }

    destino = RAIZ / "resultados" / "aula17_entendendo_decoradores.json"

    destino.write_text(
        json.dumps(relatorio, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print("\nRELATORIO:", destino)
    print("AULA 17 EXECUTADA COM SUCESSO!")


if __name__ == "__main__":
    main()
