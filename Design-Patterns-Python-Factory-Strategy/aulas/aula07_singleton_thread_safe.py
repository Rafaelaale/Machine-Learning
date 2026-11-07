"""Laboratorio da Aula 07."""

import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from src.aula07_singleton_thread_safe import (
    Singleton,
    executar_concorrencia,
    reiniciar_para_testes,
)


def main():
    print("===== AULA 07 - SINGLETON THREAD SAFE =====")

    print("\n1. INSTANCIACAO NORMAL")
    reiniciar_para_testes()

    s1 = Singleton()
    s2 = Singleton()

    print("s1 is s2:", s1 is s2)
    print("Criacoes:", Singleton.quantidade_criacoes())

    print("\n2. TESTE COM 100 THREADS")
    reiniciar_para_testes()

    resultado = executar_concorrencia(100)

    print("Threads:", resultado["threads"])
    print(
        "Instancias distintas:",
        resultado["instancias_distintas"],
    )
    print("Criacoes:", resultado["criacoes"])
    print("Todas iguais:", resultado["mesma_instancia"])

    print("\n3. REPETINDO O EXPERIMENTO")
    repeticoes = []

    for numero in range(1, 6):
        reiniciar_para_testes()
        teste = executar_concorrencia(100)

        valido = (
            teste["mesma_instancia"]
            and teste["criacoes"] == 1
        )

        repeticoes.append(valido)

        print(
            f"Rodada {numero}: "
            f"{teste['instancias_distintas']} instancia(s), "
            f"{teste['criacoes']} criacao(oes)"
        )

    if not all(repeticoes):
        raise RuntimeError(
            "Falha na validacao da concorrencia"
        )

    relatorio = {
        "aula": 7,
        "titulo": "Singleton Thread Safe",
        "implementacao": "Lock e dupla verificacao",
        "threads_por_rodada": 100,
        "rodadas_adicionais": 5,
        "todas_as_rodadas_aprovadas": all(repeticoes),
        "instancia_compartilhada": True,
        "criacoes_por_rodada": 1,
    }

    destino = (
        BASE / "resultados"
        / "aula07_singleton_thread_safe.json"
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
    print("AULA 07 EXECUTADA COM SUCESSO!")


if __name__ == "__main__":
    main()
