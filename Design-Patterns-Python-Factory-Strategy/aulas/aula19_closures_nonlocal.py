"""Laboratorio da Aula 19 - Closures e nonlocal."""

import contextlib
import io
import json
import sys
from pathlib import Path


RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from src.aula19_closures_nonlocal import (
    repetir,
    limite,
    imprime,
    diz_ola_repetida,
    say_hello,
    criar_ola_limitado,
    criar_contador,
    analisar_aula19,
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
    print("===== AULA 19 - CLOSURES E NONLOCAL =====")

    print("\n1. DECORATOR COM PARAMETRO: REPETIR(5)")

    repeticao_cinco = capturar(imprime)

    for linha in repeticao_cinco["linhas"]:
        print(linha)

    print("\n2. APLICACAO MANUAL: REPETIR(3)")

    repeticao_ola = capturar(diz_ola_repetida)

    for linha in repeticao_ola["linhas"]:
        print(linha)

    print("\n3. REUTILIZANDO O DECORATOR")

    repeticao_ingles = capturar(say_hello)

    for linha in repeticao_ingles["linhas"]:
        print(linha)

    print("\n4. DECORATOR LIMITE(3)")

    diz_ola = criar_ola_limitado(3)

    chamadas = []

    for numero in range(1, 5):
        execucao = capturar(diz_ola)
        chamadas.append(execucao)

        print(
            f"Chamada {numero}:",
            " | ".join(execucao["linhas"]),
        )

    print("\n5. CLOSURE E NONLOCAL")

    consultar, decrementar = criar_contador(3)

    valores = [
        consultar(),
        decrementar(),
        decrementar(),
        consultar(),
    ]

    print("Evolucao do contador:", valores)

    print("\n6. ANALISE")

    analise = analisar_aula19()

    print(json.dumps(
        analise,
        indent=2,
        ensure_ascii=False,
    ))

    if len(repeticao_cinco["linhas"]) != 5:
        raise RuntimeError("Repetir(5) nao executou 5 vezes")

    if len(repeticao_ola["linhas"]) != 3:
        raise RuntimeError("Repetir(3) nao executou 3 vezes")

    if len(repeticao_ingles["linhas"]) != 3:
        raise RuntimeError("Reutilizacao do decorator incorreta")

    if len(chamadas) != 4:
        raise RuntimeError("Numero de chamadas incorreto")

    if chamadas[3]["linhas"] != [
        "Limite de chamadas atingido."
    ]:
        raise RuntimeError("Limite de chamadas nao aplicado")

    if valores != [3, 2, 1, 1]:
        raise RuntimeError("Closure com nonlocal incorreta")

    relatorio = {
        "aula": 19,
        "titulo": "Decoradores com parametros, closures e nonlocal",
        "repetir_cinco": repeticao_cinco,
        "repetir_tres_portugues": repeticao_ola,
        "repetir_tres_ingles": repeticao_ingles,
        "limite_tres": chamadas,
        "contador_nonlocal": valores,
        "analise": analise,
    }

    destino = (
        RAIZ / "resultados"
        / "aula19_closures_nonlocal.json"
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
    print("AULA 19 EXECUTADA COM SUCESSO!")


if __name__ == "__main__":
    main()
