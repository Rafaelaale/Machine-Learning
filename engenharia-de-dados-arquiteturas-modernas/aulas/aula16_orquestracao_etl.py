"""Executa a Aula 16, identificando periodo real do OLTP."""

import json
import sqlite3
import sys
from contextlib import closing
from pathlib import Path


BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from src.aula16_orquestracao_etl import (
    executar_etl,
    indicadores,
)


def main():
    origem = (
        BASE / "dados" / "processed"
        / "minishop_modelo_logico_aula05.db"
    )

    destino = (
        BASE / "dados" / "processed"
        / "minishop_orquestrado_aula16.db"
    )

    print("===== AULA 16 - ORQUESTRACAO ETL =====")

    # Usa o intervalo realmente existente no OLTP
    # para que a aula nao dependa da data atual.
    with closing(
        sqlite3.connect(
            origem.resolve().as_uri() + "?mode=ro",
            uri=True,
        )
    ) as con:
        inicio, fim = con.execute(
            """
            SELECT
                MIN(substr(data_pedido, 1, 10)),
                MAX(substr(data_pedido, 1, 10))
            FROM pedidos
            WHERE estado = 'confirmado'
            """
        ).fetchone()

    if inicio is None:
        raise ValueError(
            "OLTP sem pedidos confirmados para demonstracao"
        )

    print("\n1. PARAMETROS")
    print("Data_Inicial:", inicio)
    print("Data_Final:", fim)

    print("\n2. EXECUTANDO ETL")
    carga = executar_etl(
        origem, destino, inicio, fim
    )

    print(json.dumps(
        carga, indent=2, ensure_ascii=False
    ))

    print("\n3. INDICADORES")
    metricas = indicadores(destino)

    print(json.dumps(
        metricas, indent=2, ensure_ascii=False
    ))

    if (
        metricas["faturamento_centavos"]
        != carga["fatos"]["faturamento_centavos"]
    ):
        raise RuntimeError(
            "Divergencia entre carga e indicadores"
        )

    print("\n4. SALVANDO RELATORIO")

    arquivo = (
        BASE / "resultados"
        / "aula16_orquestracao_etl.json"
    )

    relatorio = {
        "aula": 16,
        "tema": "Continuando a criacao do ETL do Minishop",
        "carga": carga,
        "indicadores": metricas,
        "limitacoes": [
            "Canal de venda ausente no OLTP",
            "Promocao por pedido ausente no OLTP",
            "Faturas sem vencimento e saldo aberto",
            "Data do movimento de inventario derivada do pedido",
            "Dados geograficos e demograficos ausentes",
            "Sem agendamento automatico nesta etapa",
        ],
    }

    arquivo.write_text(
        json.dumps(
            relatorio, indent=2, ensure_ascii=False
        ),
        encoding="utf-8",
    )

    print("Relatorio:", arquivo)
    print("AULA 16 EXECUTADA COM SUCESSO!")


if __name__ == "__main__":
    main()
