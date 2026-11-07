"""Testes automatizados do OLTP da Minishop."""

import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path


BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from src.minishop_oltp import (
    ErroCompra,
    conectar,
    contar_registros,
    consultar_estoque,
    consultar_pedido,
    criar_banco,
    registrar_compra,
)


class TestMinishopOLTP(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.banco = Path(self.temp.name) / "teste.db"
        criar_banco(self.banco)

    def tearDown(self):
        self.temp.cleanup()

    def test_01_seis_tabelas(self):
        self.assertEqual(
            len(contar_registros(self.banco)), 6
        )

    def test_02_dados_iniciais(self):
        registros = contar_registros(self.banco)
        self.assertEqual(registros["clientes"], 2)
        self.assertEqual(registros["produtos"], 3)

    def test_03_compra_confirmada(self):
        compra = registrar_compra(
            self.banco, 1, [(1, 1)]
        )
        self.assertEqual(compra["status"], "confirmado")

    def test_04_calculo_total(self):
        compra = registrar_compra(
            self.banco, 1, [(1, 1), (2, 2)]
        )
        self.assertEqual(
            compra["total_centavos"], 31000
        )

    def test_05_baixa_estoque(self):
        registrar_compra(self.banco, 1, [(1, 2)])
        self.assertEqual(
            consultar_estoque(self.banco, 1), 3
        )

    def test_06_pagamento_rollback(self):
        with self.assertRaises(ErroCompra):
            registrar_compra(
                self.banco, 1, [(1, 2)],
                pagamento_aprovado=False,
            )

        self.assertEqual(
            consultar_estoque(self.banco, 1), 5
        )
        self.assertEqual(
            contar_registros(self.banco)["pedidos"], 0
        )
        self.assertEqual(
            contar_registros(self.banco)["pagamentos"], 0
        )

    def test_07_estoque_insuficiente(self):
        with self.assertRaises(ErroCompra):
            registrar_compra(
                self.banco, 1, [(3, 99)]
            )

        self.assertEqual(
            consultar_estoque(self.banco, 3), 2
        )

    def test_08_cliente_inexistente(self):
        with self.assertRaises(ErroCompra):
            registrar_compra(
                self.banco, 999, [(1, 1)]
            )

    def test_09_produto_inexistente(self):
        with self.assertRaises(ErroCompra):
            registrar_compra(
                self.banco, 1, [(999, 1)]
            )

    def test_10_quantidade_invalida(self):
        with self.assertRaises(ErroCompra):
            registrar_compra(
                self.banco, 1, [(1, -1)]
            )

    def test_11_carrinho_vazio(self):
        with self.assertRaises(ErroCompra):
            registrar_compra(self.banco, 1, [])

    def test_12_produtos_repetidos(self):
        compra = registrar_compra(
            self.banco, 1, [(1, 1), (1, 2)]
        )

        self.assertEqual(
            compra["total_centavos"], 45000
        )
        self.assertEqual(
            consultar_estoque(self.banco, 1), 2
        )
        self.assertEqual(
            contar_registros(self.banco)["itens_pedido"], 1
        )

    def test_13_durabilidade_apos_reabrir(self):
        compra = registrar_compra(
            self.banco, 1, [(2, 1)]
        )

        pedido = consultar_pedido(
            self.banco, compra["pedido_id"]
        )

        self.assertEqual(pedido[3], "confirmado")

        with conectar(self.banco) as conexao:
            pagamento = conexao.execute(
                """
                SELECT status
                FROM pagamentos
                WHERE pedido_id = ?
                """,
                (compra["pedido_id"],),
            ).fetchone()

        self.assertEqual(pagamento[0], "aprovado")

    def test_14_integridade_referencial(self):
        with conectar(self.banco) as conexao:
            with self.assertRaises(
                sqlite3.IntegrityError
            ):
                conexao.execute(
                    """
                    INSERT INTO pedidos (cliente_id)
                    VALUES (999)
                    """
                )


if __name__ == "__main__":
    unittest.main()
