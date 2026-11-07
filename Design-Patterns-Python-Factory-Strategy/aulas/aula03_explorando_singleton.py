"""Aula 03 - Demonstra Singleton tradicional."""

import json
import sys
from pathlib import Path
from pprint import pprint


BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from src.aula03_explorando_singleton import Config


def executar():
    print("===== AULA 03 - EXPLORANDO SINGLETON =====")

    print("\n1. PRIMEIRA CHAMADA")
    s1 = Config.get_instance()

    print("\n2. SEGUNDA CHAMADA")
    s2 = Config.get_instance()

    print("\n3. CONFIGURACAO CARREGADA")
    print("Chaves da configuracao:")
    pprint(sorted(s1.dados.keys()))

    print("\n4. IDENTIDADE")
    print("s1 is s2:", s1 is s2)
    print("id(s1):", id(s1))
    print("id(s2):", id(s2))
    print("Leituras realizadas:", Config.quantidade_leituras())

    print("\n5. CONTORNANDO O SINGLETON")
    s3 = Config()

    print("s1 is s3:", s1 is s3)
    print("Leituras apos Config():", Config.quantidade_leituras())

    print("\n6. CONFIRMANDO INSTANCIA COMPARTILHADA")
    s4 = Config.get_instance()

    print("s1 is s4:", s1 is s4)
    print("s2 is s4:", s2 is s4)

    resultado = {
        "aula": 3,
        "padrao": "Singleton",
        "implementacao": "get_instance",
        "s1_is_s2": s1 is s2,
        "s1_is_s3": s1 is s3,
        "s1_is_s4": s1 is s4,
        "leituras_configuracao": Config.quantidade_leituras(),
        "chaves_configuracao": sorted(s1.dados.keys()),
        "limitacao": (
            "A criacao direta com Config() nao e bloqueada."
        ),
    }

    destino = (
        BASE / "resultados" / "aula03_explorando_singleton.json"
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
    print("AULA 03 EXECUTADA COM SUCESSO!")


if __name__ == "__main__":
    executar()
