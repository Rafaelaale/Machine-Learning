"""Executa a modelagem conceitual da Minishop."""

import json
import sys
from pathlib import Path


BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from src.aula04_modelo_conceitual import (
    ENTIDADES,
    RELACIONAMENTOS,
    REGRAS,
    PENDENCIAS,
    exportar_catalogo,
    validar_modelo,
)


def main():
    print("===== AULA 04 - MODELO CONCEITUAL MINISHOP =====")

    erros = validar_modelo()

    if erros:
        raise RuntimeError(
            "Modelo invalido: " + "; ".join(erros)
        )

    print("\n1. ENTIDADES E ATRIBUTOS")

    for entidade in ENTIDADES:
        print(
            f"{entidade.nome}: "
            f"{', '.join(entidade.atributos)}"
        )

    print("\n2. RELACIONAMENTOS E CARDINALIDADES")

    for relacao in RELACIONAMENTOS:
        print(
            f"{relacao.origem} --{relacao.verbo}--> "
            f"{relacao.destino} | "
            f"destinos por origem: {relacao.por_origem} | "
            f"origens por destino: {relacao.por_destino}"
        )

    print("\n3. REGRAS DE NEGOCIO")

    for codigo, regra in REGRAS.items():
        print(f"{codigo}: {regra}")

    print("\n4. PONTOS A VALIDAR COM A EMPRESA")

    for numero, pendencia in enumerate(PENDENCIAS, 1):
        print(f"{numero}. {pendencia}")

    resultado = exportar_catalogo()

    arquivo = (
        BASE / "resultados" / "aula04_modelo_conceitual.json"
    )

    arquivo.parent.mkdir(parents=True, exist_ok=True)

    arquivo.write_text(
        json.dumps(
            resultado, indent=2, ensure_ascii=False
        ),
        encoding="utf-8",
    )

    print("\n===== RESULTADO =====")
    print("Entidades:", len(ENTIDADES))
    print("Relacionamentos:", len(RELACIONAMENTOS))
    print("Regras:", len(REGRAS))
    print("Erros estruturais:", len(erros))
    print("Modelo aprovado pelo usuario: NAO")
    print("Relatorio:", arquivo)
    print("AULA 04 EXECUTADA COM SUCESSO!")


if __name__ == "__main__":
    main()
