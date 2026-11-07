"""Executa ETL inicial ou incremental da Minishop."""

import json
import sys
from pathlib import Path


BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from src.aula11_etl_minishop import (
    executar_etl,
    historico_cliente,
    indicadores,
)


def main():
    origem = (
        BASE / "dados" / "processed"
        / "minishop_modelo_logico_aula05.db"
    )

    destino = (
        BASE / "dados" / "processed"
        / "minishop_etl_aula11.db"
    )

    print("===== AULA 11 - ETL MINISHOP =====")

    print("\n1. EXTRACT")
    print("Fonte:", origem)
    print("Modo: somente leitura")

    print("\n2. TRANSFORM")
    print("Validacao de campos, datas e valores")
    print("Lookups e chaves substitutas")

    print("\n3. LOAD")
    resultado = executar_etl(origem, destino)

    print(json.dumps(
        resultado,
        indent=2,
        ensure_ascii=False,
    ))

    print("\n4. INDICADORES DO DW")

    metricas = indicadores(destino)

    print(json.dumps(
        metricas,
        indent=2,
        ensure_ascii=False,
    ))

    print("\n5. HISTORICO SCD TIPO 2")

    historico = historico_cliente(destino, 1)

    print(json.dumps(
        historico,
        indent=2,
        ensure_ascii=False,
    ))

    print("\n6. SALVANDO RELATORIO")

    arquivo = (
        BASE / "resultados"
        / "aula11_etl_minishop.json"
    )

    relatorio = {
        "aula": 11,
        "tema": "Introducao ao processo ETL",
        "execucao": resultado,
        "indicadores": metricas,
        "historico_cliente_1": historico,
        "limites": [
            "Extracao completa com carga diferencial no destino",
            "Ainda nao implementa CDC",
            "SCD2 usa horario da carga como inicio da versao",
            "Mudancas retroativas em fatos exigem reprocessamento",
            "Exemplo centrado em vendas, sem dados externos",
        ],
    }

    arquivo.write_text(
        json.dumps(
            relatorio, indent=2, ensure_ascii=False
        ),
        encoding="utf-8",
    )

    print("Relatorio:", arquivo)
    print("AULA 11 EXECUTADA COM SUCESSO!")


if __name__ == "__main__":
    main()
