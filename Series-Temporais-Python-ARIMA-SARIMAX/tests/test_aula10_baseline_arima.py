"""Testes da Aula 10 - baseline e ARIMA."""

import json
import unittest

import numpy as np
import pandas as pd

from src.aula10_baseline_arima import (
    carregar_divisao,
    criar_baseline,
    grafico_comparacao,
    grafico_historico,
    CSV_PREVISOES,
    JSON_RELATORIO,
    TXT_RESUMO,
    HTML_COMPARACAO,
    HTML_HISTORICO,
)


class TestAula10(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.serie, cls.treino, cls.teste = (
            carregar_divisao()
        )

        cls.baseline, cls.ultimo = (
            criar_baseline(
                cls.treino,
                cls.teste,
            )
        )

        cls.previsoes = pd.read_csv(
            CSV_PREVISOES,
            parse_dates=["data_hora"],
        )

    def test_01_treino_e_teste(self):
        self.assertGreater(
            len(self.treino),
            0,
        )
        self.assertEqual(
            len(self.teste),
            60,
        )

    def test_02_sem_vazamento_temporal(self):
        self.assertLess(
            self.treino["data_hora"].max(),
            self.teste["data_hora"].min(),
        )

    def test_03_ultimo_valor(self):
        self.assertEqual(
            self.ultimo,
            self.treino["demanda"].iloc[-1],
        )

    def test_04_baseline_constante(self):
        self.assertTrue(
            (
                self.baseline["previsao_baseline"]
                == self.ultimo
            ).all()
        )

    def test_05_60_previsoes(self):
        self.assertEqual(
            len(self.previsoes),
            60,
        )

    def test_06_colunas(self):
        for coluna in (
            "data_hora",
            "demanda",
            "previsao_baseline",
            "previsao_arima",
        ):
            self.assertIn(
                coluna,
                self.previsoes.columns,
            )

    def test_07_datas_corretas(self):
        self.assertEqual(
            self.previsoes["data_hora"].tolist(),
            self.teste["data_hora"].tolist(),
        )

    def test_08_demanda_real_preservada(self):
        self.assertTrue(
            np.allclose(
                self.previsoes["demanda"],
                self.teste["demanda"],
            )
        )

    def test_09_previsoes_finitas(self):
        self.assertTrue(
            np.isfinite(
                self.previsoes["previsao_arima"]
            ).all()
        )

    def test_10_grafico_comparacao(self):
        figura = grafico_comparacao(
            self.previsoes
        )
        self.assertEqual(
            len(figura.data),
            3,
        )

    def test_11_grafico_historico(self):
        figura = grafico_historico(
            self.treino,
            self.previsoes,
        )
        self.assertEqual(
            len(figura.data),
            4,
        )

    def test_12_arquivos_e_relatorio(self):
        for caminho in (
            CSV_PREVISOES,
            JSON_RELATORIO,
            TXT_RESUMO,
            HTML_COMPARACAO,
            HTML_HISTORICO,
        ):
            self.assertTrue(
                caminho.is_file(),
                str(caminho),
            )
            self.assertGreater(
                caminho.stat().st_size,
                0,
            )

        relatorio = json.loads(
            JSON_RELATORIO.read_text(
                encoding="utf-8"
            )
        )

        self.assertEqual(
            relatorio["ordem"],
            [1, 1, 1],
        )

        self.assertTrue(
            relatorio["treinamento_realizado"]
        )

        self.assertFalse(
            relatorio["metricas_de_erro_calculadas"]
        )


if __name__ == "__main__":
    unittest.main()
