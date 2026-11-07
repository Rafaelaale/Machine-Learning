"""Aula 19 - Fluxos de Dados com Data Lake.

FLUXO 1 - EL
    OLTP -> snapshot bruto no Data Lake.

FLUXO 2 - ETL
    Snapshot no Data Lake -> Silver -> Gold
    Snapshot no Data Lake -> Data Warehouse.

O segundo fluxo nao acessa o OLTP original.
"""

import json
import sqlite3
from contextlib import closing
from datetime import date
from pathlib import Path

from src.aula17_data_lake import (
    LAKE,
    ingerir,
    validar_snapshot,
    hash_arquivo,
)

from src.aula18_arquitetura_data_lake import (
    criar_silver,
    criar_gold,
    validar_camada,
)

from src.aula16_orquestracao_etl import (
    executar_etl,
    indicadores,
    validar_periodo,
)


BASE = Path(__file__).resolve().parent.parent


def fluxo_el(oltp, lake=LAKE):
    """Fluxo 1: extrair e preservar sem transformar para BI.

    A funcao ingerir da Aula 17 usa o Backup API
    do SQLite para produzir um snapshot consistente.
    """
    origem = Path(oltp).resolve()

    if not origem.is_file():
        raise FileNotFoundError(origem)

    resultado = ingerir(origem, lake)

    validar_snapshot(resultado["pasta"])

    return {
        "fluxo": "EL",
        "snapshot_id": resultado["snapshot_id"],
        "pasta_bronze": resultado["pasta"],
        "novo": resultado["novo"],
        "fonte": "OLTP",
        "destino": "Data Lake Bronze",
    }


def localizar_snapshot(pasta_bronze):
    """Valida a origem fisica do segundo fluxo.

    A unica origem operacional aceita nesta etapa
    e o snapshot bruto, nao o OLTP original.
    """
    pasta = Path(pasta_bronze).resolve()

    validar_snapshot(pasta)

    banco = pasta / "oltp.sqlite"

    if not banco.is_file():
        raise FileNotFoundError(banco)

    return banco


def intervalo_snapshot(pasta_bronze):
    """Descobre o periodo de pedidos existente no snapshot.

    Usa a data registrada na origem preservada.
    Nao depende do relogio do sistema operacional.
    """
    banco = localizar_snapshot(pasta_bronze)

    with closing(
        sqlite3.connect(
            banco.resolve().as_uri() + "?mode=ro",
            uri=True,
        )
    ) as con:
        linha = con.execute(
            """
            SELECT
                MIN(substr(data_pedido, 1, 10)),
                MAX(substr(data_pedido, 1, 10))
            FROM pedidos
            """
        ).fetchone()

    if linha[0] is None or linha[1] is None:
        raise ValueError(
            "Snapshot sem pedidos: informe um periodo explicito"
        )

    validar_periodo(linha[0], linha[1])

    return linha[0], linha[1]


def fluxo_etl(
    pasta_bronze,
    banco_dw,
    inicio,
    fim,
    lake=LAKE,
):
    """Fluxo 2: processa exclusivamente dados do Data Lake.

    A Bronze permanece preservada.

    A Silver valida e padroniza os dados.
    A Gold produz indicadores.
    O DW recebe fatos e dimensoes por ETL.

    Os dados utilizados para carregar o DW sao
    extraidos da copia SQLite dentro da Bronze.
    """
    validar_periodo(inicio, fim)

    snapshot_sqlite = localizar_snapshot(
        pasta_bronze
    )

    destino_dw = Path(banco_dw).resolve()

    if destino_dw == snapshot_sqlite.resolve():
        raise ValueError(
            "O DW nao pode substituir o snapshot bruto"
        )

    destino_dw.parent.mkdir(
        parents=True, exist_ok=True
    )

    # A transformacao analitica usa apenas o Lake.
    silver = criar_silver(
        pasta_bronze, lake
    )

    validar_camada(
        silver["pasta"], "silver"
    )

    gold = criar_gold(
        silver["pasta"], lake
    )

    validar_camada(
        gold["pasta"], "gold"
    )

    # O orquestrador da Aula 16 aceita um banco SQLite.
    # Aqui recebe a COPIA PRESERVADA no Data Lake,
    # e nunca o caminho do OLTP original.
    carga = executar_etl(
        snapshot_sqlite,
        destino_dw,
        inicio,
        fim,
    )

    resumo_dw = indicadores(destino_dw)

    # A Gold representa o snapshot completo.
    # A reconciliacao direta com o DW so e valida
    # quando ele contem somente o mesmo periodo.
    return {
        "fluxo": "ETL",
        "snapshot_origem": str(snapshot_sqlite),
        "periodo": {
            "inicio": inicio,
            "fim": fim,
        },
        "silver": {
            "pasta": silver["pasta"],
            "novo": silver["novo"],
        },
        "gold": {
            "pasta": gold["pasta"],
            "novo": gold["novo"],
            "indicadores": gold["resumo"],
        },
        "dw": {
            "arquivo": str(destino_dw),
            "carga": carga,
            "indicadores": resumo_dw,
        },
    }


def executar_dois_fluxos(
    oltp,
    banco_dw,
    lake=LAKE,
    inicio=None,
    fim=None,
):
    """Coordena a ingestao e o processamento separado."""
    if (inicio is None) != (fim is None):
        raise ValueError(
            "Informe as duas datas ou nenhuma"
        )

    primeiro = fluxo_el(
        oltp, lake
    )

    if inicio is None:
        inicio, fim = intervalo_snapshot(
            primeiro["pasta_bronze"]
        )

    segundo = fluxo_etl(
        primeiro["pasta_bronze"],
        banco_dw,
        inicio,
        fim,
        lake,
    )

    return {
        "ingestao": primeiro,
        "processamento": segundo,
    }


def reconstruir_sem_oltp(
    pasta_bronze,
    banco_dw,
    lake=LAKE,
    inicio=None,
    fim=None,
):
    """Reconstrucao sem receber caminho do OLTP.

    Pode ser executada mesmo que a fonte original
    tenha sido movida ou esteja indisponivel.
    """
    if (inicio is None) != (fim is None):
        raise ValueError(
            "Informe as duas datas ou nenhuma"
        )

    if inicio is None:
        inicio, fim = intervalo_snapshot(
            pasta_bronze
        )

    return fluxo_etl(
        pasta_bronze,
        banco_dw,
        inicio,
        fim,
        lake,
    )


def reconciliar_gold_dw(resultado):
    """Confronta receita e unidades do mesmo snapshot.

    Somente use quando o DW for novo e o intervalo
    abranger todos os fatos do snapshot.
    """
    gold = resultado["gold"]["indicadores"]
    dw = resultado["dw"]["indicadores"]

    faturamento_igual = (
        gold["faturamento_centavos"]
        == dw["faturamento_centavos"]
    )

    unidades_iguais = (
        gold["unidades"]
        == dw["unidades"]
    )

    return {
        "faturamento_gold_centavos": (
            gold["faturamento_centavos"]
        ),
        "faturamento_dw_centavos": (
            dw["faturamento_centavos"]
        ),
        "unidades_gold": gold["unidades"],
        "unidades_dw": dw["unidades"],
        "reconciliado": (
            faturamento_igual and unidades_iguais
        ),
    }
