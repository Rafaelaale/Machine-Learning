"""Testes do ambiente analitico separado da Minishop."""

import sqlite3
from contextlib import closing
import sys
import tempfile
import unittest
from pathlib import Path


BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from src.minishop_oltp import (
    consultar_pedido,
    criar_banco,
    registrar_compra,
)

from src.minishop_olap import (
    carregar_olap,
    conectar,
    faturamento_mensal,
    faturamento_por_produto,
    indicadores,
    ler_vendas_confirmadas,
)


class TestOLAP(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        raiz = Path(self.temp.name)

        self.oltp = raiz / "transacional.db"
        self.olap = raiz / "analitico.db"

        criar_banco(self.oltp)

    def tearDown(self):
        self.temp.cleanup()

    def comprar(self):
        return registrar_compra(
            self.oltp,
            cliente_id=1,
            itens=[(1, 1), (2, 2)],
        )

    def test_01_ambientes_separados(self):
        self.comprar()
        carregar_olap(self.oltp, self.olap)

        self.assertTrue(self.oltp.exists())
        self.assertTrue(self.olap.exists())
        self.assertNotEqual(self.oltp, self.olap)

    def test_02_carga_de_itens(self):
        self.comprar()

        quantidade = carregar_olap(
            self.oltp, self.olap
        )

        self.assertEqual(quantidade, 2)

    def test_03_faturamento(self):
        self.comprar()
        carregar_olap(self.oltp, self.olap)

        self.assertEqual(
            indicadores(self.olap)["faturamento_centavos"],
            31000,
        )

    def test_04_ticket_medio(self):
        self.comprar()
        carregar_olap(self.oltp, self.olap)

        self.assertEqual(
            indicadores(self.olap)["ticket_medio_centavos"],
            31000,
        )

    def test_05_total_unidades(self):
        self.comprar()
        carregar_olap(self.oltp, self.olap)

        self.assertEqual(
            indicadores(self.olap)["unidades_vendidas"],
            3,
        )

    def test_06_agrupamento_por_produto(self):
        self.comprar()
        carregar_olap(self.oltp, self.olap)

        produtos = faturamento_por_produto(self.olap)

        self.assertEqual(len(produtos), 2)
        self.assertEqual(
            sum(
                p["faturamento_centavos"]
                for p in produtos
            ),
            31000,
        )

    def test_07_agrupamento_mensal(self):
        self.comprar()
        carregar_olap(self.oltp, self.olap)

        meses = faturamento_mensal(self.olap)

        self.assertEqual(len(meses), 1)
        self.assertEqual(
            meses[0]["faturamento_centavos"],
            31000,
        )

    def test_08_carga_repetida_sem_duplicacao(self):
        self.comprar()

        carregar_olap(self.oltp, self.olap)
        carregar_olap(self.oltp, self.olap)

        self.assertEqual(
            indicadores(self.olap)["linhas_fato"],
            2,
        )

    def test_09_oltp_nao_foi_alterado(self):
        compra = self.comprar()

        antes = consultar_pedido(
            self.oltp, compra["pedido_id"]
        )

        carregar_olap(self.oltp, self.olap)

        depois = consultar_pedido(
            self.oltp, compra["pedido_id"]
        )

        self.assertEqual(antes, depois)

    def test_10_erro_origem_inexistente(self):
        with self.assertRaises(FileNotFoundError):
            carregar_olap(
                self.oltp.parent / "nao_existe.db",
                self.olap,
            )

        self.assertFalse(self.olap.exists())

    def test_11_pedidos_pendentes_excluidos(self):
        with closing(sqlite3.connect(self.oltp)) as conexao:
            cursor = conexao.execute(
                """
                INSERT INTO pedidos (cliente_id)
                VALUES (1)
                """
            )

            conexao.execute(
                """
                INSERT INTO itens_pedido (
                    pedido_id, produto_id,
                    quantidade, preco_unitario_centavos
                )
                VALUES (?, 1, 1, 15000)
                """,
                (cursor.lastrowid,),
            )

        vendas = ler_vendas_confirmadas(self.oltp)

        self.assertEqual(vendas, [])

        carregar_olap(self.oltp, self.olap)

        self.assertEqual(
            indicadores(self.olap)["faturamento_centavos"],
            0,
        )

    def test_12_fotografia_atualizavel(self):
        self.comprar()
        carregar_olap(self.oltp, self.olap)

        primeiro = indicadores(
            self.olap
        )["faturamento_centavos"]

        registrar_compra(
            self.oltp,
            cliente_id=2,
            itens=[(3, 1)],
        )

        # Sem nova carga, o OLAP preserva a fotografia.
        self.assertEqual(
            indicadores(self.olap)["faturamento_centavos"],
            primeiro,
        )

        carregar_olap(self.oltp, self.olap)

        segundo = indicadores(
            self.olap
        )["faturamento_centavos"]

        self.assertEqual(primeiro, 31000)
        self.assertEqual(segundo, 121000)


if __name__ == "__main__":
    unittest.main()
