"""Testes da Aula 09 - Fatos e surrogate keys."""

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
)
from src.aula06_data_warehouse import carregar_dw
from src.aula09_fatos_surrogate import (
    construir_modelo,
    consultar_dimensoes,
    extrair_dw,
    indicadores,
    reconciliar,
)


class TestFatosSurrogate(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        raiz = Path(cls.temp.name)

        cls.oltp = raiz / "oltp.db"
        cls.dw = raiz / "dw.db"
        cls.modelo = raiz / "modelo.db"

        criar_modelo(cls.oltp)

        # Duas compras do mesmo produto pelo mesmo
        # cliente na mesma data, em pedidos diferentes.
        registrar_venda(cls.oltp, 1)
        registrar_venda(cls.oltp, 1)

        carregar_dw(cls.oltp, cls.dw)
        construir_modelo(cls.dw, cls.modelo)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_01_banco_criado(self):
        self.assertTrue(self.modelo.exists())

    def test_02_dimensoes_possuem_sk(self):
        dims = consultar_dimensoes(self.modelo)

        self.assertGreater(
            dims["clientes"][0]["sk"], 0
        )
        self.assertGreater(
            dims["produtos"][0]["sk"], 0
        )
        self.assertGreater(
            dims["tempo"][0]["sk"], 0
        )

    def test_03_chaves_naturais_preservadas(self):
        dims = consultar_dimensoes(self.modelo)

        self.assertEqual(
            dims["clientes"][0]["id_origem"], 1
        )
        self.assertEqual(
            dims["produtos"][0]["id_origem"], 1
        )

    def test_04_duas_linhas_detalhadas(self):
        dados = indicadores(self.modelo, "detalhe")
        self.assertEqual(dados["linhas"], 2)

    def test_05_uma_linha_agregada(self):
        dados = indicadores(self.modelo, "resumo")
        self.assertEqual(dados["linhas"], 1)

    def test_06_duas_unidades_detalhadas(self):
        dados = indicadores(self.modelo, "detalhe")
        self.assertEqual(dados["unidades"], 2)

    def test_07_duas_unidades_agregadas(self):
        dados = indicadores(self.modelo, "resumo")
        self.assertEqual(dados["unidades"], 2)

    def test_08_faturamento_detalhado(self):
        dados = indicadores(self.modelo, "detalhe")
        self.assertEqual(
            dados["faturamento_centavos"], 30000
        )

    def test_09_faturamento_agregado(self):
        dados = indicadores(self.modelo, "resumo")
        self.assertEqual(
            dados["faturamento_centavos"], 30000
        )

    def test_10_totais_reconciliados(self):
        dados = reconciliar(self.modelo)
        self.assertTrue(dados["totais_iguais"])

    def test_11_preco_medio_ponderado(self):
        dados = indicadores(self.modelo, "resumo")
        self.assertEqual(
            dados["preco_medio_unitario_centavos"],
            15000,
        )

    def test_12_pedidos_distintos_preservados(self):
        with closing(
            sqlite3.connect(self.modelo)
        ) as conexao:
            detalhe = conexao.execute(
                """
                SELECT COUNT(DISTINCT pedido_numero)
                FROM fato_vendas_detalhe
                """
            ).fetchone()[0]

            resumo = conexao.execute(
                """
                SELECT pedidos_distintos
                FROM fato_vendas_resumo
                """
            ).fetchone()[0]

        self.assertEqual(detalhe, 2)
        self.assertEqual(resumo, 2)

    def test_13_chave_estrangeira_protegida(self):
        with closing(
            sqlite3.connect(self.modelo)
        ) as conexao:
            conexao.execute("PRAGMA foreign_keys = ON")

            with self.assertRaises(sqlite3.IntegrityError):
                with conexao:
                    conexao.execute(
                        """
                        INSERT INTO fato_vendas_resumo
                        (tempo_sk, cliente_sk, produto_sk,
                         quantidade, valor_centavos,
                         pedidos_distintos)
                        VALUES (999, 999, 999, 1, 100, 1)
                        """
                    )

    def test_14_fonte_permanece_intacta(self):
        antes = extrair_dw(self.dw)
        construir_modelo(self.dw, self.modelo)
        depois = extrair_dw(self.dw)

        self.assertEqual(antes, depois)


if __name__ == "__main__":
    unittest.main()
