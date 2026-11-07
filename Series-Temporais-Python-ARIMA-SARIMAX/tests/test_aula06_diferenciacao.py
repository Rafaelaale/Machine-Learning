"""Testes da Aula 06 - primeira diferenciacao e ADF."""

import json
import unittest

import numpy as np
import pandas as pd

from src.aula04_decomposicao import carregar_serie_diaria

from src.aula06_diferenciacao import (
    aplicar_diferenciacao,
    executar_comparacao_adf,
    criar_grafico,
    CSV_DIFERENCIADA,
    CSV_ADF_DIFERENCIADO,
    CSV_COMPARACAO,
    JSON_RELATORIO,
    HTML_GRAFICO,
)


class TestAula06(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.base = carregar_serie_diaria()
        cls.original, cls.diff = aplicar_diferenciacao(
            cls.base
        )
        cls.adf1, cls.adf2, cls.comparacao = (
            executar_comparacao_adf(
                cls.original,
                cls.diff,
            )
        )

    def test_01_coluna_diferenca(self):
        self.assertIn(
            "demanda_diff",
            self.original.columns,
        )

    def test_02_primeiro_nan(self):
        self.assertTrue(
            pd.isna(
                self.original["demanda_diff"].iloc[0]
            )
        )

    def test_03_uma_linha_removida(self):
        self.assertEqual(
            len(self.diff),
            len(self.original) - 1,
        )

    def test_04_sem_nan_diferenciado(self):
        self.assertFalse(
            self.diff["demanda_diff"].isna().any()
        )

    def test_05_primeira_diferenca(self):
        esperado = (
            self.original["demanda"].iloc[1]
            - self.original["demanda"].iloc[0]
        )
        self.assertEqual(
            self.diff["demanda_diff"].iloc[0],
            esperado,
        )

    def test_06_diferencas_manuais(self):
        esperado = (
            self.original["demanda"].diff()
            .dropna().to_numpy()
        )
        self.assertTrue(
            np.array_equal(
                esperado,
                self.diff["demanda_diff"].to_numpy(),
            )
        )

    def test_07_soma_telescopica(self):
        self.assertAlmostEqual(
            self.diff["demanda_diff"].sum(),
            self.original["demanda"].iloc[-1]
            - self.original["demanda"].iloc[0],
        )

    def test_08_datas_ordenadas(self):
        self.assertTrue(
            self.diff["data_hora"].is_monotonic_increasing
        )

    def test_09_intervalos_presentes(self):
        self.assertIn(
            "intervalo_dias",
            self.diff.columns,
        )
        self.assertTrue(
            (self.diff["intervalo_dias"] >= 1).all()
        )

    def test_10_resultados_adf(self):
        self.assertEqual(len(self.adf1), 7)
        self.assertEqual(len(self.adf2), 7)

    def test_11_duas_series_comparadas(self):
        self.assertEqual(len(self.comparacao), 2)

    def test_12_p_valores_validos(self):
        self.assertTrue(
            self.comparacao["p_valor"]
            .between(0, 1).all()
        )

    def test_13_decisoes_validas(self):
        validas = {
            "Rejeitar H0",
            "Nao rejeitar H0",
        }
        self.assertTrue(
            set(self.comparacao["decisao"])
            .issubset(validas)
        )

    def test_14_grafico_duas_series(self):
        figura = criar_grafico(self.original)
        self.assertEqual(len(figura.data), 2)

    def test_15_csv_diferenciado(self):
        self.assertTrue(
            CSV_DIFERENCIADA.is_file()
        )
        salvo = pd.read_csv(CSV_DIFERENCIADA)
        self.assertEqual(
            len(salvo),
            len(self.diff),
        )

    def test_16_relatorios_e_grafico(self):
        for arquivo in [
            CSV_ADF_DIFERENCIADO,
            CSV_COMPARACAO,
            JSON_RELATORIO,
            HTML_GRAFICO,
        ]:
            self.assertTrue(
                arquivo.is_file(),
                str(arquivo),
            )

        relatorio = json.loads(
            JSON_RELATORIO.read_text(encoding="utf-8")
        )

        self.assertEqual(
            relatorio["ordem_diferenciacao"],
            1,
        )
        self.assertFalse(
            relatorio["modelo_treinado"]
        )


if __name__ == "__main__":
    unittest.main()
