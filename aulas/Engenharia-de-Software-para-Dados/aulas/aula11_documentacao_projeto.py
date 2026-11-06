"""Audita a documentacao do projeto profissional de churn."""

import json
import sys
from pathlib import Path


BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from src.aula11_documentacao import (
    verificar_documentos,
    verificar_links_readme,
    verificar_termos_essenciais,
)


CHURN = BASE / "projetos" / "churn_profissional"


def main():
    print("=" * 60)
    print("AULA 11 - DOCUMENTACAO DE CODIGO E PROJETO")
    print("=" * 60)

    resultados = {
        "documentos": verificar_documentos(CHURN),
        "links": verificar_links_readme(CHURN),
        "resumo_executivo": verificar_termos_essenciais(CHURN),
    }

    for nome, resultado in resultados.items():
        print(f"\n{nome}:")
        print(json.dumps(
            resultado,
            indent=2,
            ensure_ascii=False,
        ))

    if not all(
        resultado["aprovado"]
        for resultado in resultados.values()
    ):
        raise AssertionError(
            "Documentacao incompleta ou inconsistente"
        )

    destino = (
        BASE
        / "resultados"
        / "aula11_auditoria_documentacao.json"
    )

    destino.write_text(
        json.dumps(
            resultados,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print("\nRELATORIO:", destino.name)
    print("AULA 11 EXECUTADA COM SUCESSO!")


if __name__ == "__main__":
    main()
