"""Testes da Aula 10 - DW misto da Minishop."""

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

from src.aula10_dw_minishop import (
    carregar_dw,
    contagens,
    extrair_oltp,
    indicadores,
    validar_reconciliacao,
)


class TestDWMinishop(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        raiz = Path(cls.temp.name)

        cls.oltp = raiz / "oltp.db"
        cls.dw = raiz / "dw10.db"

        criar_modelo(cls.oltp)
        registrar_venda(cls.oltp, 2)
        carregar_dw(cls.oltp, cls.dw)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def consultar(self, sql, parametros=()):
        with closing(sqlite3.connect(self.dw)) as conexao:
            return conexao.execute(
                sql, parametros
            ).fetchall()

    def test_01_dw_criado(self):
        self.assertTrue(self.dw.is_file())

    def test_02_tres_tabelas_fato(self):
        self.assertEqual(len(contagens(self.dw)), 3)

    def test_03_vendas_carregadas(self):
        self.assertEqual(
            contagens(self.dw)["fato_vendas"], 1
        )

    def test_04_estoque_carregado(self):
        self.assertEqual(
            contagens(self.dw)["fato_inventario"], 1
        )

    def test_05_financeiro_nao_inventado(self):
        self.assertEqual(
            contagens(self.dw)["fato_financeiro"], 0
        )

    def test_06_faturamento(self):
        self.assertEqual(
            indicadores(self.dw)["faturamento_centavos"],
            30000,
        )

    def test_07_quantidade_vendida(self):
        self.assertEqual(
            indicadores(self.dw)["unidades_vendidas"],
            2,
        )

    def test_08_saida_negativa(self):
        self.assertEqual(
            indicadores(self.dw)["saida_estoque"],
            -2,
        )

    def test_09_categoria_snowflake(self):
        dados = indicadores(self.dw)
        self.assertEqual(
            dados["faturamento_por_categoria"][0]["categoria"],
            "Informatica",
        )

    def test_10_cliente_sem_geografia_inventada(self):
        linhas = self.consultar(
            "SELECT cidade, estado, faixa_etaria FROM dim_cliente"
        )
        self.assertEqual(linhas, [(None, None, None)])

    def test_11_promocao_e_acesso_sem_valor(self):
        linhas = self.consultar(
            "SELECT promocao_sk, acesso_sk FROM fato_vendas"
        )
        self.assertEqual(linhas, [(None, None)])

    def test_12_tempo_com_hierarquia(self):
        linhas = self.consultar(
            """
            SELECT ano, mes, trimestre, semestre, dia
            FROM dim_tempo
            """
        )
        self.assertEqual(len(linhas), 1)
        self.assertTrue(1 <= linhas[0][2] <= 4)
        self.assertTrue(1 <= linhas[0][3] <= 2)

    def test_13_oito_faixas_aging(self):
        linhas = self.consultar(
            "SELECT COUNT(*) FROM dim_aging"
        )
        self.assertEqual(linhas[0][0], 8)

    def test_14_reconciliacao(self):
        resultado = validar_reconciliacao(
            self.oltp, self.dw
        )
        self.assertTrue(
            resultado["faturamento_reconciliado"]
        )
        self.assertTrue(
            resultado["estoque_reconciliado"]
        )

    def test_15_origem_preservada(self):
        antes = extrair_oltp(self.oltp)
        carregar_dw(self.oltp, self.dw)
        depois = extrair_oltp(self.oltp)
        self.assertEqual(antes, depois)

    def test_16_chave_estrangeira(self):
        with closing(sqlite3.connect(self.dw)) as conexao:
            conexao.execute("PRAGMA foreign_keys = ON")

            with self.assertRaises(sqlite3.IntegrityError):
                with conexao:
                    conexao.execute(
                        """
                        INSERT INTO fato_inventario
                        VALUES (9999, 9999, -1)
                        """
                    )


if __name__ == "__main__":
    unittest.main()
