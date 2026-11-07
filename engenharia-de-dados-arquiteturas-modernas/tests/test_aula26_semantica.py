"""16 testes da Aula 26 - Camada semantica."""

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

from src.aula26_camada_semantica import (
    METRICAS,
    DIMENSOES,
    catalogo_semantico,
    construir_sql,
    consultar_metrica,
    comparar_fontes,
    auditar_consistencia,
    relatorio_bi,
    executar,
)


class TestCamadaSemantica(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.raiz = Path(cls.temp.name)
        cls.oltp = cls.raiz / "oltp.db"
        cls.lake = cls.raiz / "lake"

        criar_modelo(cls.oltp)
        registrar_venda(cls.oltp, 1)

        cls.projeto = executar(
            cls.oltp,
            cls.lake,
        )

        cls.gold = Path(
            cls.projeto["gold"]
        )

        cls.dw = Path(
            cls.projeto["data_warehouse"]
        )

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def consultar(self, metrica, fonte, dimensao=None):
        return consultar_metrica(
            metrica,
            fonte,
            gold=self.gold,
            dw=self.dw,
            dimensao=dimensao,
        )["resultados"]

    def test_01_quatro_metricas(self):
        self.assertEqual(
            set(METRICAS),
            {
                "faturamento",
                "pedidos",
                "unidades",
                "ticket_medio",
            },
        )

    def test_02_quatro_dimensoes(self):
        self.assertEqual(
            set(DIMENSOES),
            {
                "cliente",
                "produto",
                "categoria",
                "mes",
            },
        )

    def test_03_catalogo_tem_regras(self):
        catalogo = catalogo_semantico()

        self.assertIn(
            "ticket_medio",
            catalogo["metricas"],
        )

        self.assertEqual(
            catalogo["politicas"]["armazenamento_financeiro"],
            "centavos",
        )

    def test_04_faturamento_lakehouse(self):
        self.assertEqual(
            self.consultar(
                "faturamento", "lakehouse"
            )[0]["valor"],
            15000,
        )

    def test_05_faturamento_dw(self):
        self.assertEqual(
            self.consultar(
                "faturamento", "data_warehouse"
            )[0]["valor"],
            15000,
        )

    def test_06_pedidos_distintos(self):
        self.assertEqual(
            self.consultar(
                "pedidos", "lakehouse"
            )[0]["valor"],
            1,
        )

    def test_07_unidades(self):
        self.assertEqual(
            self.consultar(
                "unidades", "data_warehouse"
            )[0]["valor"],
            1,
        )

    def test_08_ticket_medio(self):
        resultado = comparar_fontes(
            "ticket_medio",
            self.gold,
            self.dw,
        )

        self.assertTrue(resultado["iguais"])

        self.assertEqual(
            resultado["lakehouse"][0]["valor"],
            15000.0,
        )

    def test_09_dimensao_cliente(self):
        dados = self.consultar(
            "faturamento",
            "lakehouse",
            "cliente",
        )

        self.assertEqual(
            dados[0]["dimensao"],
            "Ana",
        )

    def test_10_dimensao_produto(self):
        dados = self.consultar(
            "unidades",
            "data_warehouse",
            "produto",
        )

        self.assertEqual(
            dados[0]["dimensao"],
            "Teclado",
        )

    def test_11_dimensao_categoria(self):
        dados = self.consultar(
            "faturamento",
            "lakehouse",
            "categoria",
        )

        self.assertEqual(
            dados[0]["dimensao"],
            "Informatica",
        )

    def test_12_dimensao_mes(self):
        dados = self.consultar(
            "pedidos",
            "data_warehouse",
            "mes",
        )

        self.assertRegex(
            dados[0]["dimensao"],
            r"^\d{4}-\d{2}$",
        )

    def test_13_comparacao_por_dimensao(self):
        resultado = comparar_fontes(
            "faturamento",
            self.gold,
            self.dw,
            "categoria",
        )

        self.assertTrue(resultado["iguais"])

    def test_14_auditoria_de_20_comparacoes(self):
        auditoria = auditar_consistencia(
            self.gold,
            self.dw,
        )

        self.assertEqual(
            auditoria["comparacoes"],
            20,
        )

        self.assertTrue(
            auditoria["consistente"]
        )

        self.assertEqual(
            auditoria["divergencias"],
            [],
        )

    def test_15_impede_metrica_nao_definida(self):
        with self.assertRaises(ValueError):
            construir_sql(
                "lucro_inventado",
                None,
                "lakehouse",
            )

        with self.assertRaises(ValueError):
            construir_sql(
                "faturamento",
                "cidade",
                "lakehouse",
            )

    def test_16_dois_consumidores_mesmas_metricas(self):
        painel_lakehouse = relatorio_bi(
            self.gold,
            self.dw,
            "lakehouse",
        )

        painel_dw = relatorio_bi(
            self.gold,
            self.dw,
            "data_warehouse",
        )

        self.assertEqual(
            painel_lakehouse,
            painel_dw,
        )

        self.assertEqual(
            painel_dw["faturamento"],
            15000,
        )


if __name__ == "__main__":
    unittest.main()
