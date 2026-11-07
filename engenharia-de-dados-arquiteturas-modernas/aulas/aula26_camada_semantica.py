"""Laboratorio de camada semantica da Minishop."""

import json
import sys
from pathlib import Path


BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from src.aula26_camada_semantica import (
    executar,
    consultar_metrica,
    comparar_fontes,
)


def salvar_json(caminho, objeto):
    caminho.write_text(
        json.dumps(
            objeto,
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

    print("===== AULA 26 - CAMADA SEMANTICA =====")

    resultado = executar(oltp, lake)

    print("\n1. FONTES DE DADOS")
    print("LAKEHOUSE:", resultado["gold"])
    print("DW:", resultado["data_warehouse"])

    print("\n2. METRICAS OFICIAIS")

    for metrica, valor in resultado["bi_lakehouse"].items():
        print(metrica, "=", valor)

    print("\n3. COMPARANDO TICKET MEDIO")
    ticket = comparar_fontes(
        "ticket_medio",
        resultado["gold"],
        resultado["data_warehouse"],
    )

    print(json.dumps(
        ticket, indent=2, ensure_ascii=False
    ))

    print("\n4. FATURAMENTO POR MES")
    print(json.dumps(
        consultar_metrica(
            "faturamento",
            "lakehouse",
            gold=resultado["gold"],
            dimensao="mes",
        ),
        indent=2,
        ensure_ascii=False,
    ))

    print("\n5. AUDITORIA DAS DEFINICOES")
    print(json.dumps(
        resultado["auditoria"],
        indent=2,
        ensure_ascii=False,
    ))

    catalogo = (
        BASE / "resultados"
        / "aula26_catalogo_semantico.json"
    )

    relatorio = (
        BASE / "resultados"
        / "aula26_camada_semantica.json"
    )

    salvar_json(
        catalogo,
        resultado["catalogo_semantico"],
    )

    salvar_json(relatorio, resultado)

    print("\nCATALOGO:", catalogo)
    print("RELATORIO:", relatorio)
    print("AULA 26 EXECUTADA COM SUCESSO!")


if __name__ == "__main__":
    main()
