"""Executa a Aula 15 - Arquitetura do ETL Minishop."""

import json
import sys
from pathlib import Path


BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from src.aula15_arquitetura_etl import (
    carregar_dimensoes_oltp,
    contagens,
    versoes_cliente,
)


def main():
    origem = (
        BASE / "dados" / "processed"
        / "minishop_modelo_logico_aula05.db"
    )

    destino = (
        BASE / "dados" / "processed"
        / "minishop_arquitetura_etl_aula15.db"
    )

    print("===== AULA 15 - CRIANDO ETL MINISHOP =====")

    print("\n1. POLITICAS DAS DIMENSOES")
    politicas = {
        "cliente": "SCD Tipo 2",
        "produto": "SCD Tipo 1",
        "categoria": "SCD Tipo 1",
        "promocao": "SCD Tipo 1",
        "tempo": "SCD Tipo 1",
    }

    print(json.dumps(
        politicas, indent=2, ensure_ascii=False
    ))

    print("\n2. CARREGANDO DIMENSOES DO OLTP")
    carga = carregar_dimensoes_oltp(
        origem, destino
    )

    print(json.dumps(
        carga, indent=2, ensure_ascii=False
    ))

    print("\n3. ESTRUTURA DO DATA WAREHOUSE")
    tabelas = contagens(destino)

    print(json.dumps(
        tabelas, indent=2, ensure_ascii=False
    ))

    print("\n4. VALIDANDO CLIENTE SCD TIPO 2")
    cliente = versoes_cliente(destino, "1")

    print(json.dumps(
        cliente, indent=2, ensure_ascii=False
    ))

    print("\n5. REGISTRANDO REQUISITOS PENDENTES")
    pendencias = [
        "Fonte de cidade e estado do cliente",
        "Fonte de data de nascimento e faixa etaria",
        "Data efetiva das alteracoes historicas",
        "Fonte de promocao historica",
        "Orquestracao completa do ETL na proxima aula",
    ]

    for item in pendencias:
        print("-", item)

    print("\n6. SALVANDO RELATORIO")
    resultado = {
        "aula": 15,
        "tema": "Criando ETL do Minishop",
        "politicas": politicas,
        "carga_dimensional": carga,
        "tabelas": tabelas,
        "cliente_exemplo": cliente,
        "pendencias": pendencias,
    }

    arquivo = (
        BASE / "resultados"
        / "aula15_arquitetura_etl.json"
    )

    arquivo.write_text(
        json.dumps(
            resultado, indent=2, ensure_ascii=False
        ),
        encoding="utf-8",
    )

    print("Relatorio:", arquivo)
    print("AULA 15 EXECUTADA COM SUCESSO!")


if __name__ == "__main__":
    main()
