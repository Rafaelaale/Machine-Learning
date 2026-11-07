"""Executa os exemplos completos da Aula 10."""

import contextlib
import importlib
import io
import json
import sys
from pathlib import Path


BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from src.aula10_sqlalchemy_lazy import demonstrar_sqlalchemy


def main():
    print("===== AULA 10 - LAZY LOADING =====")

    print("\n1. CARREGAMENTO IMEDIATO")

    saida_imediata = io.StringIO()

    with contextlib.redirect_stdout(saida_imediata):
        imediato = importlib.import_module(
            "src.aula10_imediato"
        )

    print("Durante o import:")
    print(saida_imediata.getvalue().strip())

    print(
        "Tema:",
        imediato.config.data["theme"],
    )
    print(
        "Leituras:",
        imediato.config.leituras,
    )

    print("\n2. CARREGAMENTO TARDIO")

    saida_import = io.StringIO()

    with contextlib.redirect_stdout(saida_import):
        tardio = importlib.import_module(
            "src.aula10_tardio"
        )

    print(
        "Leitura durante import:",
        "Lendo arquivo" in saida_import.getvalue(),
    )

    print(
        "Leituras antes de data:",
        tardio.config.leituras,
    )

    print("Aplicação iniciada.")

    tema = tardio.config.data["theme"]

    print("Tema configurado:", tema)

    print(
        "Leituras apos primeiro acesso:",
        tardio.config.leituras,
    )

    data_primeiro = tardio.config.data
    data_segundo = tardio.config.data

    print(
        "Mesmo dicionario em memoria:",
        data_primeiro is data_segundo,
    )

    print(
        "Leituras apos segundo acesso:",
        tardio.config.leituras,
    )

    print("\n3. SQLALCHEMY LAZY LOADING")

    resultado_banco = demonstrar_sqlalchemy()

    print("Autor:", resultado_banco["autor"])
    print(
        "Books carregados antes:",
        resultado_banco["books_no_dict_antes"],
    )

    print(
        "Consultas antes do acesso:",
        resultado_banco["consultas_antes_acesso"],
    )

    print(
        "Livros carregados:",
        resultado_banco["livros"],
    )

    print(
        "Consultas depois do acesso:",
        resultado_banco["consultas_depois_acesso"],
    )

    print(
        "Consultas extras para books:",
        resultado_banco["consulta_extra_ao_acessar_books"],
    )

    print(
        "Books carregados depois:",
        resultado_banco["books_no_dict_depois"],
    )

    print(
        "Consultas depois do segundo acesso:",
        resultado_banco["consultas_apos_repeticao"],
    )

    if resultado_banco["consulta_extra_ao_acessar_books"] != 1:
        raise RuntimeError(
            "Consulta lazy nao ocorreu como esperado"
        )

    if tardio.config.leituras != 1:
        raise RuntimeError(
            "O JSON lazy foi lido mais de uma vez"
        )

    relatorio = {
        "aula": 10,
        "titulo": "Lazy Loading",
        "carregamento_imediato": {
            "tema": imediato.config.data["theme"],
            "leitura_durante_import": True,
            "leituras": imediato.config.leituras,
        },
        "carregamento_tardio": {
            "tema": tema,
            "leitura_durante_import": False,
            "leituras": tardio.config.leituras,
            "cache_reutilizado":
                data_primeiro is data_segundo,
        },
        "sqlalchemy": resultado_banco,
    }

    destino = (
        BASE / "resultados"
        / "aula10_lazy_loading.json"
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
    print("AULA 10 EXECUTADA COM SUCESSO!")


if __name__ == "__main__":
    main()
