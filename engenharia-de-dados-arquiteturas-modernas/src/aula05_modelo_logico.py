"""Modelo logico e operacoes transacionais da Minishop.

Aula 05: PK, FK, UNIQUE e chave primaria composta.
Banco independente das aulas anteriores.
"""

import sqlite3
from contextlib import closing
from pathlib import Path


BASE = Path(__file__).resolve().parent.parent
SCHEMA = BASE / "sql" / "aula05_modelo_logico.sql"


def conectar(caminho):
    """Abre uma conexao com integridade referencial ativa."""
    conexao = sqlite3.connect(
        str(caminho),
        timeout=10,
    )
    conexao.execute("PRAGMA foreign_keys = ON")
    return conexao


def criar_modelo(caminho):
    """Inicializa nova base relacional sem sobrescrever uma existente."""
    caminho = Path(caminho)

    if caminho.exists():
        raise FileExistsError(
            f"Banco existente preservado: {caminho}"
        )

    caminho.parent.mkdir(parents=True, exist_ok=True)

    try:
        with closing(conectar(caminho)) as conexao:
            conexao.executescript(
                SCHEMA.read_text(encoding="utf-8")
            )

            with conexao:
                conexao.execute(
                    """
                    INSERT INTO clientes
                    (cliente_id, nome, email)
                    VALUES (1, 'Ana', 'ana@exemplo.com')
                    """
                )

                conexao.execute(
                    """
                    INSERT INTO categorias
                    (categoria_id, nome)
                    VALUES (1, 'Informatica')
                    """
                )

                conexao.execute(
                    """
                    INSERT INTO produtos
                    (produto_id, categoria_id, nome, preco_centavos)
                    VALUES (1, 1, 'Teclado', 15000)
                    """
                )

                conexao.execute(
                    """
                    INSERT INTO estoque
                    (estoque_id, produto_id, quantidade)
                    VALUES (1, 1, 5)
                    """
                )
    except Exception:
        if caminho.exists():
            caminho.unlink()
        raise


def registrar_venda(caminho, quantidade=2):
    """Registra venda, fatura, pagamento e saida atomicamente."""
    if type(quantidade) is not int or quantidade <= 0:
        raise ValueError("Quantidade deve ser inteiro positivo")

    with closing(conectar(caminho)) as conexao:
        try:
            conexao.execute("BEGIN IMMEDIATE")

            preco = conexao.execute(
                """
                SELECT preco_centavos
                FROM produtos
                WHERE produto_id = 1
                """
            ).fetchone()

            if preco is None:
                raise ValueError("Produto inexistente")

            atualizacao = conexao.execute(
                """
                UPDATE estoque
                SET quantidade = quantidade - ?
                WHERE estoque_id = 1
                  AND produto_id = 1
                  AND quantidade >= ?
                """,
                (quantidade, quantidade),
            )

            if atualizacao.rowcount != 1:
                raise ValueError("Estoque insuficiente")

            valor = preco[0] * quantidade

            pedido_id = conexao.execute(
                """
                INSERT INTO pedidos
                (cliente_id, estado, valor_centavos)
                VALUES (1, 'confirmado', ?)
                """,
                (valor,),
            ).lastrowid

            conexao.execute(
                """
                INSERT INTO itens_pedido
                (pedido_id, produto_id, quantidade,
                 preco_unitario_centavos)
                VALUES (?, 1, ?, ?)
                """,
                (pedido_id, quantidade, preco[0]),
            )

            conexao.execute(
                """
                INSERT INTO movimentos_estoque
                (estoque_id, pedido_id, produto_id,
                 tipo, quantidade)
                VALUES (1, ?, 1, 'saida', ?)
                """,
                (pedido_id, quantidade),
            )

            conexao.execute(
                """
                INSERT INTO faturas
                (pedido_id, valor_centavos, estado)
                VALUES (?, ?, 'emitida')
                """,
                (pedido_id, valor),
            )

            conexao.execute(
                """
                INSERT INTO pagamentos
                (pedido_id, valor_centavos, estado)
                VALUES (?, ?, 'aprovado')
                """,
                (pedido_id, valor),
            )

            conexao.commit()

            return {
                "pedido_id": pedido_id,
                "quantidade": quantidade,
                "valor_centavos": valor,
                "estado": "confirmado",
            }

        except Exception:
            conexao.rollback()
            raise


def estrutura_tabelas(caminho):
    """Consulta tabelas e suas chaves primarias."""
    with closing(conectar(caminho)) as conexao:
        tabelas = [
            linha[0]
            for linha in conexao.execute(
                """
                SELECT name FROM sqlite_master
                WHERE type='table'
                  AND name NOT LIKE 'sqlite_%'
                ORDER BY name
                """
            ).fetchall()
        ]

        return {
            tabela: [
                {
                    "coluna": linha[1],
                    "tipo": linha[2],
                    "pk_ordem": linha[5],
                }
                for linha in conexao.execute(
                    f'PRAGMA table_info("{tabela}")'
                ).fetchall()
            ]
            for tabela in tabelas
        }


def resumo_operacional(caminho):
    """Apresenta indicadores operacionais simples."""
    with closing(conectar(caminho)) as conexao:
        pedidos = conexao.execute(
            "SELECT COUNT(*) FROM pedidos"
        ).fetchone()[0]

        faturas = conexao.execute(
            "SELECT COUNT(*) FROM faturas"
        ).fetchone()[0]

        movimentos = conexao.execute(
            "SELECT COUNT(*) FROM movimentos_estoque"
        ).fetchone()[0]

        estoque = conexao.execute(
            """
            SELECT quantidade FROM estoque
            WHERE produto_id = 1
            """
        ).fetchone()[0]

    return {
        "pedidos": pedidos,
        "faturas": faturas,
        "movimentos": movimentos,
        "estoque_teclado": estoque,
    }
