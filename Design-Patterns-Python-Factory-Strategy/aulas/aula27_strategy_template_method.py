"""Laboratorio da Aula 27 - Strategy e Template Method."""

import json
import sys
import unittest
from pathlib import Path


RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from src.aula27_strategy_template_method import (
    demonstrar_ordenacao,
    demonstrar_comparacoes,
    AUTHENTICATION_BACKENDS,
    selecionar_serializador,
    demonstrar_formularios,
    analisar_aula27,
)

from exemplos.aula27_unittest_setup import (
    TestMinhaFuncionalidade,
)


def main():
    print("===== AULA 27 - STRATEGY E TEMPLATE METHOD =====")

    print("\n1. STRATEGY COM SORT")

    ordenacao = demonstrar_ordenacao()

    for nome, frutas in ordenacao.items():
        print(f"{nome}: {frutas}")

    print("\n2. DUNDER METHODS")

    comparacoes = demonstrar_comparacoes()

    for nome, resultado in comparacoes.items():
        print(f"{nome}: {resultado}")

    print("\n3. BACKENDS DE AUTENTICACAO DJANGO")

    for backend in AUTHENTICATION_BACKENDS:
        print(backend)

    print("\n4. SERIALIZADORES CELERY")

    print("JSON:", selecionar_serializador("json"))
    print("Pickle (apenas demonstracao):",
          selecionar_serializador("pickle"))

    print("\n5. TEMPLATE METHOD - FORMULARIO")

    formularios = demonstrar_formularios()

    print(json.dumps(
        formularios,
        indent=2,
        ensure_ascii=False,
    ))

    print("\n6. TEMPLATE METHOD - UNITTEST SETUP")

    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        TestMinhaFuncionalidade
    )
    resultado_testes = unittest.TestResult()
    suite.run(resultado_testes)

    print("Testes do exemplo:", resultado_testes.testsRun)
    print("Aprovados:", resultado_testes.wasSuccessful())

    print("\n7. ANALISE DA AULA")

    analise = analisar_aula27()

    print(json.dumps(
        analise,
        indent=2,
        ensure_ascii=False,
    ))

    if sorted(ordenacao["por_tamanho"], key=len) != (
        ordenacao["por_tamanho"]
    ):
        raise RuntimeError("Ordenacao por tamanho incorreta")

    if ordenacao["alfabetica"] != sorted(
        ordenacao["original"]
    ):
        raise RuntimeError("Ordenacao alfabetica incorreta")

    if ordenacao["por_lambda"] != sorted(
        ordenacao["alfabetica"], key=len
    ):
        raise RuntimeError("Lambda de ordenacao incorreta")

    if comparacoes["alice_menor_que_bob"]:
        raise RuntimeError("Comparacao Alice/Bob incorreta")

    if not formularios["valido"]:
        raise RuntimeError("Formulario valido foi rejeitado")

    if formularios["invalido"]:
        raise RuntimeError("Formulario invalido foi aceito")

    if not resultado_testes.wasSuccessful():
        raise RuntimeError("Exemplo unittest falhou")

    arquivos_extras = [
        "exemplos/aula27_django_forms.py",
        "exemplos/aula27_configuracoes_frameworks.py",
        "exemplos/aula27_unittest_setup.py",
    ]

    for relativo in arquivos_extras:
        if not (RAIZ / relativo).is_file():
            raise RuntimeError(f"Arquivo ausente: {relativo}")

    relatorio = {
        "aula": 27,
        "ordenacao": ordenacao,
        "comparacoes": comparacoes,
        "backends_django": AUTHENTICATION_BACKENDS,
        "serializadores_celery": [
            "json",
            "pickle",
        ],
        "formularios_didaticos": formularios,
        "teste_setup": {
            "executados": resultado_testes.testsRun,
            "aprovado": resultado_testes.wasSuccessful(),
        },
        "arquivos_extras": arquivos_extras,
        "analise": analise,
    }

    destino = (
        RAIZ / "resultados"
        / "aula27_strategy_template_method.json"
    )

    destino.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    destino.write_text(
        json.dumps(
            relatorio,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print("\nRELATORIO:", destino)
    print("AULA 27 EXECUTADA COM SUCESSO!")


if __name__ == "__main__":
    main()
