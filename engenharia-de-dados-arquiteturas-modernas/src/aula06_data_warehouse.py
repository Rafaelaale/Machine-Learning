"""Aula 06 - Prototipo historico de Data Warehouse Minishop.

Fonte: OLTP da Aula 05.
Destino: banco SQLite separado.

Cada lote representa uma fotografia completa de vendas.
Consultas atuais usam somente o ultimo lote.
Lotes anteriores sao preservados.
"""

import hashlib
import json
import sqlite3
from contextlib import closing
from datetime import date
from pathlib import Path


BASE = Path(__file__).resolve().parent.parent
SCHEMA = BASE / "sql" / "aula06_data_warehouse.sql"


def conectar_dw(caminho):
    """Abre uma conexao SQLite com integridade referencial."""
    conexao = sqlite3.connect(str(caminho), timeout=10)
    conexao.execute("PRAGMA foreign_keys = ON")
    return conexao


def extrair_vendas(banco_oltp):
    """Extrai vendas confirmadas e pagas em modo somente leitura."""
    origem = Path(banco_oltp).resolve()

    if not origem.is_file():
        raise FileNotFoundError(origem)

    uri = origem.as_uri() + "?mode=ro"

    with closing(sqlite3.connect(uri, uri=True)) as conexao:
        conexao.row_factory = sqlite3.Row

        with conexao:
            registros = conexao.execute(
                """
                SELECT
                    p.pedido_id,
                    p.cliente_id,
                    c.nome AS cliente_nome,
                    i.produto_id,
                    pr.nome AS produto_nome,
                    ca.nome AS categoria,
                    substr(p.data_pedido, 1, 10) AS data,
                    i.quantidade,
                    i.quantidade * i.preco_unitario_centavos
                        AS valor_centavos
                FROM pedidos AS p
                JOIN clientes AS c
                    ON c.cliente_id = p.cliente_id
                JOIN itens_pedido AS i
                    ON i.pedido_id = p.pedido_id
                JOIN produtos AS pr
                    ON pr.produto_id = i.produto_id
                JOIN categorias AS ca
                    ON ca.categoria_id = pr.categoria_id
                JOIN pagamentos AS pg
                    ON pg.pedido_id = p.pedido_id
                WHERE p.estado = 'confirmado'
                  AND pg.estado = 'aprovado'
                ORDER BY p.pedido_id, i.produto_id
                """
            ).fetchall()

    return [dict(registro) for registro in registros]


def validar_vendas(vendas):
    """Valida os registros antes de iniciar a carga."""
    chaves = set()

    for venda in vendas:
        chave = (venda["pedido_id"], venda["produto_id"])

        if chave in chaves:
            raise ValueError("Item de venda duplicado")

        chaves.add(chave)

        if venda["quantidade"] <= 0:
            raise ValueError("Quantidade de venda invalida")

        if venda["valor_centavos"] < 0:
            raise ValueError("Valor de venda negativo")

        if not venda["cliente_nome"] or not venda["produto_nome"]:
            raise ValueError("Dimensao incompleta")

        if not venda["categoria"]:
            raise ValueError("Categoria ausente")

        try:
            date.fromisoformat(venda["data"])
        except (TypeError, ValueError) as erro:
            raise ValueError("Data invalida") from erro


def assinatura_dados(vendas):
    """Calcula uma assinatura reproduzivel dos dados extraidos."""
    conteudo = json.dumps(
        vendas,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
    )

    return hashlib.sha256(
        conteudo.encode("utf-8")
    ).hexdigest()


def carregar_dw(banco_oltp, banco_dw):
    """Carrega nova fotografia sem remover lotes anteriores.

    Se a origem nao mudou, reutiliza o lote existente.
    """
    origem = Path(banco_oltp).resolve()
    destino = Path(banco_dw).resolve()

    if origem == destino:
        raise ValueError("Origem e destino devem ser diferentes")

    vendas = extrair_vendas(origem)
    validar_vendas(vendas)

    assinatura = assinatura_dados(vendas)
    destino.parent.mkdir(parents=True, exist_ok=True)

    with closing(conectar_dw(destino)) as conexao:
        conexao.executescript(SCHEMA.read_text(encoding="utf-8"))

        with conexao:
            existente = conexao.execute(
                """
                SELECT lote_id
                FROM lotes_carga
                WHERE assinatura = ?
                """,
                (assinatura,),
            ).fetchone()

            if existente is not None:
                return {
                    "lote_id": existente[0],
                    "linhas": len(vendas),
                    "nova_carga": False,
                }

            total = sum(
                venda["valor_centavos"]
                for venda in vendas
            )

            lote_id = conexao.execute(
                """
                INSERT INTO lotes_carga
                    (assinatura, quantidade_linhas, total_centavos)
                VALUES (?, ?, ?)
                """,
                (assinatura, len(vendas), total),
            ).lastrowid

            for venda in vendas:
                data = date.fromisoformat(venda["data"])

                conexao.execute(
                    """
                    INSERT OR IGNORE INTO dim_clientes
                        (lote_id, cliente_id, nome)
                    VALUES (?, ?, ?)
                    """,
                    (
                        lote_id,
                        venda["cliente_id"],
                        venda["cliente_nome"],
                    ),
                )

                conexao.execute(
                    """
                    INSERT OR IGNORE INTO dim_produtos
                        (lote_id, produto_id, nome, categoria)
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        lote_id,
                        venda["produto_id"],
                        venda["produto_nome"],
                        venda["categoria"],
                    ),
                )

                conexao.execute(
                    """
                    INSERT OR IGNORE INTO dim_tempo
                        (data, ano, mes, dia)
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        data.isoformat(),
                        data.year,
                        data.month,
                        data.day,
                    ),
                )

                conexao.execute(
                    """
                    INSERT INTO fato_vendas (
                        lote_id, pedido_id, produto_id,
                        cliente_id, data,
                        quantidade, valor_centavos
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        lote_id,
                        venda["pedido_id"],
                        venda["produto_id"],
                        venda["cliente_id"],
                        venda["data"],
                        venda["quantidade"],
                        venda["valor_centavos"],
                    ),
                )

    return {
        "lote_id": lote_id,
        "linhas": len(vendas),
        "nova_carga": True,
    }


def ultimo_lote(conexao):
    """Retorna o ultimo lote carregado."""
    resultado = conexao.execute(
        "SELECT MAX(lote_id) FROM lotes_carga"
    ).fetchone()

    return resultado[0]


def indicadores_dw(banco_dw, lote_id=None):
    """Calcula indicadores de uma fotografia especifica."""
    if not Path(banco_dw).is_file():
        raise FileNotFoundError(banco_dw)

    with closing(conectar_dw(banco_dw)) as conexao:
        if lote_id is None:
            lote_id = ultimo_lote(conexao)

        if lote_id is None:
            return {
                "lote_id": None,
                "pedidos": 0,
                "faturamento_centavos": 0,
                "unidades": 0,
                "ticket_medio_centavos": 0,
            }

        existe = conexao.execute(
            "SELECT 1 FROM lotes_carga WHERE lote_id = ?",
            (lote_id,),
        ).fetchone()

        if existe is None:
            raise ValueError("Lote inexistente")

        faturamento, pedidos, unidades = conexao.execute(
            """
            SELECT
                COALESCE(SUM(valor_centavos), 0),
                COUNT(DISTINCT pedido_id),
                COALESCE(SUM(quantidade), 0)
            FROM fato_vendas
            WHERE lote_id = ?
            """,
            (lote_id,),
        ).fetchone()

    return {
        "lote_id": lote_id,
        "pedidos": pedidos,
        "faturamento_centavos": faturamento,
        "unidades": unidades,
        "ticket_medio_centavos": (
            round(faturamento / pedidos)
            if pedidos else 0
        ),
    }


def faturamento_por_categoria(banco_dw, lote_id=None):
    """Consulta a receita por categoria do lote selecionado."""
    with closing(conectar_dw(banco_dw)) as conexao:
        if lote_id is None:
            lote_id = ultimo_lote(conexao)

        if lote_id is None:
            return []

        registros = conexao.execute(
            """
            SELECT
                p.categoria,
                SUM(f.valor_centavos),
                SUM(f.quantidade)
            FROM fato_vendas AS f
            JOIN dim_produtos AS p
                ON p.lote_id = f.lote_id
               AND p.produto_id = f.produto_id
            WHERE f.lote_id = ?
            GROUP BY p.categoria
            ORDER BY SUM(f.valor_centavos) DESC
            """,
            (lote_id,),
        ).fetchall()

    return [
        {
            "categoria": categoria,
            "faturamento_centavos": valor,
            "unidades": quantidade,
        }
        for categoria, valor, quantidade in registros
    ]


def faturamento_mensal(banco_dw, lote_id=None):
    """Consulta a receita por mes do lote selecionado."""
    with closing(conectar_dw(banco_dw)) as conexao:
        if lote_id is None:
            lote_id = ultimo_lote(conexao)

        if lote_id is None:
            return []

        registros = conexao.execute(
            """
            SELECT
                t.ano,
                t.mes,
                SUM(f.valor_centavos)
            FROM fato_vendas AS f
            JOIN dim_tempo AS t
                ON t.data = f.data
            WHERE f.lote_id = ?
            GROUP BY t.ano, t.mes
            ORDER BY t.ano, t.mes
            """,
            (lote_id,),
        ).fetchall()

    return [
        {
            "ano": ano,
            "mes": mes,
            "faturamento_centavos": valor,
        }
        for ano, mes, valor in registros
    ]


def historico_cargas(banco_dw):
    """Lista todos os lotes historicos sem os modificar."""
    with closing(conectar_dw(banco_dw)) as conexao:
        registros = conexao.execute(
            """
            SELECT lote_id, carregado_em,
                   quantidade_linhas, total_centavos
            FROM lotes_carga
            ORDER BY lote_id
            """
        ).fetchall()

    return [
        {
            "lote_id": lote,
            "carregado_em": data,
            "linhas": linhas,
            "total_centavos": total,
        }
        for lote, data, linhas, total in registros
    ]
