"""Testes do modelo logico da Aula 05."""

import sqlite3
import sys
import tempfile
import unittest
from contextlib import closing
from pathlib import Path


BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from src.aula05_modelo_logico import (
    conectar,
    criar_modelo,
    registrar_venda,
    estrutura_tabelas,
    resumo_operacional,
)


class TestModeloLogico(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.banco = Path(self.temp.name) / "modelo.db"
        criar_modelo(self.banco)

    def tearDown(self):
        self.temp.cleanup()

    def test_01_nove_tabelas(self):
        self.assertEqual(
            len(estrutura_tabelas(self.banco)), 9
        )

    def test_02_chave_composta(self):
        colunas = estrutura_tabelas(
            self.banco
        )["itens_pedido"]

        chaves = {
            c["coluna"]: c["pk_ordem"]
            for c in colunas if c["pk_ordem"]
        }

        self.assertEqual(
            chaves,
            {"pedido_id": 1, "produto_id": 2},
        )

    def test_03_cliente_obrigatorio(self):
        with closing(conectar(self.banco)) as conexao:
            with self.assertRaises(sqlite3.IntegrityError):
                with conexao:
                    conexao.execute(
                        """
                        INSERT INTO pedidos (cliente_id)
                        VALUES (999)
                        """
                    )

    def test_04_categoria_obrigatoria(self):
        with closing(conectar(self.banco)) as conexao:
            with self.assertRaises(sqlite3.IntegrityError):
                with conexao:
                    conexao.execute(
                        """
                        INSERT INTO produtos
                        (produto_id, categoria_id,
                         nome, preco_centavos)
                        VALUES (99, 999, 'Teste', 100)
                        """
                    )

    def test_05_compra_confirmada(self):
        venda = registrar_venda(self.banco, 2)
        self.assertEqual(venda["valor_centavos"], 30000)

    def test_06_estoque_atualizado(self):
        registrar_venda(self.banco, 2)
        self.assertEqual(
            resumo_operacional(self.banco)["estoque_teclado"],
            3,
        )

    def test_07_fatura_criada(self):
        registrar_venda(self.banco, 1)
        self.assertEqual(
            resumo_operacional(self.banco)["faturas"], 1
        )

    def test_08_movimento_criado(self):
        registrar_venda(self.banco, 1)
        self.assertEqual(
            resumo_operacional(self.banco)["movimentos"], 1
        )

    def test_09_fatura_unica(self):
        venda = registrar_venda(self.banco, 1)

        with closing(conectar(self.banco)) as conexao:
            with self.assertRaises(sqlite3.IntegrityError):
                with conexao:
                    conexao.execute(
                        """
                        INSERT INTO faturas
                        (pedido_id, valor_centavos)
                        VALUES (?, 15000)
                        """,
                        (venda["pedido_id"],),
                    )

    def test_10_produto_unico_por_pedido(self):
        venda = registrar_venda(self.banco, 1)

        with closing(conectar(self.banco)) as conexao:
            with self.assertRaises(sqlite3.IntegrityError):
                with conexao:
                    conexao.execute(
                        """
                        INSERT INTO itens_pedido
                        (pedido_id, produto_id,
                         quantidade, preco_unitario_centavos)
                        VALUES (?, 1, 1, 15000)
                        """,
                        (venda["pedido_id"],),
                    )

    def test_11_estoque_insuficiente_revertido(self):
        with self.assertRaises(ValueError):
            registrar_venda(self.banco, 99)

        resumo = resumo_operacional(self.banco)

        self.assertEqual(resumo["pedidos"], 0)
        self.assertEqual(resumo["estoque_teclado"], 5)

    def test_12_quantidade_invalida(self):
        with self.assertRaises(ValueError):
            registrar_venda(self.banco, -1)

        self.assertEqual(
            resumo_operacional(self.banco)["pedidos"], 0
        )


if __name__ == "__main__":
    unittest.main()
