"""16 testes da Aula 21 - Introducao ao Lakehouse."""

import sys
import tempfile
import unittest
from pathlib import Path


BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from src.aula05_modelo_logico import (
    criar_modelo,
    registrar_venda,
)

from src.aula17_data_lake import (
    hash_arquivo,
    validar_snapshot,
)

from src.aula20_data_lake_minishop import (
    ler_silver,
    validar_camada,
)

from src.aula21_introducao_lakehouse import (
    executar_laboratorio,
    abrir_consulta_silver,
    consulta_sql,
    indicadores_silver,
    consultar_mensal,
    consultar_produtos,
    consultar_clientes,
    reconciliar_gold,
    consultar_snapshot_sem_oltp,
)


class TestIntroducaoLakehouse(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.raiz = Path(self.temp.name)

        self.oltp = self.raiz / "oltp.db"
        self.lake = self.raiz / "lake"

        criar_modelo(self.oltp)
        registrar_venda(self.oltp, 1)

        self.resultado = executar_laboratorio(
            self.oltp, self.lake
        )

        camadas = self.resultado["camadas"]

        self.bronze = Path(
            camadas["snapshot"]["pasta"]
        )

        self.silver = Path(
            camadas["silver"]["pasta"]
        )

        self.gold = Path(
            camadas["gold"]["pasta"]
        )

    def tearDown(self):
        self.temp.cleanup()

    def test_01_snapshot_bronze_preservado(self):
        self.assertTrue(
            validar_snapshot(self.bronze)
        )

    def test_02_silver_validada(self):
        self.assertEqual(
            validar_camada(
                self.silver, "silver"
            )["camada"],
            "silver",
        )

    def test_03_gold_validada(self):
        self.assertEqual(
            validar_camada(
                self.gold, "gold"
            )["camada"],
            "gold",
        )

    def test_04_sql_conta_vendas(self):
        linhas = consulta_sql(
            self.silver,
            "SELECT COUNT(*) AS total FROM vendas",
        )
        self.assertEqual(
            linhas[0]["total"], 1
        )

    def test_05_sql_faturamento(self):
        metricas = indicadores_silver(
            self.silver
        )
        self.assertEqual(
            metricas["faturamento_centavos"],
            15000,
        )

    def test_06_sql_unidades(self):
        self.assertEqual(
            indicadores_silver(
                self.silver
            )["unidades"],
            1,
        )

    def test_07_sql_cliente(self):
        clientes = consultar_clientes(
            self.silver
        )
        self.assertEqual(len(clientes), 1)
        self.assertEqual(
            clientes[0]["cliente"], "Ana"
        )

    def test_08_sql_produto(self):
        produtos = consultar_produtos(
            self.silver
        )
        self.assertEqual(
            produtos[0]["produto"], "Teclado"
        )

    def test_09_sql_categoria(self):
        produtos = consultar_produtos(
            self.silver
        )
        self.assertEqual(
            produtos[0]["categoria"],
            "Informatica",
        )

    def test_10_sql_mensal(self):
        mensal = consultar_mensal(
            self.silver
        )
        self.assertEqual(len(mensal), 1)
        self.assertEqual(
            mensal[0]["faturamento_centavos"],
            15000,
        )

    def test_11_reconciliacao_gold(self):
        comparacao = reconciliar_gold(
            self.silver, self.gold
        )
        self.assertTrue(
            comparacao["reconciliado"]
        )

    def test_12_consulta_somente_leitura(self):
        with self.assertRaises(ValueError):
            consulta_sql(
                self.silver,
                "DELETE FROM vendas",
            )

        with abrir_consulta_silver(
            self.silver
        ) as con:
            with self.assertRaises(
                Exception
            ):
                con.execute(
                    "DELETE FROM vendas"
                )

    def test_13_sem_dw_persistente(self):
        self.assertFalse(
            self.resultado[
                "banco_dw_persistente_criado"
            ]
        )

        self.assertEqual(
            list(self.raiz.glob("dw*.db")),
            [],
        )

    def test_14_bronze_nao_alterada(self):
        antes = hash_arquivo(
            self.bronze / "oltp.sqlite"
        )

        consultar_snapshot_sem_oltp(
            self.silver
        )

        depois = hash_arquivo(
            self.bronze / "oltp.sqlite"
        )

        self.assertEqual(antes, depois)

    def test_15_consulta_sem_oltp_original(self):
        indisponivel = (
            self.raiz / "oltp_indisponivel.db"
        )

        self.oltp.rename(indisponivel)

        try:
            resultado = consultar_snapshot_sem_oltp(
                self.silver
            )
            self.assertEqual(
                resultado["indicadores"][
                    "faturamento_centavos"
                ],
                15000,
            )
        finally:
            indisponivel.rename(self.oltp)

    def test_16_novo_snapshot_nova_consulta(self):
        antigo = indicadores_silver(
            self.silver
        )

        registrar_venda(
            self.oltp, 1
        )

        novo = executar_laboratorio(
            self.oltp, self.lake
        )

        nova_silver = (
            novo["camadas"]["silver"]["pasta"]
        )

        recente = indicadores_silver(
            nova_silver
        )

        self.assertEqual(
            antigo["faturamento_centavos"],
            15000,
        )
        self.assertEqual(
            recente["faturamento_centavos"],
            30000,
        )
        self.assertTrue(
            validar_snapshot(self.bronze)
        )


if __name__ == "__main__":
    unittest.main()
