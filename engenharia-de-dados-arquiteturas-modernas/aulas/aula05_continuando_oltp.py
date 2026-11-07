"""Executa a criacao e validacao do modelo logico."""

import json
import sys
from pathlib import Path


BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from src.aula05_modelo_logico import (
    criar_modelo,
    registrar_venda,
    estrutura_tabelas,
    resumo_operacional,
)


def main():
    banco = (
        BASE / "dados" / "processed"
        / "minishop_modelo_logico_aula05.db"
    )

    print("===== AULA 05 - MODELO LOGICO =====")

    if not banco.exists():
        criar_modelo(banco)
        print("Novo banco criado")
    else:
        print("Banco existente preservado")

    print("\n1. INSPECIONANDO TABELAS")
    tabelas = estrutura_tabelas(banco)

    for nome, colunas in tabelas.items():
        chaves = [
            c["coluna"]
            for c in sorted(
                colunas,
                key=lambda x: x["pk_ordem"],
            )
            if c["pk_ordem"] > 0
        ]

        print(f"{nome}: PK = {chaves}")

    print("\n2. REGISTRANDO COMPRA")

    venda = registrar_venda(banco, quantidade=2)
    print(venda)

    print("\n3. RESULTADO OPERACIONAL")

    resumo = resumo_operacional(banco)
    print(resumo)

    print("\n4. SALVANDO RELATORIO")

    destino = (
        BASE / "resultados"
        / "aula05_modelo_logico.json"
    )

    resultado = {
        "aula": 5,
        "tema": "Modelo logico relacional",
        "tabelas": tabelas,
        "venda": venda,
        "resumo": resumo,
        "observacoes": [
            "Chave primaria composta em itens_pedido",
            "Chave unica na fatura por pedido",
            "Movimento de estoque relacionado ao item",
            "Base independente das aulas anteriores",
            "Exemplo didatico, nao fluxo completo de producao",
        ],
    }

    destino.write_text(
        json.dumps(
            resultado,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print("Relatorio:", destino)
    print("AULA 05 EXECUTADA COM SUCESSO!")


if __name__ == "__main__":
    main()
