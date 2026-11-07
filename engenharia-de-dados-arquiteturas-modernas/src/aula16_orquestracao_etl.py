"""Aula 16 - Orquestracao ETL Minishop.

Extracao consistente em leitura, dimensoes primeiro,
fatos depois, reprocessamento de periodo completo,
auditoria e rollback.

Reutiliza a estrutura e os lookups da Aula 15.
"""

import sqlite3
from contextlib import closing
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from src.aula15_arquitetura_etl import (
    criar_dw,
    conectar,
    lookup_categoria,
    lookup_produto,
    lookup_cliente_historico,
    registrar_tempo,
    INICIO_HISTORICO,
)


BASE = Path(__file__).resolve().parent.parent
SCHEMA = BASE / "sql" / "aula16_orquestracao_etl.sql"


def validar_periodo(inicio, fim):
    try:
        di = date.fromisoformat(inicio)
        df = date.fromisoformat(fim)
    except (ValueError, TypeError) as erro:
        raise ValueError("Datas invalidas") from erro

    if di.isoformat() != inicio or df.isoformat() != fim:
        raise ValueError("Use datas YYYY-MM-DD")

    if di > df:
        raise ValueError("Data inicial posterior a final")

    return di, df


def ultimos_30_dias(referencia=None):
    """Janela inclusiva de 30 datas, incluindo a referencia."""
    hoje = referencia or date.today()

    if not isinstance(hoje, date):
        raise ValueError("Referencia deve ser uma data")

    return (
        (hoje - timedelta(days=29)).isoformat(),
        hoje.isoformat(),
    )


def preparar_dw(banco):
    criar_dw(banco)

    with closing(conectar(banco)) as con:
        con.executescript(
            SCHEMA.read_text(encoding="utf-8")
        )


def extrair(banco, inicio, fim):
    """Snapshot do OLTP. Nao modifica a origem."""
    validar_periodo(inicio, fim)

    origem = Path(banco).resolve()

    if not origem.is_file():
        raise FileNotFoundError(origem)

    with closing(
        sqlite3.connect(
            origem.as_uri() + "?mode=ro",
            uri=True,
        )
    ) as con:
        con.row_factory = sqlite3.Row
        con.execute("BEGIN")

        clientes = con.execute(
            """
            SELECT cliente_id, nome
            FROM clientes
            ORDER BY cliente_id
            """
        ).fetchall()

        produtos = con.execute(
            """
            SELECT
                p.produto_id, p.nome AS produto_nome,
                c.categoria_id, c.nome AS categoria_nome
            FROM produtos p
            JOIN categorias c
              ON c.categoria_id = p.categoria_id
            ORDER BY p.produto_id
            """
        ).fetchall()

        vendas = con.execute(
            """
            SELECT
                pe.pedido_id, pe.cliente_id,
                it.produto_id,
                substr(pe.data_pedido, 1, 10) AS data,
                it.quantidade,
                it.preco_unitario_centavos,
                it.quantidade * it.preco_unitario_centavos
                    AS valor_total_centavos
            FROM pedidos pe
            JOIN itens_pedido it
              ON it.pedido_id = pe.pedido_id
            JOIN pagamentos pg
              ON pg.pedido_id = pe.pedido_id
            WHERE pe.estado = 'confirmado'
              AND pg.estado = 'aprovado'
              AND substr(pe.data_pedido, 1, 10)
                  BETWEEN ? AND ?
            ORDER BY pe.pedido_id, it.produto_id
            """,
            (inicio, fim),
        ).fetchall()

        # O OLTP da Aula 05 nao registra data independente
        # para movimento de estoque. Usamos a data do pedido
        # e registramos essa limitacao na documentacao.
        movimentos = con.execute(
            """
            SELECT
                m.movimento_id, m.produto_id,
                substr(pe.data_pedido, 1, 10) AS data,
                m.quantidade
            FROM movimentos_estoque m
            JOIN pedidos pe
              ON pe.pedido_id = m.pedido_id
            JOIN pagamentos pg
              ON pg.pedido_id = pe.pedido_id
            WHERE m.tipo = 'saida'
              AND pe.estado = 'confirmado'
              AND pg.estado = 'aprovado'
              AND substr(pe.data_pedido, 1, 10)
                  BETWEEN ? AND ?
            ORDER BY m.movimento_id
            """,
            (inicio, fim),
        ).fetchall()

        con.commit()

    return {
        "clientes": [dict(r) for r in clientes],
        "produtos": [dict(r) for r in produtos],
        "vendas": [dict(r) for r in vendas],
        "movimentos": [dict(r) for r in movimentos],
    }


def validar_extracao(dados):
    """Impede medidas invalidas antes do DELETE do periodo."""
    chaves_venda = set()
    chaves_movimento = set()

    for v in dados["vendas"]:
        if (
            type(v["quantidade"]) is not int
            or v["quantidade"] <= 0
            or type(v["preco_unitario_centavos"]) is not int
            or v["preco_unitario_centavos"] < 0
            or v["valor_total_centavos"] != (
                v["quantidade"] * v["preco_unitario_centavos"]
            )
        ):
            raise ValueError("Venda inconsistente")

        chave = (v["pedido_id"], v["produto_id"])

        if chave in chaves_venda:
            raise ValueError("Venda duplicada")

        chaves_venda.add(chave)

    for m in dados["movimentos"]:
        if (
            type(m["quantidade"]) is not int
            or m["quantidade"] <= 0
        ):
            raise ValueError("Movimento invalido")

        if m["movimento_id"] in chaves_movimento:
            raise ValueError("Movimento duplicado")

        chaves_movimento.add(m["movimento_id"])


def lookup_sk(con, tabela, natural, codigo):
    permitidas = {
        "dim_produto": ("produto_sk", "cod_produto"),
        "dim_cliente": ("cliente_sk", "cod_cliente"),
    }

    if tabela not in permitidas:
        raise ValueError("Lookup nao autorizado")

    sk, campo = permitidas[tabela]

    linha = con.execute(
        f"""
        SELECT {sk}
        FROM {tabela}
        WHERE {campo} = ?
        """,
        (str(codigo),),
    ).fetchone()

    if linha is None:
        raise ValueError(
            f"Dimensao nao encontrada: {tabela}/{codigo}"
        )

    return linha[0]


def lookup_cliente_na_data(con, codigo, data_evento):
    """Lookup SCD2 dentro da mesma transacao da carga."""
    linhas = con.execute(
        """
        SELECT cliente_sk
        FROM dim_cliente
        WHERE cod_cliente = ?
          AND valid_from <= ?
          AND (valid_to IS NULL OR ? < valid_to)
        """,
        (str(codigo), data_evento, data_evento),
    ).fetchall()

    if len(linhas) != 1:
        raise ValueError(
            "Cliente sem versao SCD2 unica na data do fato"
        )

    return linhas[0][0]


def carregar_dimensoes(con, dados, inicio, fim):
    """Carga ordenada: categoria antes de produto."""
    for c in dados["clientes"]:
        codigo = str(c["cliente_id"])

        atual = con.execute(
            """
            SELECT cliente_sk, nome_cliente
            FROM dim_cliente
            WHERE cod_cliente = ?
              AND valid_to IS NULL
            """,
            (codigo,),
        ).fetchone()

        if atual is None:
            con.execute(
                """
                INSERT INTO dim_cliente
                (cod_cliente, nome_cliente, valid_from, valid_to)
                VALUES (?, ?, ?, NULL)
                """,
                (codigo, c["nome"], INICIO_HISTORICO),
            )
        elif atual[1] != c["nome"]:
            # Nome: correcao Tipo 1 apenas da versao atual.
            # Campos geograficos nao existem no OLTP atual.
            con.execute(
                """
                UPDATE dim_cliente
                SET nome_cliente = ?
                WHERE cliente_sk = ?
                """,
                (c["nome"], atual[0]),
            )

    for p in dados["produtos"]:
        categoria_sk = lookup_categoria(
            con,
            str(p["categoria_id"]),
            p["categoria_nome"],
        )

        lookup_produto(
            con,
            str(p["produto_id"]),
            p["produto_nome"],
            categoria_sk,
        )

    # Dois membros fixos, mas sem associar uma promocao
    # aos pedidos que nao informam esse atributo.
    for codigo, descricao in (
        ("TRUE", "Em promocao"),
        ("FALSE", "Sem promocao"),
    ):
        con.execute(
            """
            INSERT INTO dim_promocao
            (cod_promocao, descricao)
            VALUES (?, ?)
            ON CONFLICT(cod_promocao)
            DO UPDATE SET descricao = excluded.descricao
            """,
            (codigo, descricao),
        )

    # Canal de venda e ausente no modelo OLTP atual.
    # Portanto a dimensao Acesso nao recebe valores inventados.

    for situacao in ("a_vencer", "vencido"):
        for primeiro, ultimo, faixa in (
            (0, 15, "0-15"),
            (16, 30, "16-30"),
            (31, 60, "31-60"),
            (61, None, "61+"),
        ):
            con.execute(
                """
                INSERT OR IGNORE INTO dim_aging
                (situacao, faixa, inicio_dias, fim_dias)
                VALUES (?, ?, ?, ?)
                """,
                (situacao, faixa, primeiro, ultimo),
            )

    di, df = validar_periodo(inicio, fim)
    atual = di

    while atual <= df:
        registrar_tempo(con, atual.isoformat())
        atual += timedelta(days=1)


def carregar_fatos(con, dados, inicio, fim):
    """Substitui as fotografias completas do intervalo."""
    sk_inicio = int(inicio.replace("-", ""))
    sk_fim = int(fim.replace("-", ""))

    for tabela in ("fato_vendas", "fato_inventario"):
        con.execute(
            f"""
            DELETE FROM {tabela}
            WHERE tempo_sk BETWEEN ? AND ?
            """,
            (sk_inicio, sk_fim),
        )

    for venda in dados["vendas"]:
        cliente_sk = lookup_cliente_na_data(
            con, venda["cliente_id"], venda["data"]
        )

        produto_sk = lookup_sk(
            con,
            "dim_produto",
            "cod_produto",
            venda["produto_id"],
        )

        tempo_sk = int(venda["data"].replace("-", ""))

        con.execute(
            """
            INSERT INTO fato_vendas
            (pedido_id_origem, produto_id_origem,
             cliente_sk, produto_sk, tempo_sk,
             promocao_sk, acesso_sk,
             quantidade, preco_unitario_centavos,
             valor_total_centavos)
            VALUES (?, ?, ?, ?, ?, NULL, NULL, ?, ?, ?)
            """,
            (
                venda["pedido_id"],
                venda["produto_id"],
                cliente_sk,
                produto_sk,
                tempo_sk,
                venda["quantidade"],
                venda["preco_unitario_centavos"],
                venda["valor_total_centavos"],
            ),
        )

    for movimento in dados["movimentos"]:
        produto_sk = lookup_sk(
            con,
            "dim_produto",
            "cod_produto",
            movimento["produto_id"],
        )

        tempo_sk = int(movimento["data"].replace("-", ""))

        con.execute(
            """
            INSERT INTO fato_inventario
            (movimento_id_origem, produto_sk,
             tempo_sk, saida_estoque)
            VALUES (?, ?, ?, ?)
            """,
            (
                movimento["movimento_id"],
                produto_sk,
                tempo_sk,
                -movimento["quantidade"],
            ),
        )

    return {
        "vendas": len(dados["vendas"]),
        "inventario": len(dados["movimentos"]),
        "faturamento_centavos": sum(
            v["valor_total_centavos"]
            for v in dados["vendas"]
        ),
        "saida_estoque": -sum(
            m["quantidade"]
            for m in dados["movimentos"]
        ),
    }


def executar_etl(origem, destino, inicio, fim):
    """Orquestra uma carga unica e transacional no DW."""
    validar_periodo(inicio, fim)

    if Path(origem).resolve() == Path(destino).resolve():
        raise ValueError("OLTP e DW devem ser distintos")

    dados = extrair(origem, inicio, fim)
    validar_extracao(dados)

    preparar_dw(destino)

    with closing(conectar(destino)) as con:
        try:
            con.execute("BEGIN IMMEDIATE")

            carregar_dimensoes(
                con, dados, inicio, fim
            )

            resultado = carregar_fatos(
                con, dados, inicio, fim
            )

            # A fonte atual nao tem vencimento e saldo
            # aberto para construir o fato financeiro.
            # Nao apagar fatos financeiros preexistentes.

            con.execute(
                """
                INSERT INTO etl_execucoes
                (inicio, fim, executado_em,
                 vendas_carregadas, movimentos_carregados,
                 faturamento_centavos)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    inicio,
                    fim,
                    datetime.now(timezone.utc).isoformat(),
                    resultado["vendas"],
                    resultado["inventario"],
                    resultado["faturamento_centavos"],
                ),
            )

            con.commit()

        except Exception:
            con.rollback()
            raise

    return {
        "periodo": {
            "inicio": inicio,
            "fim": fim,
        },
        "extracao": {
            chave: len(valor)
            for chave, valor in dados.items()
        },
        "fatos": resultado,
        "financeiro": "nao carregado: dados insuficientes",
    }


def indicadores(banco):
    with closing(conectar(banco)) as con:
        vendas = con.execute(
            """
            SELECT COUNT(*),
                   COALESCE(SUM(quantidade), 0),
                   COALESCE(SUM(valor_total_centavos), 0)
            FROM fato_vendas
            """
        ).fetchone()

        inventario = con.execute(
            """
            SELECT COUNT(*),
                   COALESCE(SUM(saida_estoque), 0)
            FROM fato_inventario
            """
        ).fetchone()

        financeiro = con.execute(
            "SELECT COUNT(*) FROM fato_financeiro"
        ).fetchone()[0]

        cargas = con.execute(
            "SELECT COUNT(*) FROM etl_execucoes"
        ).fetchone()[0]

        dias = con.execute(
            "SELECT COUNT(*) FROM dim_tempo"
        ).fetchone()[0]

    return {
        "linhas_vendas": vendas[0],
        "unidades": vendas[1],
        "faturamento_centavos": vendas[2],
        "linhas_inventario": inventario[0],
        "saida_estoque": inventario[1],
        "linhas_financeiro": financeiro,
        "dias_dimensao_tempo": dias,
        "execucoes": cargas,
    }
