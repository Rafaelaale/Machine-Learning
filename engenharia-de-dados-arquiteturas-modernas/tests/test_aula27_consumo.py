"""16 testes de consumo analitico, Aula 27."""

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
from src.aula27_consumo_semantico import (
    CATALOGO_CONSUMO,
    catalogo_publico,
    consultar_indicador,
    relatorio_area,
    demonstrar_conflito_semantico,
    auditar_consumo,
    executar,
)


class TestConsumoSemantico(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.raiz = Path(cls.temp.name)

        cls.oltp = cls.raiz / "minishop.db"
        cls.lake = cls.raiz / "lake"
        cls.exemplos = cls.raiz / "exemplos"

        criar_modelo(cls.oltp)
        registrar_venda(cls.oltp, 1)

        cls.resultado = executar(
            cls.oltp,
            cls.lake,
            cls.exemplos,
        )

        cls.contexto = cls.resultado["contexto"]

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def consultar(self, nome, fonte, dimensao=None):
        return consultar_indicador(
            nome,
            fonte,
            self.contexto,
            dimensao,
        )["resultados"]

    def test_01_catalogo_publico(self):
        self.assertEqual(
            catalogo_publico()["versao"],
            "1.0",
        )

    def test_02_sete_indicadores(self):
        self.assertEqual(
            len(CATALOGO_CONSUMO),
            7,
        )

    def test_03_faturamento_minishop_lakehouse(self):
        self.assertEqual(
            self.consultar(
                "minishop.faturamento", "lakehouse"
            )[0]["valor"],
            15000,
        )

    def test_04_faturamento_minishop_dw(self):
        self.assertEqual(
            self.consultar(
                "minishop.faturamento", "data_warehouse"
            )[0]["valor"],
            15000,
        )

    def test_05_comercial_mesma_metrica(self):
        dados = relatorio_area(
            "comercial", self.contexto, "lakehouse"
        )
        self.assertEqual(
            dados["faturamento_centavos"],
            15000,
        )

    def test_06_financeiro_mesma_metrica(self):
        dados = relatorio_area(
            "financeiro", self.contexto, "data_warehouse"
        )
        self.assertEqual(
            dados["faturamento_centavos"],
            15000,
        )

    def test_07_duas_areas_concordam(self):
        a = self.resultado["relatorios"]["comercial"]
        b = self.resultado["relatorios"]["financeiro"]

        for campo in (
            "faturamento_centavos",
            "pedidos",
            "ticket_medio_centavos",
        ):
            self.assertEqual(a[campo], b[campo])

    def test_08_faturas_emitidas_didaticas(self):
        self.assertEqual(
            self.consultar(
                "contas.valor_faturado", "contas_gold"
            )[0]["valor"],
            230000,
        )

    def test_09_valor_recebido_didatico(self):
        self.assertEqual(
            self.consultar(
                "contas.entrada_caixa", "contas_gold"
            )[0]["valor"],
            150000,
        )

    def test_10_saldo_aberto_didatico(self):
        self.assertEqual(
            self.consultar(
                "contas.saldo_aberto", "contas_gold"
            )[0]["valor"],
            80000,
        )

    def test_11_conflito_semantico_identificado(self):
        conflito = demonstrar_conflito_semantico(
            self.contexto
        )
        self.assertFalse(conflito["iguais"])
        self.assertEqual(
            conflito["diferenca_centavos"],
            80000,
        )

    def test_12_agrupamento_por_estado(self):
        dados = self.consultar(
            "contas.entrada_caixa",
            "contas_gold",
            "estado",
        )
        estados = {
            item["dimensao"]: item["valor"]
            for item in dados
        }
        self.assertEqual(estados["MG"], 150000)
        self.assertEqual(estados["SP"], 0)

    def test_13_agrupamento_por_categoria(self):
        dados = self.consultar(
            "minishop.faturamento",
            "lakehouse",
            "categoria",
        )
        self.assertEqual(
            dados[0]["dimensao"],
            "Informatica",
        )

    def test_14_bloqueia_fonte_incorreta(self):
        with self.assertRaises(ValueError):
            self.consultar(
                "contas.entrada_caixa",
                "data_warehouse",
            )

    def test_15_bloqueia_metrica_inexistente(self):
        with self.assertRaises(ValueError):
            self.consultar(
                "minishop.lucro",
                "lakehouse",
            )

    def test_16_auditoria_integral(self):
        auditoria = auditar_consumo(
            self.contexto
        )
        self.assertTrue(auditoria["consistente"])
        self.assertTrue(
            auditoria["contas_didaticas_conciliadas"]
        )
        self.assertEqual(
            auditoria["comparacoes_entre_fontes"],
            20,
        )


if __name__ == "__main__":
    unittest.main()
