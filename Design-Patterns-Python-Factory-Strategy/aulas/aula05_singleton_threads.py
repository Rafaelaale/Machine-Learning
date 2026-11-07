"""Executavel da Aula 05 - Singleton Thread Safe."""

import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from src.aula05_singleton_threads import executar


def main():
    print("===== AULA 05 - SINGLETON E THREADS =====")

    resultado = executar(100)

    print("\n1. EXPERIMENTO REAL COM 100 THREADS")
    print(json.dumps(
        resultado["experimento_real"],
        indent=2,
        ensure_ascii=False,
    ))

    print(
        "\nObservacao: obter apenas uma instancia "
        "nao comprova seguranca entre threads."
    )

    print("\n2. CORRIDA CONTROLADA COM 2 THREADS")
    print(json.dumps(
        resultado["experimento_controlado"],
        indent=2,
        ensure_ascii=False,
    ))

    print("\n3. CONCLUSAO")
    print(
        "Corrida demonstrada:",
        resultado["corrida_demonstrada"],
    )
    print(
        "Singleton protegido por Lock:",
        resultado["thread_safe_implementado"],
    )

    if not resultado["corrida_demonstrada"]:
        raise RuntimeError(
            "A demonstracao controlada nao detectou a corrida"
        )

    destino = (
        BASE / "resultados"
        / "aula05_singleton_threads.json"
    )

    destino.write_text(
        json.dumps(
            resultado,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print("\nRELATORIO:", destino)
    print("AULA 05 EXECUTADA COM SUCESSO!")


if __name__ == "__main__":
    main()
