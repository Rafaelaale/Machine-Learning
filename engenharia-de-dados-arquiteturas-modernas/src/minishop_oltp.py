"""Aula 01 - OLTP do e-commerce Minishop.

Demonstra transacoes ACID com SQLite.
Valores monetarios sao armazenados em centavos.
"""

import sqlite3
from collections import defaultdict
from pathlib import Path


BASE = Path(__file__).resolve().parent.parent
SCHEMA = BASE / "sql" / "aula01_minishop.sql"


class ErroCompra(Exception):
    """Indica que a compra nao pode ser confirmada."""


class ConexaoGerenciada(sqlite3.Connection):
    """Confirma ou reverte a transacao e fecha a conexao."""

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            return super().__exit__(
                exc_type, exc_value, traceback
            )
        finally:
            self.close()


def conectar(caminho):
    """Abre uma conexao com integridade referencial ativa."""
    conexao = sqlite3.connect(
        str(caminho),
        timeout=10,
        isolation_level=None,
        factory=ConexaoGerenciada,
    )
    conexao.execute("PRAGMA foreign_keys = ON")
    conexao.execute("PRAGMA busy_timeout = 10000")
    return conexao


def criar_banco(caminho):
    """Cria a estrutura e cadastra exemplos da Minishop."""
    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)

    with conectar(caminho) as conexao:
        conexao.executescript(SCHEMA.read_text(encoding="utf-8"))

        conexao.execute(
            "INSERT OR IGNORE INTO clientes VALUES (?, ?, ?)",
            (1, "Ana Silva", "ana@minishop.exemplo"),
        )
        conexao.execute(
            "INSERT OR IGNORE INTO clientes VALUES (?, ?, ?)",
            (2, "Bruno Lima", "bruno@minishop.exemplo"),
        )

        produtos = [
            (1, "Teclado", 15000, 5),
            (2, "Mouse", 8000, 3),
            (3, "Monitor", 90000, 2),
        ]

        for identificador, nome, preco, estoque in produtos:
            conexao.execute(
                """
                INSERT OR IGNORE INTO produtos
                (id, nome, preco_centavos)
                VALUES (?, ?, ?)
                """,
                (identificador, nome, preco),
            )
            conexao.execute(
                """
                INSERT OR IGNORE INTO inventario
                (produto_id, quantidade)
                VALUES (?, ?)
                """,
                (identificador, estoque),
            )


def registrar_compra(
    caminho,
    cliente_id,
    itens,
    pagamento_aprovado=True,
):
    """Executa pedido, itens, estoque e pagamento atomicamente.

    itens: lista de tuplas (produto_id, quantidade).

    BEGIN IMMEDIATE reserva a transacao de escrita.
    Falhas geram ROLLBACK integral.
    """
    if not itens:
        raise ErroCompra("A compra precisa ter itens")

    quantidades = defaultdict(int)

    for produto_id, quantidade in itens:
        if (
            type(produto_id) is not int
            or type(quantidade) is not int
            or quantidade <= 0
        ):
            raise ErroCompra("Produto ou quantidade invalida")
        quantidades[produto_id] += quantidade

    conexao = conectar(caminho)

    try:
        conexao.execute("BEGIN IMMEDIATE")

        cliente = conexao.execute(
            "SELECT id FROM clientes WHERE id = ?",
            (cliente_id,),
        ).fetchone()

        if cliente is None:
            raise ErroCompra("Cliente inexistente")

        pedido_id = conexao.execute(
            """
            INSERT INTO pedidos (cliente_id)
            VALUES (?)
            """,
            (cliente_id,),
        ).lastrowid

        total = 0

        for produto_id, quantidade in quantidades.items():
            produto = conexao.execute(
                """
                SELECT preco_centavos
                FROM produtos
                WHERE id = ?
                """,
                (produto_id,),
            ).fetchone()

            if produto is None:
                raise ErroCompra("Produto inexistente")

            preco = produto[0]

            atualizado = conexao.execute(
                """
                UPDATE inventario
                SET quantidade = quantidade - ?
                WHERE produto_id = ?
                  AND quantidade >= ?
                """,
                (quantidade, produto_id, quantidade),
            )

            if atualizado.rowcount != 1:
                raise ErroCompra("Estoque insuficiente")

            conexao.execute(
                """
                INSERT INTO itens_pedido (
                    pedido_id,
                    produto_id,
                    quantidade,
                    preco_unitario_centavos
                )
                VALUES (?, ?, ?, ?)
                """,
                (pedido_id, produto_id, quantidade, preco),
            )

            total += preco * quantidade

        if not pagamento_aprovado:
            raise ErroCompra("Pagamento recusado")

        conexao.execute(
            """
            INSERT INTO pagamentos (
                pedido_id, valor_centavos, status
            )
            VALUES (?, ?, 'aprovado')
            """,
            (pedido_id, total),
        )

        conexao.execute(
            """
            UPDATE pedidos
            SET total_centavos = ?, status = 'confirmado'
            WHERE id = ?
            """,
            (total, pedido_id),
        )

        conexao.commit()

        return {
            "pedido_id": pedido_id,
            "total_centavos": total,
            "status": "confirmado",
        }

    except Exception:
        conexao.rollback()
        raise

    finally:
        conexao.close()


def consultar_pedido(caminho, pedido_id):
    """Consulta operacional por chave primaria."""
    with conectar(caminho) as conexao:
        return conexao.execute(
            """
            SELECT id, cliente_id, total_centavos, status
            FROM pedidos
            WHERE id = ?
            """,
            (pedido_id,),
        ).fetchone()


def consultar_estoque(caminho, produto_id):
    """Consulta pontual de estoque."""
    with conectar(caminho) as conexao:
        resultado = conexao.execute(
            """
            SELECT quantidade
            FROM inventario
            WHERE produto_id = ?
            """,
            (produto_id,),
        ).fetchone()

    return None if resultado is None else resultado[0]


def contar_registros(caminho):
    """Retorna quantidades das seis tabelas."""
    tabelas = (
        "clientes",
        "produtos",
        "inventario",
        "pedidos",
        "itens_pedido",
        "pagamentos",
    )

    with conectar(caminho) as conexao:
        return {
            tabela: conexao.execute(
                f"SELECT COUNT(*) FROM {tabela}"
            ).fetchone()[0]
            for tabela in tabelas
        }
