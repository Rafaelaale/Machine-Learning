"""Executa a Aula 27 sem modificar o projeto original."""

import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from src.aula27_consumo_semantico import executar


def main():
    oltp = (
        BASE / "dados" / "processed"
        / "minishop_modelo_logico_aula05.db"
    )

    lake = BASE / "dados" / "lake"

    pasta_exemplo = (
        BASE / "dados" / "exemplos" / "aula27"
    )

    resultado = executar(
        oltp, lake, pasta_exemplo
    )

    print("===== AULA 27 - CONSUMO SEMANTICO =====")

    print("\n1. RELATORIOS DAS AREAS")
    print(json.dumps(
        resultado["relatorios"],
        indent=2,
        ensure_ascii=False,
    ))

    print("\n2. CONFLITO DE SIGNIFICADO - EXEMPLO DIDATICO")
    print(json.dumps(
        resultado["conflito_didatico"],
        indent=2,
        ensure_ascii=False,
    ))

    print("\n3. AUDITORIA")
    print(json.dumps(
        resultado["auditoria"],
        indent=2,
        ensure_ascii=False,
    ))

    catalogo = (
        BASE / "resultados"
        / "aula27_catalogo_consumo.json"
    )

    relatorio = (
        BASE / "resultados"
        / "aula27_consumo_semantico.json"
    )

    catalogo.write_text(
        json.dumps(
            resultado["catalogo"],
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    relatorio.write_text(
        json.dumps(
            resultado,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print("\nCATALOGO:", catalogo)
    print("RELATORIO:", relatorio)
    print("AULA 27 EXECUTADA COM SUCESSO!")


if __name__ == "__main__":
    main()
