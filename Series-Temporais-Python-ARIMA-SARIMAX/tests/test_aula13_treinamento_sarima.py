"""Testes automatizados da Aula 13."""

import json
import unittest

import numpy as np
import pandas as pd

from statsmodels.tsa.statespace.sarimax import (
    SARIMAXResults,
)

from src.aula13_treinamento_sarima import (
    carregar_dados,
    verificar_calendario,
    calcular_resultados,
    grafico_previsoes,
    grafico_mape,
    grafico_residuos,
    ORDEM_SARIMA,
    ORDEM_SAZONAL,
    CSV_PREVISOES,
    CSV_METRICAS,
    CSV_COMPARACAO,
    CSV_RESIDUOS,
    JSON_RELATORIO,
    TXT_RESUMO,
    ARQUIVO_MODELO,
    HTML_PREVISOES,
    HTML_MAPE,
    HTML_RESIDUOS,
)


class TestAula13(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.treino, cls.teste = carregar_dados()

        cls.previsoes = pd.read_csv(
            CSV_PREVISOES,
            parse_dates=["data_hora"],
        )

        cls.metricas, cls.comparacao, cls.residuos = (
            calcular_resultados(cls.previsoes)
        )

    def test_01_ordem_nao_sazonal(self):
        self.assertEqual(
            ORDEM_SARIMA,
            (1, 1, 1),
        )

    def test_02_ordem_sazonal(self):
        self.assertEqual(
            ORDEM_SAZONAL,
            (1, 0, 1, 7),
        )

    def test_03_treino(self):
        self.assertEqual(
            len(self.treino),
            396,
        )

    def test_04_teste(self):
        self.assertEqual(
            len(self.teste),
            60,
        )

    def test_05_ausencia_vazamento(self):
        self.assertLess(
            self.treino["data_hora"].max(),
            self.teste["data_hora"].min(),
        )

    def test_06_colunas_previsoes(self):
        self.assertEqual(
            self.previsoes.columns.tolist(),
            [
                "data_hora",
                "demanda",
                "previsao_sarima",
            ],
        )

    def test_07_quantidade_previsoes(self):
        self.assertEqual(
            len(self.previsoes),
            60,
        )

    def test_08_previsoes_finitas(self):
        self.assertTrue(
            np.isfinite(
                self.previsoes["previsao_sarima"]
            ).all()
        )

    def test_09_datas_preservadas(self):
        self.assertEqual(
            self.previsoes["data_hora"].tolist(),
            self.teste["data_hora"].tolist(),
        )

    def test_10_demanda_preservada(self):
        np.testing.assert_allclose(
            self.previsoes["demanda"],
            self.teste["demanda"],
        )

    def test_11_metricas_sarima(self):
        self.assertEqual(
            len(self.metricas),
            1,
        )

        self.assertTrue(
            np.isfinite(
                self.metricas[
                    ["MAE", "RMSE", "MAPE"]
                ].to_numpy()
            ).all()
        )

    def test_12_comparacao_modelos(self):
        self.assertEqual(
            len(self.comparacao),
            3,
        )

        self.assertTrue(
            self.comparacao[
                "MAPE"
            ].is_monotonic_increasing
        )

    def test_13_residuos(self):
        esperado = (
            self.previsoes["demanda"]
            - self.previsoes["previsao_sarima"]
        )

        np.testing.assert_allclose(
            self.residuos["residuos_sarima"],
            esperado,
        )

    def test_14_graficos(self):
        self.assertEqual(
            len(grafico_previsoes(self.previsoes).data),
            2,
        )

        self.assertEqual(
            len(grafico_mape(self.comparacao).data),
            1,
        )

        self.assertEqual(
            len(grafico_residuos(self.residuos).data),
            1,
        )

    def test_15_calendario(self):
        diagnostico = verificar_calendario(
            self.treino,
            self.teste,
        )

        self.assertEqual(
            diagnostico["ciclo_sazonal"],
            7,
        )

        self.assertGreaterEqual(
            diagnostico["datas_ausentes"],
            0,
        )

    def test_16_arquivos_e_relatorio(self):
        for arquivo in (
            CSV_PREVISOES,
            CSV_METRICAS,
            CSV_COMPARACAO,
            CSV_RESIDUOS,
            JSON_RELATORIO,
            TXT_RESUMO,
            ARQUIVO_MODELO,
            HTML_PREVISOES,
            HTML_MAPE,
            HTML_RESIDUOS,
        ):
            self.assertTrue(
                arquivo.is_file(),
                str(arquivo),
            )

            self.assertGreater(
                arquivo.stat().st_size,
                0,
            )

        relatorio = json.loads(
            JSON_RELATORIO.read_text(
                encoding="utf-8"
            )
        )

        self.assertEqual(
            relatorio["aula"],
            13,
        )

        self.assertEqual(
            relatorio["ordem_sazonal"],
            [1, 0, 1, 7],
        )

        self.assertFalse(
            relatorio["variaveis_exogenas_utilizadas"]
        )


if __name__ == "__main__":
    unittest.main()
