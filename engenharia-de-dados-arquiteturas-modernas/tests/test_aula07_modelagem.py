"""Testes da modelagem estrela, snowflake e pai-filho."""

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
from src.aula07_modelagem_dimensional import (
    comparar_modelos,
    consultar_hierarquia,
    extrair_ultimo_lote,
    gerar_modelos,
    indicadores,
    vendas_por_categoria,
)


class TestModelagemDimensional(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        raiz = Path(self.temp.name)

        self.oltp = raiz / "oltp.db"
        self.dw = raiz / "dw.db"
        self.modelo = raiz / "modelagem.db"

        criar_modelo(self.oltp)
        registrar_venda(self.oltp, 2)
        carregar_dw(self.oltp, self.dw)
        gerar_modelos(self.dw, self.modelo)

    def tearDown(self):
        self.temp.cleanup()

    def test_01_banco_fisico_criado(self):
        self.assertTrue(self.modelo.is_file())

    def test_02_modelo_estrela_pedidos(self):
        resultado = indicadores(self.modelo, "estrela")
        self.assertEqual(resultado["pedidos"], 1)

    def test_03_modelo_snowflake_pedidos(self):
        resultado = indicadores(
            self.modelo, "snowflake"
        )
        self.assertEqual(resultado["pedidos"], 1)

    def test_04_faturamento_estrela(self):
        resultado = indicadores(self.modelo, "estrela")
        self.assertEqual(
            resultado["faturamento_centavos"], 30000
        )

    def test_05_faturamento_snowflake(self):
        resultado = indicadores(
            self.modelo, "snowflake"
        )
        self.assertEqual(
            resultado["faturamento_centavos"], 30000
        )

    def test_06_modelos_equivalentes(self):
        resultado = comparar_modelos(self.modelo)
        self.assertTrue(resultado["equivalentes"])

    def test_07_categoria_estrela(self):
        resultado = vendas_por_categoria(
            self.modelo, "estrela"
        )
        self.assertEqual(
            resultado[0]["categoria"], "Informatica"
        )

    def test_08_categoria_snowflake(self):
        resultado = vendas_por_categoria(
            self.modelo, "snowflake"
        )
        self.assertEqual(
            resultado[0]["faturamento_centavos"],
            30000,
        )

    def test_09_hierarquia_regular(self):
        caminhos = consultar_hierarquia(
            self.modelo, "Salvador"
        )
        self.assertEqual(
            caminhos, ["Brasil > Bahia > Salvador"]
        )

    def test_10_hierarquia_irregular(self):
        caminhos = consultar_hierarquia(
            self.modelo, "Monaco"
        )
        self.assertEqual(
            caminhos, ["Monaco > Monaco"]
        )

    def test_11_cidade_desconhecida(self):
        self.assertEqual(
            consultar_hierarquia(
                self.modelo, "Cidade inexistente"
            ),
            [],
        )

    def test_12_fonte_preservada(self):
        antes = extrair_ultimo_lote(self.dw)
        gerar_modelos(self.dw, self.modelo)
        depois = extrair_ultimo_lote(self.dw)
        self.assertEqual(antes, depois)

    def test_13_reexecucao_sem_duplicacao(self):
        gerar_modelos(self.dw, self.modelo)
        resultado = indicadores(self.modelo, "estrela")
        self.assertEqual(resultado["linhas"], 1)

    def test_14_origem_inexistente(self):
        with self.assertRaises(FileNotFoundError):
            gerar_modelos(
                self.modelo.parent / "ausente.db",
                self.modelo,
            )

    def test_15_destino_igual_origem(self):
        with self.assertRaises(ValueError):
            gerar_modelos(self.dw, self.dw)

    def test_16_integridade_referencial(self):
        with closing(
            sqlite3.connect(self.modelo)
        ) as conexao:
            conexao.execute("PRAGMA foreign_keys = ON")
            with self.assertRaises(
                sqlite3.IntegrityError
            ):
                with conexao:
                    conexao.execute(
                        """
                        INSERT INTO snow_dim_produtos
                        VALUES (999, 'Invalido', 999)
                        """
                    )


if __name__ == "__main__":
    unittest.main()
