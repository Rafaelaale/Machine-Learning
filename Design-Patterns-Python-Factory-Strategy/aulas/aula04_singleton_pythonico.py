"""Executa os exemplos da Aula 04."""

import json
import sys
from pathlib import Path
from pprint import pprint


BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from src.aula04_singleton_pythonico import Singleton


def executar():
    print("===== AULA 04 - SINGLETON PYTHONICO =====")

    print("\n1. PRIMEIRA INSTANCIACAO")
    s1 = Singleton()

    print("\n2. CONFIGURACAO")
    print("Campos carregados:")
    pprint(sorted(s1.dados.keys()))

    print("\n3. SEGUNDA INSTANCIACAO")
    s2 = Singleton()

    print("s1 is s2:", s1 is s2)
    print("id(s1):", id(s1))
    print("id(s2):", id(s2))

    print("\n4. CHAMADA DIRETA DE __new__")
    s3 = Singleton.__new__(Singleton)

    print("s1 is s3:", s1 is s3)
    print("id(s3):", id(s3))

    print("\n5. COMPARTILHAMENTO DOS DADOS")
    print("s1.dados is s2.dados:", s1.dados is s2.dados)
    print("s1.dados is s3.dados:", s1.dados is s3.dados)

    print("\n6. LEITURA DO ARQUIVO")
    print(
        "Quantidade de leituras:",
        Singleton.quantidade_leituras(),
    )

    print("\n7. LIMITACAO")
    print(
        "O Singleton ainda nao possui protecao "
        "contra chamadas concorrentes de threads."
    )

    resultado = {
        "aula": 4,
        "padrao": "Singleton",
        "implementacao": "__new__",
        "s1_is_s2": s1 is s2,
        "s1_is_s3": s1 is s3,
        "dados_compartilhados": s1.dados is s2.dados,
        "leituras_configuracao": Singleton.quantidade_leituras(),
        "chaves_configuracao": sorted(s1.dados.keys()),
        "thread_safe": False,
    }

    destino = (
        BASE / "resultados"
        / "aula04_singleton_pythonico.json"
    )

    destino.parent.mkdir(
        parents=True,
        exist_ok=True,
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
    print("AULA 04 EXECUTADA COM SUCESSO!")


if __name__ == "__main__":
    executar()
