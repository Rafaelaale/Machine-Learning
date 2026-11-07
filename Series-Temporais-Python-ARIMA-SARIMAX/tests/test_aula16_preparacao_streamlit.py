"""Testes da Aula 16 - dados para Streamlit."""

import json
import unittest

import numpy as np
import pandas as pd

from src.aula16_preparacao_streamlit import (
    carregar_arquivos,
    validar_dados,
    selecionar_melhor_modelo,
    criar_resumo,
    grafico_historico,
    grafico_previsoes,
    ARQUIVO_HISTORICO,
    ARQUIVO_METRICAS,
    ARQUIVO_PREVISOES,
    ARQUIVO_RESUMO,
    ARQUIVO_RELATORIO,
    GRAFICO_HISTORICO,
    GRAFICO_MODELOS,
)


class TestAula16(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        (
            cls.historico,
            cls.metricas,
            cls.previsoes,
            cls.relatorio_anterior,
        ) = carregar_arquivos()

        cls.resumo = criar_resumo(
            cls.historico,
            cls.metricas,
            cls.previsoes,
        )

    def test_01_historico_456(self):
        self.assertEqual(len(self.historico), 456)

    def test_02_colunas_historico(self):
        self.assertEqual(
            self.historico.columns.tolist(),
            ["data_hora", "demanda"],
        )

    def test_03_quatro_modelos(self):
        self.assertEqual(len(self.metricas), 4)

    def test_04_metricas_completas(self):
        self.assertTrue(
            set(["modelo", "MAE", "RMSE", "MAPE"])
            .issubset(self.metricas.columns)
        )

    def test_05_previsoes_60(self):
        self.assertEqual(len(self.previsoes), 60)

    def test_06_seis_colunas_previsoes(self):
        self.assertEqual(
            len(self.previsoes.columns),
            6,
        )

    def test_07_datas_unicas(self):
        self.assertTrue(
            self.historico["data_hora"].is_unique
        )
        self.assertTrue(
            self.previsoes["data_hora"].is_unique
        )

    def test_08_valores_finitos(self):
        self.assertTrue(
            np.isfinite(
                self.metricas[
                    ["MAE", "RMSE", "MAPE"]
                ].to_numpy()
            ).all()
        )

    def test_09_validacao_completa(self):
        self.assertTrue(
            validar_dados(
                self.historico,
                self.metricas,
                self.previsoes,
            )
        )

    def test_10_melhor_por_mape(self):
        melhor = selecionar_melhor_modelo(
            self.metricas
        )

        self.assertAlmostEqual(
            float(melhor["MAPE"]),
            float(self.metricas["MAPE"].min()),
        )

    def test_11_resumo_uma_linha(self):
        self.assertEqual(len(self.resumo), 1)

    def test_12_dias_historico(self):
        self.assertEqual(
            int(self.resumo.iloc[0]["dias_historico"]),
            456,
        )

    def test_13_dias_teste(self):
        self.assertEqual(
            int(self.resumo.iloc[0]["dias_teste"]),
            60,
        )

    def test_14_graficos(self):
        self.assertEqual(
            len(grafico_historico(self.historico).data),
            1,
        )

        self.assertEqual(
            len(grafico_previsoes(self.previsoes).data),
            5,
        )

    def test_15_quatro_csvs(self):
        for arquivo in (
            ARQUIVO_HISTORICO,
            ARQUIVO_METRICAS,
            ARQUIVO_PREVISOES,
            ARQUIVO_RESUMO,
        ):
            self.assertTrue(arquivo.is_file())
            self.assertGreater(
                arquivo.stat().st_size,
                0,
            )

    def test_16_relatorio_e_graficos(self):
        for arquivo in (
            ARQUIVO_RELATORIO,
            GRAFICO_HISTORICO,
            GRAFICO_MODELOS,
        ):
            self.assertTrue(arquivo.is_file())
            self.assertGreater(
                arquivo.stat().st_size,
                0,
            )

        relatorio = json.loads(
            ARQUIVO_RELATORIO.read_text(
                encoding="utf-8"
            )
        )

        self.assertEqual(
            relatorio["aula"],
            16,
        )

        self.assertFalse(
            relatorio["modelos_treinados_novamente"]
        )

        self.assertEqual(
            relatorio["observacoes_teste"],
            60,
        )


if __name__ == "__main__":
    unittest.main()
