"""Executa o Data Warehouse dimensional da Minishop."""

import json
import sys
from pathlib import Path


BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from src.aula10_dw_minishop import (
    carregar_dw,
    contagens,
    indicadores,
    validar_reconciliacao,
)


def main():
    origem = (
        BASE / "dados" / "processed"
        / "minishop_modelo_logico_aula05.db"
    )

    destino = (
        BASE / "dados" / "processed"
        / "minishop_dw_aula10.db"
    )

    print("===== AULA 10 - DW MINISHOP =====")

    print("\n1. CONSTRUINDO MODELO DIMENSIONAL")
    carga = carregar_dw(origem, destino)
    print(json.dumps(carga, indent=2, ensure_ascii=False))

    print("\n2. CONTANDO TABELAS DE FATOS")
    tabelas = contagens(destino)
    print(json.dumps(tabelas, indent=2))

    print("\n3. CONSULTANDO INDICADORES")
    metricas = indicadores(destino)
    print(json.dumps(
        metricas, indent=2, ensure_ascii=False
    ))

    print("\n4. RECONCILIANDO COM O OLTP")
    conciliacao = validar_reconciliacao(origem, destino)
    print(json.dumps(conciliacao, indent=2))

    if not all((
        conciliacao["faturamento_reconciliado"],
        conciliacao["estoque_reconciliado"],
    )):
        raise RuntimeError("Divergencia entre OLTP e DW")

    print("\n5. DOCUMENTANDO LIMITES")
    pendencias = [
        "Cidade e estado ainda sem fonte",
        "Faixa etaria ainda sem nascimento",
        "Promocao historica ainda sem fonte",
        "Canal de acesso ainda sem fonte",
        "Vencimento financeiro ainda sem fonte",
        "Saldo em aberto ainda sem fonte",
    ]

    for item in pendencias:
        print("-", item)

    relatorio = {
        "aula": 10,
        "tema": "Continuando a criacao do DW",
        "carga": carga,
        "tabelas_fatos": tabelas,
        "indicadores": metricas,
        "reconciliacao": conciliacao,
        "pendencias": pendencias,
    }

    arquivo = (
        BASE / "resultados" / "aula10_dw_minishop.json"
    )

    arquivo.write_text(
        json.dumps(
            relatorio, indent=2, ensure_ascii=False
        ),
        encoding="utf-8",
    )

    print("\nRelatorio:", arquivo)
    print("AULA 10 EXECUTADA COM SUCESSO!")


if __name__ == "__main__":
    main()
