"""Laboratorio da Aula 21 - Decorando classes."""

import contextlib
import io
import json
import sys
from pathlib import Path


RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from src.aula21_decorando_classes import (
    singleton,
    Configuracao,
    registry,
    registrar,
    PagamentoPix,
    PagamentoCartao,
    demonstrar_singleton,
    demonstrar_registry,
    analisar_aula21,
)


def main():
    print("===== AULA 21 - DECORANDO CLASSES =====")

    print("\n1. DECORATOR SINGLETON")

    saida = io.StringIO()

    with contextlib.redirect_stdout(saida):
        singleton_resultado = demonstrar_singleton()

    mensagem = saida.getvalue()

    print(mensagem, end="")
    print("Valor:", singleton_resultado["valor"])
    print(
        "Mesma instancia:",
        singleton_resultado["mesma_instancia"],
    )

    print("\n2. PRESERVACAO DE METADADOS")

    print("Nome decorado:", Configuracao.__name__)
    print(
        "Classe original:",
        Configuracao.__wrapped__.__name__,
    )
    print(
        "Configuracao ainda e classe?",
        isinstance(Configuracao, type),
    )

    print("\n3. REGISTRY POR DECORATORS")

    registry_resultado = demonstrar_registry()

    print("Chaves:", registry_resultado["chaves"])
    print("PIX:", registry_resultado["pix"])
    print("Cartao:", registry_resultado["cartao"])

    print("\n4. ACESSANDO CLASSES REGISTRADAS")

    print("Classe PIX:", registry["pix"])
    print("Classe cartao:", registry["cartao"])

    print("\n5. REGISTRO DINAMICO DE NOVA CLASSE")

    # Registro isolado somente para o laboratorio.
    # Nao modifica o registry global da transcricao.
    registro_extra = {}

    def registrar_extra(nome):
        def decorator(cls):
            registro_extra[nome] = cls
            return cls
        return decorator

    @registrar_extra("boleto")
    class PagamentoBoleto:
        pass

    print(
        "Boleto registrado:",
        registro_extra["boleto"] is PagamentoBoleto,
    )

    print("\n6. ANALISE")

    analise = analisar_aula21()

    print(json.dumps(
        analise,
        indent=2,
        ensure_ascii=False,
    ))

    if mensagem.count("Carregando configurações...") != 1:
        raise RuntimeError(
            "Singleton inicializou mais de uma vez"
        )

    if not singleton_resultado["mesma_instancia"]:
        raise RuntimeError("Singleton retornou objetos distintos")

    if singleton_resultado["valor"] != 42:
        raise RuntimeError("Valor da configuracao incorreto")

    if registry_resultado["chaves"] != ["cartao", "pix"]:
        raise RuntimeError("Registry incompleto")

    if not registry_resultado["pix_preserva_classe"]:
        raise RuntimeError("Decorator alterou classe PIX")

    if not registry_resultado["cartao_preserva_classe"]:
        raise RuntimeError("Decorator alterou classe cartao")

    relatorio = {
        "aula": 21,
        "titulo": "Decorando classes",
        "singleton": singleton_resultado,
        "mensagem_de_inicializacao": mensagem.strip(),
        "registry": registry_resultado,
        "registro_adicional": {
            "chave": "boleto",
            "classe": PagamentoBoleto.__name__,
        },
        "analise": analise,
    }

    destino = (
        RAIZ / "resultados"
        / "aula21_decorando_classes.json"
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
    print("AULA 21 EXECUTADA COM SUCESSO!")


if __name__ == "__main__":
    main()
