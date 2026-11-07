"""Testes da Aula 12 - preparacao SARIMA."""

import json
import unittest

import pandas as pd

from src.aula12_preparacao_sarima import (
    carregar_serie_diaria,
    preparar_treino_teste,
    verificar_divisao_anterior,
    investigar_calendario,
    grafico_demanda,
    grafico_divisao,
    CSV_SERIE,
    CSV_TREINO,
    CSV_TESTE,
    CSV_CALENDARIO,
    JSON_RELATORIO,
    HTML_SERIE,
    HTML_DIVISAO,
)


class TestAula12(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.serie = carregar_serie_diaria()
        cls.treino, cls.teste = preparar_treino_teste(
            cls.serie
        )

        cls.diagnostico, cls.ausentes = (
            investigar_calendario(
                cls.serie,
                cls.treino,
                cls.teste,
            )
        )

    def test_01_colunas(self):
        self.assertEqual(
            self.serie.columns.tolist(),
            ["data_hora", "demanda"],
        )

    def test_02_total_observacoes(self):
        self.assertEqual(
            len(self.serie),
            456,
        )

    def test_03_tamanho_treino(self):
        self.assertEqual(
            len(self.treino),
            396,
        )

    def test_04_tamanho_teste(self):
        self.assertEqual(
            len(self.teste),
            60,
        )

    def test_05_preservacao_total(self):
        self.assertEqual(
            len(self.treino) + len(self.teste),
            len(self.serie),
        )

    def test_06_datas_ordenadas(self):
        self.assertTrue(
            self.serie[
                "data_hora"
            ].is_monotonic_increasing
        )

    def test_07_datas_unicas(self):
        self.assertTrue(
            self.serie["data_hora"].is_unique
        )

    def test_08_treino_antes_teste(self):
        self.assertLess(
            self.treino["data_hora"].max(),
            self.teste["data_hora"].min(),
        )

    def test_09_divisao_igual_arima(self):
        self.assertTrue(
            verificar_divisao_anterior(
                self.treino,
                self.teste,
            )
        )

    def test_10_serie_sem_nulos(self):
        self.assertFalse(
            self.serie.isna().any().any()
        )

    def test_11_calendario(self):
        self.assertEqual(
            self.diagnostico[
                "observacoes_teste"
            ],
            60,
        )

        self.assertEqual(
            self.diagnostico[
                "ciclo_semanal_a_investigar"
            ],
            7,
        )

    def test_12_grafico_serie(self):
        fig = grafico_demanda(
            self.serie
        )

        self.assertEqual(len(fig.data), 1)

    def test_13_grafico_divisao(self):
        fig = grafico_divisao(
            self.treino,
            self.teste,
        )

        self.assertEqual(len(fig.data), 2)

    def test_14_arquivos_salvos(self):
        for arquivo in (
            CSV_SERIE,
            CSV_TREINO,
            CSV_TESTE,
            CSV_CALENDARIO,
            JSON_RELATORIO,
            HTML_SERIE,
            HTML_DIVISAO,
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
            12,
        )

        self.assertFalse(
            relatorio["sarima_treinado"]
        )

        self.assertFalse(
            relatorio["ciclo_semanal_validado"]
        )


if __name__ == "__main__":
    unittest.main()
