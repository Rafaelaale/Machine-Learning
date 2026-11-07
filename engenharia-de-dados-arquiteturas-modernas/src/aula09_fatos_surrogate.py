"""Aula 09 - Tabelas de fatos e surrogate keys.

Cria um novo modelo dimensional a partir do ultimo
lote historico do DW da Aula 06.

Nao altera a origem.
"""

import os
import sqlite3
import tempfile
from contextlib import closing
from datetime import date
from pathlib import Path


BASE = Path(__file__).resolve().parent.parent
SCHEMA = BASE / "sql" / "aula09_fatos_surrogate_keys.sql"


def conectar(caminho):
    conexao = sqlite3.connect(str(caminho), timeout=10)
    conexao.execute("PRAGMA foreign_keys = ON")
    return conexao


def extrair_dw(banco_dw):
    """Le exclusivamente a fotografia analitica mais recente."""
    origem = Path(banco_dw).resolve()

    if not origem.is_file():
        raise FileNotFoundError(origem)

    with closing(
        sqlite3.connect(origem.as_uri() + "?mode=ro", uri=True)
    ) as conexao:
        conexao.row_factory = sqlite3.Row
        conexao.execute("BEGIN")

        resultado = conexao.execute(
            "SELECT MAX(lote_id) FROM lotes_carga"
        ).fetchone()

        lote = resultado[0]

        if lote is None:
            raise ValueError("DW sem cargas disponiveis")

        registros = conexao.execute(
            """
            SELECT
                f.pedido_id,
                f.cliente_id,
                c.nome AS cliente_nome,
                f.produto_id,
                p.nome AS produto_nome,
                p.categoria,
                f.data,
                f.quantidade,
                f.valor_centavos
            FROM fato_vendas AS f
            JOIN dim_clientes AS c
              ON c.lote_id = f.lote_id
             AND c.cliente_id = f.cliente_id
            JOIN dim_produtos AS p
              ON p.lote_id = f.lote_id
             AND p.produto_id = f.produto_id
            WHERE f.lote_id = ?
            ORDER BY f.pedido_id, f.produto_id
            """,
            (lote,),
        ).fetchall()

        conexao.commit()

    return lote, [dict(r) for r in registros]


def construir_modelo(banco_dw, banco_saida):
    """Constroi modelo novo e substitui apenas a saida da Aula 09."""
    origem = Path(banco_dw).resolve()
    destino = Path(banco_saida).resolve()

    if origem == destino:
        raise ValueError("Origem e destino nao podem ser iguais")

    lote, vendas = extrair_dw(origem)

    destino.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile(
        prefix="aula09_",
        suffix=".db",
        dir=destino.parent,
        delete=False,
    ) as arquivo:
        temporario = Path(arquivo.name)

    try:
        with closing(conectar(temporario)) as conexao:
            conexao.executescript(
                SCHEMA.read_text(encoding="utf-8")
            )

            with conexao:
                clientes = sorted({
                    (r["cliente_id"], r["cliente_nome"])
                    for r in vendas
                })

                produtos = sorted({
                    (
                        r["produto_id"],
                        r["produto_nome"],
                        r["categoria"],
                    )
                    for r in vendas
                })

                datas = sorted({
                    r["data"] for r in vendas
                })

                mapa_clientes = {}
                mapa_produtos = {}
                mapa_tempo = {}

                for sk, (codigo, nome) in enumerate(
                    clientes, start=1
                ):
                    conexao.execute(
                        """
                        INSERT INTO dim_clientes
                        (cliente_sk, cliente_id_origem, nome)
                        VALUES (?, ?, ?)
                        """,
                        (sk, codigo, nome),
                    )
                    mapa_clientes[codigo] = sk

                for sk, (codigo, nome, categoria) in enumerate(
                    produtos, start=1
                ):
                    conexao.execute(
                        """
                        INSERT INTO dim_produtos
                        (produto_sk, produto_id_origem,
                         nome, categoria)
                        VALUES (?, ?, ?, ?)
                        """,
                        (sk, codigo, nome, categoria),
                    )
                    mapa_produtos[codigo] = sk

                for sk, valor in enumerate(
                    datas, start=1
                ):
                    data = date.fromisoformat(valor)

                    conexao.execute(
                        """
                        INSERT INTO dim_tempo
                        (tempo_sk, data_calendario, ano, mes, dia)
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (
                            sk,
                            valor,
                            data.year,
                            data.month,
                            data.day,
                        ),
                    )
                    mapa_tempo[valor] = sk

                for venda in vendas:
                    if venda["quantidade"] <= 0:
                        raise ValueError(
                            "Quantidade invalida na origem"
                        )

                    if venda["valor_centavos"] < 0:
                        raise ValueError(
                            "Valor negativo na origem"
                        )

                    conexao.execute(
                        """
                        INSERT INTO fato_vendas_detalhe (
                            pedido_numero,
                            cliente_sk,
                            produto_sk,
                            tempo_sk,
                            quantidade,
                            valor_centavos
                        )
                        VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (
                            venda["pedido_id"],
                            mapa_clientes[venda["cliente_id"]],
                            mapa_produtos[venda["produto_id"]],
                            mapa_tempo[venda["data"]],
                            venda["quantidade"],
                            venda["valor_centavos"],
                        ),
                    )

                conexao.execute(
                    """
                    INSERT INTO fato_vendas_resumo (
                        tempo_sk,
                        cliente_sk,
                        produto_sk,
                        quantidade,
                        valor_centavos,
                        pedidos_distintos
                    )
                    SELECT
                        tempo_sk,
                        cliente_sk,
                        produto_sk,
                        SUM(quantidade),
                        SUM(valor_centavos),
                        COUNT(DISTINCT pedido_numero)
                    FROM fato_vendas_detalhe
                    GROUP BY
                        tempo_sk, cliente_sk, produto_sk
                    """
                )

        os.replace(temporario, destino)

    finally:
        if temporario.exists():
            temporario.unlink()

    return {
        "lote_origem": lote,
        "itens_origem": len(vendas),
        "banco": str(destino),
    }


def indicadores(banco, granularidade="detalhe"):
    """Calcula medidas aditivas sem duplicar os pedidos."""
    tabelas = {
        "detalhe": "fato_vendas_detalhe",
        "resumo": "fato_vendas_resumo",
    }

    if granularidade not in tabelas:
        raise ValueError("Granularidade desconhecida")

    tabela = tabelas[granularidade]

    with closing(conectar(banco)) as conexao:
        linhas, unidades, total = conexao.execute(
            f"""
            SELECT
                COUNT(*),
                COALESCE(SUM(quantidade), 0),
                COALESCE(SUM(valor_centavos), 0)
            FROM {tabela}
            """
        ).fetchone()

    return {
        "granularidade": granularidade,
        "linhas": linhas,
        "unidades": unidades,
        "faturamento_centavos": total,
        "preco_medio_unitario_centavos": (
            round(total / unidades, 2)
            if unidades else None
        ),
    }


def consultar_dimensoes(banco):
    """Mostra a correspondencia entre SK e chave natural."""
    with closing(conectar(banco)) as conexao:
        clientes = conexao.execute(
            """
            SELECT cliente_sk, cliente_id_origem, nome
            FROM dim_clientes
            ORDER BY cliente_sk
            """
        ).fetchall()

        produtos = conexao.execute(
            """
            SELECT produto_sk, produto_id_origem, nome
            FROM dim_produtos
            ORDER BY produto_sk
            """
        ).fetchall()

        datas = conexao.execute(
            """
            SELECT tempo_sk, data_calendario
            FROM dim_tempo
            ORDER BY tempo_sk
            """
        ).fetchall()

    return {
        "clientes": [
            {
                "sk": sk,
                "id_origem": codigo,
                "nome": nome,
            }
            for sk, codigo, nome in clientes
        ],
        "produtos": [
            {
                "sk": sk,
                "id_origem": codigo,
                "nome": nome,
            }
            for sk, codigo, nome in produtos
        ],
        "tempo": [
            {"sk": sk, "data": data}
            for sk, data in datas
        ],
    }


def reconciliar(banco):
    """Compara medidas das duas granularidades."""
    detalhe = indicadores(banco, "detalhe")
    resumo = indicadores(banco, "resumo")

    return {
        "detalhe": detalhe,
        "resumo": resumo,
        "totais_iguais": (
            detalhe["unidades"] == resumo["unidades"]
            and detalhe["faturamento_centavos"]
            == resumo["faturamento_centavos"]
        ),
    }
