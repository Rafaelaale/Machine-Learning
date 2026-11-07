"""Demonstracao pratica do Singleton por modulo."""

import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))


def executar():
    print("===== AULA 01 - SINGLETON POR MODULOS =====")

    print("\n1. PRIMEIRA IMPORTACAO")
    from singleton1_4 import singleton as primeira

    print("\n2. SEGUNDA IMPORTACAO")
    from singleton1_4 import singleton as segunda

    print("\n3. IMPORTANDO O MODULO COMPLETO")
    import singleton1_4

    print("\n4. CONFERINDO IDENTIDADE")
    print("Mesmo objeto:", primeira is segunda)
    print("Mesmo objeto no modulo:", primeira is singleton1_4.singleton)
    print("Modulo no cache:", "singleton1_4" in sys.modules)

    print("\n5. COMPARTILHANDO ESTADO")
    print("Contador inicial:", primeira.contador)

    primeira.incrementar()

    print("Contador visto pela segunda referencia:", segunda.contador)

    print("\n6. CARREGANDO CONFIGURACOES")
    from singleton1_4 import dados

    print(json.dumps(
        dados,
        ensure_ascii=False,
        indent=2
    ))

    print("\n7. IMPORTANDO CONFIGURACAO NOVAMENTE")
    from singleton1_4 import dados as outros_dados

    print("Mesmo dicionario:", dados is outros_dados)

    print("\n8. OBSERVACAO")
    print(
        "Importar novamente nao recria o objeto. "
        "Um novo processo Python possui seu proprio cache."
    )

    print("\nAULA 01 EXECUTADA COM SUCESSO!")


if __name__ == "__main__":
    executar()
