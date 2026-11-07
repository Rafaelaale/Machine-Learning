"""Testes automatizados da Aula 07."""

import json
import unittest

import numpy as np
import pandas as pd

from src.aula07_acf_pacf import (
    carregar_serie_diferenciada,
    calcular_acf_pacf,
    grafico_lags,
    grafico_comparacao,
    CSV_ACF,
    CSV_PACF,
    CSV_COMPARACAO,
    JSON_RELATORIO,
    HTML_ACF,
    HTML_PACF,
    HTML_COMPARACAO,
)


class TestAula07(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.df = carregar_serie_diferenciada()
        cls.tabela, cls.limite = calcular_acf_pacf(
            cls.df["demanda_diff"],
            nlags=30,
        )

    def test_01_serie_diferenciada(self):
        self.assertIn("demanda_diff", self.df.columns)

    def test_02_sem_nan(self):
        self.assertFalse(
            self.df["demanda_diff"].isna().any()
        )

    def test_03_tamanho_acf(self):
        self.assertEqual(len(self.tabela), 31)

    def test_04_lags_0_a_30(self):
        self.assertEqual(
            self.tabela["lag"].tolist(),
            list(range(31)),
        )

    def test_05_acf_lag_zero(self):
        self.assertAlmostEqual(
            self.tabela["acf"].iloc[0],
            1.0,
        )

    def test_06_pacf_lag_zero(self):
        self.assertAlmostEqual(
            self.tabela["pacf"].iloc[0],
            1.0,
        )

    def test_07_acf_entre_menos_um_e_um(self):
        self.assertTrue(
            np.all(
                np.abs(self.tabela["acf"]) <= 1.000001
            )
        )

    def test_08_pacf_entre_menos_um_e_um(self):
        self.assertTrue(
            np.all(
                np.abs(self.tabela["pacf"]) <= 1.000001
            )
        )

    def test_09_sem_valores_nan(self):
        self.assertFalse(
            self.tabela[["acf", "pacf"]]
            .isna().any().any()
        )

    def test_10_limite_positivo(self):
        self.assertGreater(self.limite, 0)
        self.assertLess(self.limite, 1)

    def test_11_lag_zero_nao_sinalizado(self):
        self.assertFalse(
            bool(self.tabela["fora_faixa_acf"].iloc[0])
        )
        self.assertFalse(
            bool(self.tabela["fora_faixa_pacf"].iloc[0])
        )

    def test_12_entrada_constante(self):
        with self.assertRaises(ValueError):
            calcular_acf_pacf(
                pd.Series([2] * 100)
            )

    def test_13_numero_lags_invalido(self):
        with self.assertRaises(ValueError):
            calcular_acf_pacf(
                self.df["demanda_diff"],
                nlags=0,
            )

    def test_14_graficos_individuais(self):
        acf_fig = grafico_lags(
            self.tabela, "acf", "ACF", self.limite
        )
        pacf_fig = grafico_lags(
            self.tabela, "pacf", "PACF", self.limite
        )

        self.assertEqual(len(acf_fig.data), 1)
        self.assertEqual(len(pacf_fig.data), 1)

    def test_15_grafico_comparativo(self):
        fig = grafico_comparacao(
            self.tabela, self.limite
        )
        self.assertEqual(len(fig.data), 2)

    def test_16_arquivos_e_relatorio(self):
        for caminho in (
            CSV_ACF,
            CSV_PACF,
            CSV_COMPARACAO,
            JSON_RELATORIO,
            HTML_ACF,
            HTML_PACF,
            HTML_COMPARACAO,
        ):
            self.assertTrue(
                caminho.is_file(),
                str(caminho),
            )
            self.assertGreater(
                caminho.stat().st_size,
                0,
            )

        with JSON_RELATORIO.open(
            encoding="utf-8"
        ) as arquivo:
            relatorio = json.load(arquivo)

        self.assertEqual(relatorio["numero_lags"], 30)
        self.assertFalse(relatorio["modelo_arima_treinado"])


if __name__ == "__main__":
    unittest.main()
