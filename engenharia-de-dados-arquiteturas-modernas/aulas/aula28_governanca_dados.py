"""Laboratorio de governanca da Minishop - Aula 28."""

import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from src.aula28_governanca_dados import executar


def salvar(caminho, conteudo):
    caminho.write_text(
        json.dumps(
            conteudo,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def main():
    oltp = (
        BASE / "dados" / "processed"
        / "minishop_modelo_logico_aula05.db"
    )

    lake = BASE / "dados" / "lake"

    print("===== AULA 28 - GOVERNANCA DOS DADOS =====")

    resultado = executar(oltp, lake)

    print("\n1. CATALOGO")
    catalogo = resultado["catalogo"]

    print(
        "Tabelas DW:",
        list(catalogo["data_warehouse"]["tabelas"]),
    )
    print(
        "Tabelas Lakehouse:",
        list(catalogo["lakehouse"]["tabelas"]),
    )
    print(
        "Metricas oficiais:",
        list(catalogo["camada_semantica"]["metricas"]),
    )

    print("\n2. LINHAGEM")
    for etapa in resultado["linhagem"]["etapas"]:
        print(
            etapa["origem"],
            "->",
            etapa["destino"],
            ":",
            etapa["operacao"],
        )

    print("\n3. QUALIDADE")
    print(json.dumps(
        resultado["qualidade"],
        indent=2,
        ensure_ascii=False,
    ))

    print("\n4. PRESERVACAO")
    print("Dados preservados:", resultado["dados_preservados"])

    pasta = BASE / "resultados"

    arquivos = {
        "aula28_catalogo_dados.json":
            resultado["catalogo"],
        "aula28_linhagem_dados.json":
            resultado["linhagem"],
        "aula28_qualidade_dados.json":
            resultado["qualidade"],
        "aula28_governanca_dados.json":
            resultado,
    }

    print("\n5. SALVANDO RELATORIOS")

    for nome, conteudo in arquivos.items():
        caminho = pasta / nome
        salvar(caminho, conteudo)
        print("SALVO:", caminho)

    print("\nAULA 28 EXECUTADA COM SUCESSO!")


if __name__ == "__main__":
    main()
