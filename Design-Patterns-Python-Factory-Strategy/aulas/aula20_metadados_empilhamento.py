"""Laboratorio da Aula 20 - Metadados e empilhamento."""

import contextlib
import io
import json
import sys
from pathlib import Path


RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from src.aula20_metadados_empilhamento import (
    somar_sem_wraps,
    somar,
    dividir,
    somar_empilhada,
    somar_ordem_invertida,
    somar_original,
    demonstrar_ordem_aplicacao,
    demonstrar_metadados,
    analisar_aula20,
)


def capturar(funcao, *args):
    saida = io.StringIO()

    with contextlib.redirect_stdout(saida):
        resultado = funcao(*args)

    return {
        "resultado": resultado,
        "saida": saida.getvalue(),
    }


def main():
    print("===== AULA 20 - METADADOS E EMPILHAMENTO =====")

    print("\n1. ANTES DE FUNCTOOLS.WRAPS")

    sem_wraps = capturar(somar_sem_wraps, 2, 3)

    print("Nome:", somar_sem_wraps.__name__)
    print("Resultado:", sem_wraps["resultado"])
    print(sem_wraps["saida"], end="")

    print("\n2. DEPOIS DE FUNCTOOLS.WRAPS")

    com_wraps = capturar(somar, 2, 3)

    print("Nome:", somar.__name__)
    print("Documentacao:", somar.__doc__)
    print("Resultado:", com_wraps["resultado"])
    print(com_wraps["saida"], end="")

    print("\n3. DECORATOR EM OUTRA FUNCAO")

    divisao = capturar(dividir, 10, 2)

    print("Nome:", dividir.__name__)
    print(divisao["saida"], end="")

    print("\n4. EMPILHAMENTO DE DECORATORS")

    empilhada = capturar(somar_empilhada, 2, 3)

    print(empilhada["saida"], end="")

    print("\n5. ORDEM INVERTIDA")

    invertida = capturar(
        somar_ordem_invertida, 2, 3
    )

    print(invertida["saida"], end="")

    print("\n6. APLICACAO MANUAL EQUIVALENTE")

    manual = demonstrar_ordem_aplicacao()
    manual_resultado = capturar(manual, 2, 3)

    print(manual_resultado["saida"], end="")

    print("\n7. FUNCAO ORIGINAL")

    print("Resultado:", somar_original(2, 3))

    print("\n8. METADADOS")

    metadados = demonstrar_metadados()

    print(json.dumps(
        metadados,
        indent=2,
        ensure_ascii=False,
    ))

    print("\n9. ANALISE DA AULA")

    analise = analisar_aula20()

    print(json.dumps(
        analise,
        indent=2,
        ensure_ascii=False,
    ))

    if metadados["sem_wraps"]["nome"] != "wrapper":
        raise RuntimeError(
            "Nome sem wraps deveria ser wrapper"
        )

    if metadados["com_wraps"]["nome"] != "somar":
        raise RuntimeError(
            "functools.wraps nao preservou o nome"
        )

    if com_wraps["resultado"] != 5:
        raise RuntimeError("Resultado da soma incorreto")

    if empilhada["saida"].count(
        "Executando somar_empilhada"
    ) != 3:
        raise RuntimeError(
            "Empilhamento nao repetiu o log 3 vezes"
        )

    if empilhada["resultado"] is not None:
        raise RuntimeError(
            "Repetir deveria retornar None nesta aula"
        )

    if manual_resultado["saida"].count(
        "Executando operacao"
    ) != 3:
        raise RuntimeError(
            "Aplicacao manual nao foi equivalente"
        )

    relatorio = {
        "aula": 20,
        "titulo": "Preservando metadados e empilhando decoradores",
        "sem_wraps": sem_wraps,
        "com_wraps": com_wraps,
        "divisao": divisao,
        "empilhada": empilhada,
        "ordem_invertida": invertida,
        "aplicacao_manual": manual_resultado,
        "metadados": metadados,
        "analise": analise,
    }

    destino = (
        RAIZ / "resultados"
        / "aula20_metadados_empilhamento.json"
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
    print("AULA 20 EXECUTADA COM SUCESSO!")


if __name__ == "__main__":
    main()
