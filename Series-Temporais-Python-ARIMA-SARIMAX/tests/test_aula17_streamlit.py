"""Testes das funcoes utilizadas pelo app.py."""

import unittest

import numpy as np

from src.aula17_app_utils import (
    carregar_dados,
    validar_colunas,
    formatar_data,
    diagnosticar_calendario,
    grafico_historico,
    grafico_metricas,
    grafico_previsoes,
    COLUNAS_PREVISOES,
)


class TestAula17(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        (
            cls.historico,
            cls.metricas,
            cls.previsoes,
            cls.resumo,
        ) = carregar_dados()

    def test_01_historico(self):
        self.assertEqual(
            len(self.historico), 456
        )

    def test_02_teste(self):
        self.assertEqual(
            len(self.previsoes), 60
        )

    def test_03_modelos(self):
        self.assertEqual(
            len(self.metricas), 4
        )

    def test_04_resumo(self):
        self.assertEqual(
            len(self.resumo), 1
        )

    def test_05_modelo_final(self):
        melhor = (
            self.metricas.sort_values("MAPE")
            .iloc[0]["modelo"]
        )

        self.assertEqual(
            melhor,
            self.resumo.iloc[0]["modelo_final"],
        )

    def test_06_mape_valido(self):
        self.assertTrue(
            np.isfinite(
                self.metricas["MAPE"]
            ).all()
        )

    def test_07_coluna_demanda(self):
        self.assertIn(
            "demanda",
            self.historico.columns,
        )

    def test_08_colunas_previsoes(self):
        for nome in COLUNAS_PREVISOES.values():
            self.assertIn(
                nome,
                self.previsoes.columns,
            )

    def test_09_validacao_colunas(self):
        with self.assertRaises(ValueError):
            validar_colunas(
                self.metricas,
                ["coluna_inexistente"],
                "teste",
            )

    def test_10_formatar_data(self):
        self.assertEqual(
            formatar_data("2011-01-01"),
            "01/01/2011",
        )

    def test_11_dias_ausentes(self):
        self.assertEqual(
            diagnosticar_calendario(
                self.historico
            ),
            263,
        )

    def test_12_grafico_historico(self):
        self.assertEqual(
            len(grafico_historico(
                self.historico
            ).data),
            1,
        )

    def test_13_grafico_metricas(self):
        self.assertEqual(
            len(grafico_metricas(
                self.metricas
            ).data),
            1,
        )

    def test_14_grafico_previsoes(self):
        self.assertEqual(
            len(grafico_previsoes(
                self.previsoes
            ).data),
            5,
        )

    def test_15_filtro_previsoes(self):
        figura = grafico_previsoes(
            self.previsoes,
            ["Demanda real", "SARIMAX"],
        )

        self.assertEqual(
            len(figura.data),
            2,
        )

    def test_16_modelo_invalido(self):
        with self.assertRaises(ValueError):
            grafico_previsoes(
                self.previsoes,
                ["Modelo inexistente"],
            )


if __name__ == "__main__":
    unittest.main()
