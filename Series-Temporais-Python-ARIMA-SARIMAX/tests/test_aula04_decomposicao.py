"""Testes da Aula 04 - decomposicao de series temporais."""

import unittest

import numpy as np
import pandas as pd

from src.aula04_decomposicao import (
    CSV_ORIGINAL,
    CSV_DIARIO,
    CSV_COMPONENTES,
    CSV_MEDIA_MOVEL,
    GRAFICO_MEDIA,
    GRAFICO_DECOMPOSICAO,
    RELATORIO,
    carregar_serie_diaria,
    calcular_media_movel,
    verificar_calendario,
    decompor_serie,
    grafico_media_movel,
    grafico_componentes,
)


class TestAula04(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.df = carregar_serie_diaria()
        cls.media = calcular_media_movel(cls.df)
        cls.componentes = decompor_serie(cls.df)
        cls.calendario = verificar_calendario(cls.df)

    def test_01_csv_original(self):
        self.assertTrue(CSV_ORIGINAL.is_file())

    def test_02_serie_diaria(self):
        self.assertTrue(CSV_DIARIO.is_file())

    def test_03_colunas(self):
        self.assertEqual(
            self.df.columns.tolist(),
            ["data_hora", "demanda"],
        )

    def test_04_datas_datetime(self):
        self.assertTrue(
            pd.api.types.is_datetime64_any_dtype(
                self.df["data_hora"]
            )
        )

    def test_05_datas_ordenadas(self):
        self.assertTrue(
            self.df["data_hora"].is_monotonic_increasing
        )

    def test_06_datas_unicas(self):
        self.assertTrue(
            self.df["data_hora"].is_unique
        )

    def test_07_media_movel_primeiros_nan(self):
        self.assertTrue(
            self.media["media_movel_7"].iloc[:6]
            .isna().all()
        )

    def test_08_primeira_media(self):
        esperado = self.df["demanda"].iloc[:7].mean()

        self.assertAlmostEqual(
            self.media["media_movel_7"].iloc[6],
            esperado,
        )

    def test_09_media_nao_e_previsao(self):
        self.assertEqual(
            len(self.media),
            len(self.df),
        )

    def test_10_colunas_componentes(self):
        self.assertEqual(
            self.componentes.columns.tolist(),
            [
                "data",
                "observado",
                "tendencia",
                "sazonalidade",
                "residuo",
            ],
        )

    def test_11_quantidade_componentes(self):
        self.assertEqual(
            len(self.componentes),
            len(self.df),
        )

    def test_12_modelo_aditivo(self):
        dados = self.componentes.dropna()

        reconstrucao = (
            dados["tendencia"]
            + dados["sazonalidade"]
            + dados["residuo"]
        )

        self.assertTrue(
            np.allclose(
                dados["observado"],
                reconstrucao,
            )
        )

    def test_13_nans_nas_extremidades(self):
        self.assertTrue(
            pd.isna(
                self.componentes["tendencia"].iloc[0]
            )
        )

        self.assertTrue(
            pd.isna(
                self.componentes["tendencia"].iloc[-1]
            )
        )

    def test_14_calendario(self):
        self.assertGreaterEqual(
            self.calendario["dias_no_calendario"],
            self.calendario["dias_observados"],
        )

        self.assertEqual(
            self.calendario["dias_sem_observacao"],
            self.calendario["dias_no_calendario"]
            - self.calendario["dias_observados"],
        )

    def test_15_graficos(self):
        fig1 = grafico_media_movel(self.media)
        fig2 = grafico_componentes(self.componentes)

        self.assertEqual(len(fig1.data), 2)
        self.assertEqual(len(fig2.data), 4)

    def test_16_arquivos_gerados(self):
        for arquivo in [
            CSV_MEDIA_MOVEL,
            CSV_COMPONENTES,
            GRAFICO_MEDIA,
            GRAFICO_DECOMPOSICAO,
            RELATORIO,
        ]:
            self.assertTrue(
                arquivo.is_file(),
                str(arquivo),
            )


if __name__ == "__main__":
    unittest.main()
