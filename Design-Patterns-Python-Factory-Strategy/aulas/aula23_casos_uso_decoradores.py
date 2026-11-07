"""Laboratorio da Aula 23."""

import contextlib
import io
import json
import sys
from pathlib import Path


RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from src.aula23_casos_uso_decoradores import (
    demonstrar_fastapi,
    demonstrar_nativos,
    demonstrar_cache,
    analisar_aula23,
)


def main():
    print("===== AULA 23 - CASOS DE USO DE DECORADORES =====")

    print("\n1. FASTAPI: REGISTRO DE ROTAS")

    fastapi = demonstrar_fastapi()
    print(json.dumps(fastapi, indent=2, ensure_ascii=False))

    print("\n2. DECORADORES NATIVOS")

    nativos = demonstrar_nativos()
    print(json.dumps(nativos, indent=2, ensure_ascii=False))

    print("\n3. LRU_CACHE")

    saida = io.StringIO()

    with contextlib.redirect_stdout(saida):
        cache = demonstrar_cache()

    print(saida.getvalue(), end="")
    print(json.dumps(cache, indent=2, ensure_ascii=False))

    print("\n4. FRAMEWORKS ADICIONAIS")

    exemplos = [
        "exemplos/aula23_flask.py",
        "exemplos/aula23_click.py",
        "exemplos/aula23_django.py",
        "exemplos/aula23_celery.py",
    ]

    for caminho in exemplos:
        arquivo = RAIZ / caminho
        if not arquivo.is_file():
            raise RuntimeError(f"Arquivo ausente: {caminho}")
        print("Exemplo salvo:", caminho)

    print("\n5. ANALISE")

    analise = analisar_aula23()
    print(json.dumps(analise, indent=2, ensure_ascii=False))

    if fastapi["resposta"] != [{"id": 1, "nome": "Maria"}]:
        raise RuntimeError("Falha no endpoint FastAPI")

    if nativos["staticmethod"]["dobro_de_5"] != 10:
        raise RuntimeError("Falha no staticmethod")

    if not nativos["classmethod"]["instancia_valida"]:
        raise RuntimeError("Falha no classmethod")

    if cache["resultados"] != [6, 6, 20, 20, 20]:
        raise RuntimeError("Resultados da cache incorretos")

    if cache["hits"] != 3 or cache["misses"] != 2:
        raise RuntimeError("Contadores da cache incorretos")

    if saida.getvalue().count("Calculando") != 2:
        raise RuntimeError("Cache recalculou valores repetidos")

    relatorio = {
        "aula": 23,
        "fastapi": fastapi,
        "decoradores_nativos": nativos,
        "lru_cache": cache,
        "saida_cache": saida.getvalue().splitlines(),
        "exemplos_adicionais": exemplos,
        "analise": analise,
    }

    destino = (
        RAIZ / "resultados"
        / "aula23_casos_uso_decoradores.json"
    )

    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(
        json.dumps(relatorio, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print("\nRELATORIO:", destino)
    print("AULA 23 EXECUTADA COM SUCESSO!")


if __name__ == "__main__":
    main()
