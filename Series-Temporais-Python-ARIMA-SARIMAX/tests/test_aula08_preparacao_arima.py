"""Testes da Aula 08 - fundamentos ARIMA."""

import json
import unittest

import pandas as pd

from src.aula08_preparacao_arima import (
    criar_parametros_iniciais,
    explicar_componentes,
    consultar_evidencias,
    CSV_PARAMETROS,
    JSON_RELATORIO,
)


class TestAula08(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.tabela = criar_parametros_iniciais()
        cls.componentes = explicar_componentes()

    def test_01_tres_parametros(self):
        self.assertEqual(len(self.tabela), 3)

    def test_02_ordem_parametros(self):
        self.assertEqual(
            self.tabela["parametro"].tolist(),
            ["p", "d", "q"],
        )

    def test_03_colunas(self):
        self.assertEqual(
            self.tabela.columns.tolist(),
            ["parametro", "ideia", "Ponto de partida"],
        )

    def test_04_parametro_p(self):
        linha = self.tabela.iloc[0]
        self.assertEqual(linha["parametro"], "p")
        self.assertEqual(
            linha["Ponto de partida"],
            "Avaliar pela PACF",
        )

    def test_05_parametro_d(self):
        linha = self.tabela.iloc[1]
        self.assertEqual(linha["parametro"], "d")
        self.assertEqual(linha["Ponto de partida"], "1")

    def test_06_parametro_q(self):
        linha = self.tabela.iloc[2]
        self.assertEqual(linha["parametro"], "q")
        self.assertEqual(
            linha["Ponto de partida"],
            "Avaliar pela ACF",
        )

    def test_07_componentes_presentes(self):
        self.assertEqual(
            set(self.componentes),
            {"AR", "MA", "ARMA", "ARIMA"},
        )

    def test_08_conceito_ar(self):
        self.assertEqual(
            self.componentes["AR"]["parametro"],
            "p",
        )

    def test_09_conceito_ma(self):
        self.assertEqual(
            self.componentes["MA"]["parametro"],
            "q",
        )

    def test_10_conceito_arima(self):
        self.assertEqual(
            self.componentes["ARIMA"]["parametros"],
            ["p", "d", "q"],
        )

    def test_11_evidencias(self):
        evidencias = consultar_evidencias()

        self.assertEqual(
            evidencias["d_inicial"],
            1,
        )

        self.assertIsNone(
            evidencias["p_definitivo"]
        )

        self.assertIsNone(
            evidencias["q_definitivo"]
        )

    def test_12_arquivos_salvos(self):
        self.assertTrue(CSV_PARAMETROS.is_file())
        self.assertTrue(JSON_RELATORIO.is_file())

        tabela_salva = pd.read_csv(
            CSV_PARAMETROS,
            dtype={"Ponto de partida": str},
        )

        self.assertEqual(
            tabela_salva["parametro"].tolist(),
            ["p", "d", "q"],
        )

        relatorio = json.loads(
            JSON_RELATORIO.read_text(encoding="utf-8")
        )

        self.assertEqual(relatorio["aula"], 8)
        self.assertFalse(relatorio["modelo_treinado"])
        self.assertFalse(relatorio["previsoes_geradas"])


if __name__ == "__main__":
    unittest.main()
