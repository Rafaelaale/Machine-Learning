"""16 testes da Aula 25: Lakehouse integrado Minishop."""

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

from src.aula17_data_lake import hash_arquivo

from src.aula25_lakehouse_minishop import (
    executar,
    validar_gold_analitica,
    consultar_lakehouse,
    indicadores_lakehouse,
    indicadores_dw,
    vendas_por_categoria,
    conferir_integracao,
    criar_gold_analitica,
    carregar_dw_dimensional,
)


class TestLakehouseIntegrado(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.raiz = Path(cls.temp.name)

        cls.oltp = cls.raiz / "oltp.db"
        cls.lake = cls.raiz / "lake"

        criar_modelo(cls.oltp)
        registrar_venda(cls.oltp, 1)

        cls.resultado = executar(cls.oltp, cls.lake)
        cls.gold = Path(cls.resultado["gold_analitica"])
        cls.dw = Path(cls.resultado["data_warehouse"])

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_01_bronze_existe(self):
        self.assertTrue(
            Path(self.resultado["bronze"]).is_dir()
        )

    def test_02_silver_existe(self):
        self.assertTrue(
            Path(self.resultado["silver"]).is_dir()
        )

    def test_03_gold_analitica_existe(self):
        self.assertTrue(self.gold.is_dir())

    def test_04_catalogo_valido(self):
        catalogo = validar_gold_analitica(
            self.gold
        )

        self.assertEqual(
            set(catalogo["tabelas"]),
            {
                "vendas_enriquecidas",
                "indicadores_mensais",
            },
        )

    def test_05_gold_parquet_real(self):
        for tabela in (
            "vendas_enriquecidas",
            "indicadores_mensais",
        ):
            arquivo = self.gold / f"{tabela}.parquet"

            with arquivo.open("rb") as entrada:
                self.assertEqual(
                    entrada.read(4), b"PAR1"
                )

    def test_06_consulta_sql_direta(self):
        linhas = consultar_lakehouse(
            self.gold,
            """
            SELECT COUNT(*) AS quantidade
            FROM vendas_enriquecidas
            """,
        )

        self.assertEqual(linhas[0]["quantidade"], 1)

    def test_07_cliente_enriquecido(self):
        linhas = consultar_lakehouse(
            self.gold,
            """
            SELECT cliente_nome
            FROM vendas_enriquecidas
            """,
        )

        self.assertEqual(
            linhas[0]["cliente_nome"], "Ana"
        )

    def test_08_produto_enriquecido(self):
        linhas = consultar_lakehouse(
            self.gold,
            """
            SELECT produto_nome
            FROM vendas_enriquecidas
            """,
        )

        self.assertEqual(
            linhas[0]["produto_nome"], "Teclado"
        )

    def test_09_categoria(self):
        categorias = vendas_por_categoria(
            self.gold
        )

        self.assertEqual(
            categorias[0]["categoria_nome"],
            "Informatica",
        )

    def test_10_lakehouse_faturamento(self):
        self.assertEqual(
            indicadores_lakehouse(self.gold)[
                "faturamento_centavos"
            ],
            15000,
        )

    def test_11_dw_dimensional_existe(self):
        with closing(sqlite3.connect(
            self.dw.resolve().as_uri() + "?mode=ro",
            uri=True,
        )) as con:
            tabelas = {
                linha[0]
                for linha in con.execute(
                    """
                    SELECT name
                    FROM sqlite_master
                    WHERE type='table'
                    """
                )
            }

        self.assertTrue({
            "dim_cliente",
            "dim_produto",
            "dim_tempo",
            "fato_vendas",
        }.issubset(tabelas))

    def test_12_dw_faturamento(self):
        self.assertEqual(
            indicadores_dw(self.dw)[
                "faturamento_centavos"
            ],
            15000,
        )

    def test_13_integracao_consistente(self):
        self.assertTrue(
            conferir_integracao(
                self.gold,
                self.dw,
            )["consistente"]
        )

    def test_14_proibe_escrita_sql(self):
        with self.assertRaises(ValueError):
            consultar_lakehouse(
                self.gold,
                "DELETE FROM vendas_enriquecidas",
            )

    def test_15_preserva_snapshot_e_parquet(self):
        arquivo = self.gold / "vendas_enriquecidas.parquet"
        antes = hash_arquivo(arquivo)

        outro = executar(self.oltp, self.lake)

        self.assertEqual(
            outro["snapshot_id"],
            self.resultado["snapshot_id"],
        )

        self.assertEqual(
            hash_arquivo(arquivo),
            antes,
        )

    def test_16_snapshot_novo_e_historico(self):
        registrar_venda(self.oltp, 1)

        novo = executar(self.oltp, self.lake)

        self.assertNotEqual(
            novo["snapshot_id"],
            self.resultado["snapshot_id"],
        )

        self.assertEqual(
            novo["reconciliacao"]["lakehouse"][
                "faturamento_centavos"
            ],
            30000,
        )

        self.assertEqual(
            indicadores_lakehouse(self.gold)[
                "faturamento_centavos"
            ],
            15000,
        )


if __name__ == "__main__":
    unittest.main()
