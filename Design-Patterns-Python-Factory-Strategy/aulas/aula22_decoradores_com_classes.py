"""Laboratorio da Aula 22 - Decoradores com classes."""

import contextlib
import io
import json
import sys
from pathlib import Path


RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from src.aula22_decoradores_com_classes import (
    ComLog,
    Repetir,
    somar,
    imprime,
    demonstrar_aplicacao_manual,
    analisar_aula22,
)


def capturar(funcao, *args, **kwargs):
    saida = io.StringIO()

    with contextlib.redirect_stdout(saida):
        resultado = funcao(*args, **kwargs)

    return {
        "resultado": resultado,
        "linhas": saida.getvalue().splitlines(),
    }


def main():
    print("===== AULA 22 - DECORADORES COM CLASSES =====")

    print("\n1. DECORATOR COMLOG")

    resultado_soma = capturar(somar, 3, 5)

    for linha in resultado_soma["linhas"]:
        print(linha)

    print("Resultado final:", resultado_soma["resultado"])

    print("\n2. FUNCAO DECORADA AGORA E OBJETO")

    print("Tipo:", type(somar).__name__)
    print("Callable:", callable(somar))
    print("Instancia de ComLog:", isinstance(somar, ComLog))

    print("\n3. DECORATOR PARAMETRIZADO REPETIR(5)")

    resultado_repeticao = capturar(imprime)

    for linha in resultado_repeticao["linhas"]:
        print(linha)

    print("\n4. APLICACAO MANUAL EQUIVALENTE")

    manuais = demonstrar_aplicacao_manual()

    resultado_manual_soma = capturar(
        manuais["soma_manual"], 3, 5
    )

    resultado_manual_repeticao = capturar(
        manuais["imprime_manual"]
    )

    print("Soma manual:")

    for linha in resultado_manual_soma["linhas"]:
        print(linha)

    print("Repeticao manual:")

    for linha in resultado_manual_repeticao["linhas"]:
        print(linha)

    print("\n5. COMPARANDO DECORADORES")

    print(
        "ComLog retorna resultado:",
        resultado_soma["resultado"],
    )

    print(
        "Repetir retorna resultado:",
        resultado_repeticao["resultado"],
    )

    print("\n6. ANALISE")

    analise = analisar_aula22()

    print(json.dumps(
        analise,
        indent=2,
        ensure_ascii=False,
    ))

    if resultado_soma["resultado"] != 8:
        raise RuntimeError("Resultado da soma incorreto")

    if resultado_soma["linhas"] != [
        "Executando somar (3, 5)",
        "Resultado: 8",
    ]:
        raise RuntimeError("Logs da soma incorretos")

    if len(resultado_repeticao["linhas"]) != 5:
        raise RuntimeError("Repetir(5) nao executou 5 vezes")

    if resultado_manual_soma["resultado"] != resultado_soma["resultado"]:
        raise RuntimeError("ComLog manual nao e equivalente")

    if len(resultado_manual_repeticao["linhas"]) != 3:
        raise RuntimeError("Repetir(3) manual incorreto")

    relatorio = {
        "aula": 22,
        "titulo": "Implementando decoradores com classes",
        "comlog": resultado_soma,
        "repetir_cinco": resultado_repeticao,
        "comlog_manual": resultado_manual_soma,
        "repetir_tres_manual": resultado_manual_repeticao,
        "analise": analise,
    }

    destino = (
        RAIZ / "resultados"
        / "aula22_decoradores_com_classes.json"
    )

    destino.parent.mkdir(parents=True, exist_ok=True)

    destino.write_text(
        json.dumps(
            relatorio,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print("\nRELATORIO:", destino)
    print("AULA 22 EXECUTADA COM SUCESSO!")


if __name__ == "__main__":
    main()
