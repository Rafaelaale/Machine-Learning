"""Testes automatizados do Data Warehouse da Minishop."""

import sqlite3
import sys
import tempfile
import unittest
from contextlib import closing
from pathlib import Path


BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from src.aula05_modelo_logico import (
    criar_modelo,
    registrar_venda,
    resumo_operacional,
)

from src.aula06_data_warehouse import (
    carregar_dw,
    extrair_vendas,
    faturamento_mensal,
    faturamento_por_categoria,
    historico_cargas,
    indicadores_dw,
    validar_vendas,
)


class TestDataWarehouse(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        raiz = Path(self.temp.name)

        self.oltp = raiz / "operacional.db"
        self.dw = raiz / "warehouse.db"

        criar_modelo(self.oltp)

    def tearDown(self):
        self.temp.cleanup()

    def comprar(self, quantidade=2):
        return registrar_venda(self.oltp, quantidade)

    def test_01_ambientes_separados(self):
        self.comprar()
        carregar_dw(self.oltp, self.dw)

        self.assertTrue(self.oltp.exists())
        self.assertTrue(self.dw.exists())
        self.assertNotEqual(self.oltp, self.dw)

    def test_02_extracao_confirmada(self):
        self.comprar()

        registros = extrair_vendas(self.oltp)

        self.assertEqual(len(registros), 1)
        self.assertEqual(
            registros[0]["valor_centavos"], 30000
        )

    def test_03_carga_faturamento(self):
        self.comprar()
        carregar_dw(self.oltp, self.dw)

        self.assertEqual(
            indicadores_dw(self.dw)["faturamento_centavos"],
            30000,
        )

    def test_04_dimensao_categoria(self):
        self.comprar()
        carregar_dw(self.oltp, self.dw)

        categorias = faturamento_por_categoria(self.dw)

        self.assertEqual(len(categorias), 1)
        self.assertEqual(
            categorias[0]["categoria"], "Informatica"
        )

    def test_05_dimensao_tempo(self):
        self.comprar()
        carregar_dw(self.oltp, self.dw)

        meses = faturamento_mensal(self.dw)

        self.assertEqual(len(meses), 1)
        self.assertEqual(
            meses[0]["faturamento_centavos"], 30000
        )

    def test_06_idempotencia(self):
        self.comprar()

        primeiro = carregar_dw(self.oltp, self.dw)
        segundo = carregar_dw(self.oltp, self.dw)

        self.assertEqual(
            primeiro["lote_id"], segundo["lote_id"]
        )
        self.assertFalse(segundo["nova_carga"])
        self.assertEqual(
            len(historico_cargas(self.dw)), 1
        )

    def test_07_fotografia_desatualizada(self):
        self.comprar(1)
        carregar_dw(self.oltp, self.dw)

        self.comprar(1)

        self.assertEqual(
            indicadores_dw(self.dw)["faturamento_centavos"],
            15000,
        )

    def test_08_novo_lote(self):
        self.comprar(1)
        primeiro = carregar_dw(self.oltp, self.dw)

        self.comprar(1)
        segundo = carregar_dw(self.oltp, self.dw)

        self.assertNotEqual(
            primeiro["lote_id"], segundo["lote_id"]
        )
        self.assertTrue(segundo["nova_carga"])

    def test_09_historico_preservado(self):
        self.comprar(1)
        primeiro = carregar_dw(self.oltp, self.dw)

        self.comprar(1)
        carregar_dw(self.oltp, self.dw)

        anterior = indicadores_dw(
            self.dw, primeiro["lote_id"]
        )
        atual = indicadores_dw(self.dw)

        self.assertEqual(
            anterior["faturamento_centavos"], 15000
        )
        self.assertEqual(
            atual["faturamento_centavos"], 30000
        )

    def test_10_nao_altera_origem(self):
        self.comprar()

        antes = resumo_operacional(self.oltp)

        carregar_dw(self.oltp, self.dw)

        depois = resumo_operacional(self.oltp)

        self.assertEqual(antes, depois)

    def test_11_origem_inexistente(self):
        with self.assertRaises(FileNotFoundError):
            carregar_dw(
                self.oltp.parent / "nao_existe.db",
                self.dw,
            )

    def test_12_destino_igual_origem(self):
        with self.assertRaises(ValueError):
            carregar_dw(self.oltp, self.oltp)

    def test_13_rejeitar_data_invalida(self):
        vendas = [{
            "pedido_id": 1,
            "produto_id": 1,
            "cliente_nome": "Ana",
            "produto_nome": "Teclado",
            "categoria": "Informatica",
            "quantidade": 1,
            "valor_centavos": 15000,
            "data": "2026-99-99",
        }]

        with self.assertRaises(ValueError):
            validar_vendas(vendas)

    def test_14_pedido_nao_pago_excluido(self):
        with closing(sqlite3.connect(self.oltp)) as conexao:
            with conexao:
                pedido = conexao.execute(
                    """
                    INSERT INTO pedidos
                        (cliente_id, estado, valor_centavos)
                    VALUES (1, 'pendente', 15000)
                    """
                ).lastrowid

                conexao.execute(
                    """
                    INSERT INTO itens_pedido
                        (pedido_id, produto_id,
                         quantidade, preco_unitario_centavos)
                    VALUES (?, 1, 1, 15000)
                    """,
                    (pedido,),
                )

        registros = extrair_vendas(self.oltp)

        self.assertEqual(registros, [])

        carregar_dw(self.oltp, self.dw)

        self.assertEqual(
            indicadores_dw(self.dw)["faturamento_centavos"],
            0,
        )


if __name__ == "__main__":
    unittest.main()
