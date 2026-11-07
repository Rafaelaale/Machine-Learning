"""Aula 10 - Data Warehouse dimensional da Minishop.

Cliente: estrela.
Produto/Categoria: snowflake.
Fatos: vendas, inventario e financeiro.

Apenas medidas comprovadas na origem sao carregadas.
"""

import json
import os
import sqlite3
import tempfile
from collections import defaultdict
from contextlib import closing
from datetime import date
from pathlib import Path


BASE = Path(__file__).resolve().parent.parent
SCHEMA = BASE / "sql" / "aula10_dw_minishop.sql"


def conectar(banco):
    conexao = sqlite3.connect(str(banco), timeout=10)
    conexao.execute("PRAGMA foreign_keys = ON")
    return conexao


def extrair_oltp(banco):
    """Le vendas e movimentos reais sem alterar o OLTP."""
    banco = Path(banco).resolve()

    if not banco.is_file():
        raise FileNotFoundError(banco)

    with closing(
        sqlite3.connect(banco.as_uri() + "?mode=ro", uri=True)
    ) as conexao:
        conexao.row_factory = sqlite3.Row
        conexao.execute("BEGIN")

        vendas = conexao.execute(
            """
            SELECT
                pe.pedido_id,
                pe.cliente_id,
                cl.nome AS cliente_nome,
                it.produto_id,
                pr.nome AS produto_nome,
                ca.categoria_id,
                ca.nome AS categoria_nome,
                substr(pe.data_pedido, 1, 10) AS data,
                it.quantidade,
                it.quantidade * it.preco_unitario_centavos
                    AS valor_centavos
            FROM pedidos pe
            JOIN clientes cl ON cl.cliente_id = pe.cliente_id
            JOIN itens_pedido it ON it.pedido_id = pe.pedido_id
            JOIN produtos pr ON pr.produto_id = it.produto_id
            JOIN categorias ca
              ON ca.categoria_id = pr.categoria_id
            JOIN pagamentos pg ON pg.pedido_id = pe.pedido_id
            WHERE pe.estado = 'confirmado'
              AND pg.estado = 'aprovado'
            ORDER BY pe.pedido_id, it.produto_id
            """
        ).fetchall()

        movimentos = conexao.execute(
            """
            SELECT
                m.movimento_id,
                m.pedido_id,
                m.produto_id,
                pr.nome AS produto_nome,
                ca.categoria_id,
                ca.nome AS categoria_nome,
                substr(pe.data_pedido, 1, 10) AS data,
                m.quantidade,
                m.tipo
            FROM movimentos_estoque m
            JOIN pedidos pe ON pe.pedido_id = m.pedido_id
            JOIN pagamentos pg ON pg.pedido_id = pe.pedido_id
            JOIN produtos pr ON pr.produto_id = m.produto_id
            JOIN categorias ca
              ON ca.categoria_id = pr.categoria_id
            WHERE m.tipo = 'saida'
              AND pe.estado = 'confirmado'
              AND pg.estado = 'aprovado'
            ORDER BY m.movimento_id
            """
        ).fetchall()

        conexao.commit()

    return {
        "vendas": [dict(r) for r in vendas],
        "movimentos": [dict(r) for r in movimentos],
    }


def carregar_dw(banco_oltp, banco_dw):
    """Cria uma fotografia fisica independente do OLTP."""
    origem = Path(banco_oltp).resolve()
    destino = Path(banco_dw).resolve()

    if origem == destino:
        raise ValueError("Origem e destino iguais")

    if destino.suffix.lower() != ".db":
        raise ValueError("Destino deve possuir extensao .db")

    dados = extrair_oltp(origem)
    vendas = dados["vendas"]
    movimentos = dados["movimentos"]

    clientes = {}
    categorias = {}
    produtos = {}
    datas = set()

    for v in vendas:
        if v["quantidade"] <= 0 or v["valor_centavos"] < 0:
            raise ValueError("Venda invalida na origem")

        clientes[v["cliente_id"]] = v["cliente_nome"]
        categorias[v["categoria_id"]] = v["categoria_nome"]

        produtos[v["produto_id"]] = (
            v["produto_nome"],
            v["categoria_id"],
        )

        datas.add(v["data"])

    for m in movimentos:
        if m["quantidade"] <= 0:
            raise ValueError("Movimento invalido na origem")

        categorias[m["categoria_id"]] = m["categoria_nome"]
        produtos[m["produto_id"]] = (
            m["produto_nome"],
            m["categoria_id"],
        )
        datas.add(m["data"])

    destino.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile(
        prefix="aula10_",
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
                sk_cliente = {
                    codigo: sk
                    for sk, codigo in enumerate(
                        sorted(clientes), start=1
                    )
                }

                sk_categoria = {
                    codigo: sk
                    for sk, codigo in enumerate(
                        sorted(categorias), start=1
                    )
                }

                sk_produto = {
                    codigo: sk
                    for sk, codigo in enumerate(
                        sorted(produtos), start=1
                    )
                }

                sk_tempo = {
                    valor: sk
                    for sk, valor in enumerate(
                        sorted(datas), start=1
                    )
                }

                for codigo, sk in sk_cliente.items():
                    conexao.execute(
                        """
                        INSERT INTO dim_cliente
                        (cliente_sk, cliente_id_origem, nome)
                        VALUES (?, ?, ?)
                        """,
                        (sk, codigo, clientes[codigo]),
                    )

                for codigo, sk in sk_categoria.items():
                    conexao.execute(
                        """
                        INSERT INTO dim_categoria
                        VALUES (?, ?, ?)
                        """,
                        (sk, codigo, categorias[codigo]),
                    )

                for codigo, sk in sk_produto.items():
                    nome, categoria_id = produtos[codigo]

                    conexao.execute(
                        """
                        INSERT INTO dim_produto
                        VALUES (?, ?, ?, ?)
                        """,
                        (
                            sk,
                            codigo,
                            nome,
                            sk_categoria[categoria_id],
                        ),
                    )

                for valor, sk in sk_tempo.items():
                    d = date.fromisoformat(valor)

                    conexao.execute(
                        """
                        INSERT INTO dim_tempo
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            sk,
                            valor,
                            d.year,
                            d.month,
                            (d.month - 1) // 3 + 1,
                            (d.month - 1) // 6 + 1,
                            d.day,
                        ),
                    )

                # Faixas de classificacao, sem valores financeiros.
                faixas = [
                    (0, 15, "0-15"),
                    (16, 30, "16-30"),
                    (31, 60, "31-60"),
                    (61, None, "61+"),
                ]

                sk = 1

                for situacao in ("a_vencer", "vencido"):
                    for inicio, fim, nome in faixas:
                        conexao.execute(
                            """
                            INSERT INTO dim_aging
                            VALUES (?, ?, ?, ?, ?)
                            """,
                            (sk, situacao, nome, inicio, fim),
                        )
                        sk += 1

                for v in vendas:
                    preco_medio = (
                        v["valor_centavos"] / v["quantidade"]
                    )

                    conexao.execute(
                        """
                        INSERT INTO fato_vendas
                        VALUES (?, ?, ?, ?, NULL, NULL, ?, ?, ?)
                        """,
                        (
                            v["pedido_id"],
                            sk_cliente[v["cliente_id"]],
                            sk_produto[v["produto_id"]],
                            sk_tempo[v["data"]],
                            v["quantidade"],
                            preco_medio,
                            v["valor_centavos"],
                        ),
                    )

                # Agregacao: saidas reais por produto e dia.
                agregados = defaultdict(int)

                for m in movimentos:
                    chave = (
                        sk_produto[m["produto_id"]],
                        sk_tempo[m["data"]],
                    )

                    agregados[chave] -= m["quantidade"]

                for (produto_sk, tempo_sk), quantidade in sorted(
                    agregados.items()
                ):
                    conexao.execute(
                        """
                        INSERT INTO fato_inventario
                        VALUES (?, ?, ?)
                        """,
                        (produto_sk, tempo_sk, quantidade),
                    )

                # O fato financeiro permanece vazio.
                # Nao ha vencimento ou saldo em aberto na origem.

        os.replace(temporario, destino)

    finally:
        if temporario.exists():
            temporario.unlink()

    return {
        "vendas_importadas": len(vendas),
        "movimentos_importados": len(movimentos),
        "linhas_inventario": len(agregados),
        "linhas_financeiras": 0,
        "destino": str(destino),
    }


def contagens(banco):
    """Conta registros das tres tabelas de fatos."""
    with closing(conectar(banco)) as conexao:
        resultado = {}

        for tabela in (
            "fato_vendas",
            "fato_inventario",
            "fato_financeiro",
        ):
            resultado[tabela] = conexao.execute(
                f"SELECT COUNT(*) FROM {tabela}"
            ).fetchone()[0]

    return resultado


def indicadores(banco):
    """Consulta indicadores analiticos conhecidos."""
    with closing(conectar(banco)) as conexao:
        pedidos, unidades, receita = conexao.execute(
            """
            SELECT
                COUNT(DISTINCT pedido_numero),
                COALESCE(SUM(quantidade), 0),
                COALESCE(SUM(valor_total_centavos), 0)
            FROM fato_vendas
            """
        ).fetchone()

        saidas = conexao.execute(
            """
            SELECT COALESCE(SUM(saida_estoque), 0)
            FROM fato_inventario
            """
        ).fetchone()[0]

        categorias = conexao.execute(
            """
            SELECT
                c.nome,
                SUM(f.valor_total_centavos)
            FROM fato_vendas f
            JOIN dim_produto p
              ON p.produto_sk = f.produto_sk
            JOIN dim_categoria c
              ON c.categoria_sk = p.categoria_sk
            GROUP BY c.nome
            ORDER BY c.nome
            """
        ).fetchall()

        financeiras = conexao.execute(
            "SELECT COUNT(*) FROM fato_financeiro"
        ).fetchone()[0]

    return {
        "pedidos": pedidos,
        "unidades_vendidas": unidades,
        "faturamento_centavos": receita,
        "preco_medio_centavos": (
            round(receita / unidades, 2)
            if unidades else None
        ),
        "saida_estoque": saidas,
        "faturamento_por_categoria": [
            {"categoria": nome, "valor_centavos": valor}
            for nome, valor in categorias
        ],
        "financeiro_disponivel": financeiras > 0,
        "valor_receber_centavos": None,
        "valor_atraso_centavos": None,
    }


def validar_reconciliacao(banco_oltp, banco_dw):
    """Compara faturamento e saidas com os registros de origem."""
    origem = extrair_oltp(banco_oltp)
    metricas = indicadores(banco_dw)

    faturamento_origem = sum(
        v["valor_centavos"]
        for v in origem["vendas"]
    )

    saidas_origem = -sum(
        m["quantidade"]
        for m in origem["movimentos"]
    )

    return {
        "faturamento_reconciliado": (
            faturamento_origem
            == metricas["faturamento_centavos"]
        ),
        "estoque_reconciliado": (
            saidas_origem == metricas["saida_estoque"]
        ),
        "faturamento_origem_centavos": faturamento_origem,
        "saida_origem": saidas_origem,
    }
