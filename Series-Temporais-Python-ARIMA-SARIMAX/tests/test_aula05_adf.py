"""Testes automatizados da Aula 05."""

import json
import unittest

import numpy as np
import pandas as pd

from src.aula05_adf import (
    carregar_serie_diaria,
    teste_adf,
    extrair_metrica,
    interpretar_adf,
    CSV_ADF,
    JSON_ADF,
)


class TestAula05(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.df = carregar_serie_diaria()
        cls.resultado = teste_adf(cls.df["demanda"])

    def test_01_serie_carregada(self):
        self.assertGreater(len(self.df), 100)

    def test_02_demanda_presente(self):
        self.assertIn("demanda", self.df.columns)

    def test_03_colunas_tabela(self):
        self.assertEqual(
            self.resultado.columns.tolist(),
            ["metrica", "valor"],
        )

    def test_04_estatistica_adf(self):
        self.assertTrue(np.isfinite(
            extrair_metrica(self.resultado, "estatistica_adf")
        ))

    def test_05_p_valor_valido(self):
        p = extrair_metrica(self.resultado, "p_valor")
        self.assertGreaterEqual(p, 0)
        self.assertLessEqual(p, 1)

    def test_06_lags(self):
        self.assertGreaterEqual(
            extrair_metrica(self.resultado, "lags_utilizados"),
            0,
        )

    def test_07_observacoes(self):
        self.assertGreater(
            extrair_metrica(self.resultado, "observacoes"),
            0,
        )

    def test_08_valor_critico_1(self):
        self.assertIn(
            "valor_critico_1%",
            self.resultado["metrica"].tolist(),
        )

    def test_09_valor_critico_5(self):
        self.assertIn(
            "valor_critico_5%",
            self.resultado["metrica"].tolist(),
        )

    def test_10_valor_critico_10(self):
        self.assertIn(
            "valor_critico_10%",
            self.resultado["metrica"].tolist(),
        )

    def test_11_sete_metricas(self):
        self.assertEqual(len(self.resultado), 7)

    def test_12_serie_com_nulos(self):
        serie = self.df["demanda"].copy()
        serie.iloc[0] = np.nan
        resultado = teste_adf(serie)
        self.assertEqual(len(resultado), 7)

    def test_13_serie_constante(self):
        with self.assertRaises(ValueError):
            teste_adf(pd.Series([1] * 30))

    def test_14_interpretacao(self):
        resposta = interpretar_adf(self.resultado)
        self.assertIn(
            resposta["decisao"],
            ["Rejeitar H0", "Nao rejeitar H0"],
        )
        self.assertEqual(resposta["alfa"], 0.05)

    def test_15_interpretacao_limiar(self):
        tabela = self.resultado.copy()
        tabela.loc[
            tabela["metrica"] == "p_valor", "valor"
        ] = 0.05
        self.assertEqual(
            interpretar_adf(tabela)["decisao"],
            "Rejeitar H0",
        )

        tabela.loc[
            tabela["metrica"] == "p_valor", "valor"
        ] = 0.06
        self.assertEqual(
            interpretar_adf(tabela)["decisao"],
            "Nao rejeitar H0",
        )

    def test_16_arquivos_salvos(self):
        self.assertTrue(CSV_ADF.is_file())
        self.assertTrue(JSON_ADF.is_file())

        salvo = pd.read_csv(CSV_ADF)
        self.assertEqual(len(salvo), 7)

        with JSON_ADF.open(encoding="utf-8") as arquivo:
            relatorio = json.load(arquivo)

        self.assertEqual(relatorio["aula"], 5)
        self.assertFalse(relatorio["diferenciacao_aplicada"])
        self.assertFalse(relatorio["modelo_treinado"])


if __name__ == "__main__":
    unittest.main()
