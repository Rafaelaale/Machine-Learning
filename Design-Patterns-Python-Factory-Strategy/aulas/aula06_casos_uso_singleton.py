"""Laboratorio da Aula 06."""

import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from src.aula06_casos_uso_singleton import executar


def main():
    print("===== AULA 06 - CASOS DE USO DO SINGLETON =====")

    resultado = executar()

    for titulo, chave in (
        ("1. NONE", "none"),
        ("2. TRUE E FALSE", "booleanos"),
        ("3. FLUXOS SYS", "fluxos"),
        ("4. LOGGING", "logging"),
        ("5. SQLALCHEMY", "sqlalchemy"),
    ):
        print("\n" + titulo)

        print(json.dumps(
            resultado[chave],
            ensure_ascii=False,
            indent=2,
        ))

    destino = (
        BASE / "resultados"
        / "aula06_casos_uso_singleton.json"
    )

    destino.parent.mkdir(parents=True, exist_ok=True)

    destino.write_text(
        json.dumps(
            resultado,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print("\nRELATORIO:", destino)
    print("AULA 06 EXECUTADA COM SUCESSO!")


if __name__ == "__main__":
    main()
