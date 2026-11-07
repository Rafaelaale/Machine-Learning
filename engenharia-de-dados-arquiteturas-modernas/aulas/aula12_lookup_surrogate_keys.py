"""Executa a carga inicial e a atualizacao SCD Tipo 1."""

import json
import sys
from pathlib import Path


BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from src.aula12_lookup_surrogate_keys import (
    CLIENTES_INICIAIS,
    CLIENTES_ATUALIZADOS,
    PRODUTOS_EXEMPLO,
    VENDAS_EXEMPLO,
    carregar_clientes,
    carregar_produtos,
    carregar_fatos,
    criar_banco,
    listar_clientes,
    resumo_fatos,
)


def main():
    banco = (
        BASE / "dados" / "processed"
        / "minishop_lookup_aula12.db"
    )

    print("===== AULA 12 - LOOKUP E SURROGATE KEYS =====")

    if not banco.exists():
        criar_banco(banco)
        print("\n1. CARGA INICIAL")
        inicial = carregar_clientes(
            banco, CLIENTES_INICIAIS
        )
    else:
        print("\n1. BANCO JA EXISTENTE")
        inicial = None

    print("\n2. ATUALIZACAO SCD TIPO 1")
    atualizacao = carregar_clientes(
        banco, CLIENTES_ATUALIZADOS
    )

    print(json.dumps(
        atualizacao, indent=2, ensure_ascii=False
    ))

    print("\n3. CHAVES SUBSTITUTAS")
    clientes = listar_clientes(banco)

    print(json.dumps(
        clientes, indent=2, ensure_ascii=False
    ))

    print("\n4. LOOKUP DE PRODUTOS E FATOS")
    carregar_produtos(banco, PRODUTOS_EXEMPLO)

    carga_fatos = carregar_fatos(
        banco, VENDAS_EXEMPLO
    )
    print(carga_fatos)

    print("\n5. INDICADORES")
    indicadores = resumo_fatos(banco)

    print(json.dumps(
        indicadores, indent=2, ensure_ascii=False
    ))

    print("\n6. SALVANDO RELATORIO")
    resultado = {
        "aula": 12,
        "tema": "Lookup e Surrogate Keys",
        "carga_inicial": inicial,
        "atualizacao_scd1": atualizacao,
        "clientes": clientes,
        "carga_fatos": carga_fatos,
        "indicadores": indicadores,
        "observacoes": [
            "Exemplos didaticos da aula",
            "Codigo natural textual preservado",
            "SCD Tipo 1 nao guarda versoes antigas",
            "SCD Tipo 2 permanece na Aula 11",
            "Fatos ligados a dimensoes por SK",
        ],
    }

    arquivo = (
        BASE / "resultados"
        / "aula12_lookup_surrogate_keys.json"
    )

    arquivo.write_text(
        json.dumps(
            resultado, indent=2, ensure_ascii=False
        ),
        encoding="utf-8",
    )

    print("Relatorio:", arquivo)
    print("AULA 12 EXECUTADA COM SUCESSO!")


if __name__ == "__main__":
    main()
