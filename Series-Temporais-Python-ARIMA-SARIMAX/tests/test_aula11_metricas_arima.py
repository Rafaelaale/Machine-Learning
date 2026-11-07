"""Testes da Aula 11."""

import json
import unittest

import numpy as np
import pandas as pd

from src.aula11_metricas_arima import (
    carregar_previsoes,
    calcular_metrica,
    comparar_modelos,
    calcular_residuos,
    grafico_metricas,
    grafico_residuos,
    CSV_PREVISOES,
    CSV_METRICAS,
    CSV_RESIDUOS,
    JSON_RELATORIO,
    HTML_METRICAS,
    HTML_RESIDUOS,
)


class TestAula11(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.teste = carregar_previsoes()
        cls.metricas = comparar_modelos(cls.teste)
        cls.residuos = calcular_residuos(cls.teste)

    def test_01_60_previsoes(self):
        self.assertEqual(len(self.teste), 60)

    def test_02_quatro_colunas(self):
        self.assertEqual(len(self.teste.columns), 4)

    def test_03_mae_simples(self):
        resultado = calcular_metrica(
            [10, 20, 30],
            [12, 18, 33],
        )
        self.assertAlmostEqual(
            resultado["MAE"],
            7 / 3,
        )

    def test_04_rmse_simples(self):
        resultado = calcular_metrica(
            [10, 20, 30],
            [12, 18, 33],
        )
        self.assertAlmostEqual(
            resultado["RMSE"],
            np.sqrt(17 / 3),
        )

    def test_05_mape_simples(self):
        resultado = calcular_metrica(
            [100, 200],
            [90, 220],
        )
        self.assertAlmostEqual(
            resultado["MAPE"],
            10.0,
        )

    def test_06_mape_ignora_zero(self):
        resultado = calcular_metrica(
            [0, 100],
            [10, 90],
        )
        self.assertAlmostEqual(
            resultado["MAPE"],
            10.0,
        )

    def test_07_mape_todos_zero(self):
        with self.assertRaises(ValueError):
            calcular_metrica(
                [0, 0],
                [1, 2],
            )

    def test_08_tamanhos_diferentes(self):
        with self.assertRaises(ValueError):
            calcular_metrica(
                [1, 2],
                [1],
            )

    def test_09_metricas_finitas(self):
        valores = self.metricas[
            ["MAE", "RMSE", "MAPE"]
        ].to_numpy()

        self.assertTrue(
            np.isfinite(valores).all()
        )

        self.assertTrue(
            (valores >= 0).all()
        )

    def test_10_dois_modelos(self):
        self.assertEqual(
            self.metricas["modelo"].tolist(),
            ["Baseline", "ARIMA(1,1,1)"],
        )

    def test_11_residuos_60(self):
        self.assertEqual(
            len(self.residuos),
            60,
        )

    def test_12_formula_residuos(self):
        esperado = (
            self.teste["demanda"]
            - self.teste["previsao_arima"]
        )

        self.assertTrue(
            np.allclose(
                self.residuos["residuo_arima"],
                esperado,
            )
        )

    def test_13_graficos(self):
        fig_metricas = grafico_metricas(
            self.metricas
        )

        fig_residuos = grafico_residuos(
            self.residuos
        )

        self.assertEqual(
            len(fig_metricas.data),
            3,
        )

        self.assertEqual(
            len(fig_residuos.data),
            1,
        )

    def test_14_arquivos_e_relatorio(self):
        for arquivo in (
            CSV_PREVISOES,
            CSV_METRICAS,
            CSV_RESIDUOS,
            JSON_RELATORIO,
            HTML_METRICAS,
            HTML_RESIDUOS,
        ):
            self.assertTrue(arquivo.is_file())
            self.assertGreater(
                arquivo.stat().st_size,
                0,
            )

        tabela_salva = pd.read_csv(
            CSV_METRICAS
        )

        self.assertEqual(
            len(tabela_salva),
            2,
        )

        relatorio = json.loads(
            JSON_RELATORIO.read_text(
                encoding="utf-8"
            )
        )

        self.assertEqual(
            relatorio["aula"],
            11,
        )

        self.assertFalse(
            relatorio["novo_treinamento_arima"]
        )

        self.assertIn(
            relatorio["melhor_modelo_por_mape"],
            ["Baseline", "ARIMA(1,1,1)"],
        )


if __name__ == "__main__":
    unittest.main()
