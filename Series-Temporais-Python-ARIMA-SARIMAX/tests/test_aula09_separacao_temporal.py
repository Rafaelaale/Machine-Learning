"""Testes da Aula 09 - divisao temporal para ARIMA."""

import json
import unittest

import pandas as pd

from src.aula09_separacao_temporal import (
    preparar_serie,
    separar_treino_teste,
    diagnosticar_calendario,
    grafico_serie_modelagem,
    grafico_treino_teste,
    CSV_MODELAGEM,
    CSV_TREINO,
    CSV_TESTE,
    JSON_RELATORIO,
    HTML_SERIE,
    HTML_DIVISAO,
)


class TestAula09(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.serie = preparar_serie()
        cls.treino, cls.teste = separar_treino_teste(
            cls.serie,
            tamanho_teste=60,
        )

    def test_01_colunas(self):
        self.assertEqual(
            self.serie.columns.tolist(),
            ["data_hora", "demanda"],
        )

    def test_02_datas_datetime(self):
        self.assertTrue(
            pd.api.types.is_datetime64_any_dtype(
                self.serie["data_hora"]
            )
        )

    def test_03_ordenacao(self):
        self.assertTrue(
            self.serie["data_hora"].is_monotonic_increasing
        )

    def test_04_datas_unicas(self):
        self.assertTrue(
            self.serie["data_hora"].is_unique
        )

    def test_05_sessenta_observacoes(self):
        self.assertEqual(len(self.teste), 60)

    def test_06_tamanho_total(self):
        self.assertEqual(
            len(self.treino) + len(self.teste),
            len(self.serie),
        )

    def test_07_treino_antes_teste(self):
        self.assertLess(
            self.treino["data_hora"].max(),
            self.teste["data_hora"].min(),
        )

    def test_08_treino_inicio(self):
        self.assertEqual(
            self.treino["data_hora"].iloc[0],
            self.serie["data_hora"].iloc[0],
        )

    def test_09_teste_final(self):
        self.assertEqual(
            self.teste["data_hora"].iloc[-1],
            self.serie["data_hora"].iloc[-1],
        )

    def test_10_tamanho_invalido(self):
        for tamanho in (0, -1, len(self.serie)):
            with self.assertRaises(ValueError):
                separar_treino_teste(
                    self.serie,
                    tamanho_teste=tamanho,
                )

    def test_11_graficos_e_calendario(self):
        grafico1 = grafico_serie_modelagem(
            self.serie
        )

        grafico2 = grafico_treino_teste(
            self.treino,
            self.teste,
        )

        self.assertEqual(len(grafico1.data), 1)
        self.assertEqual(len(grafico2.data), 2)

        diagnostico = diagnosticar_calendario(
            self.serie,
            self.treino,
            self.teste,
        )

        self.assertTrue(
            diagnostico["teste_pos_treino"]
        )

        self.assertEqual(
            diagnostico["observacoes_teste"],
            60,
        )

    def test_12_arquivos_salvos(self):
        for caminho in (
            CSV_MODELAGEM,
            CSV_TREINO,
            CSV_TESTE,
            JSON_RELATORIO,
            HTML_SERIE,
            HTML_DIVISAO,
        ):
            self.assertTrue(
                caminho.is_file(),
                str(caminho),
            )
            self.assertGreater(
                caminho.stat().st_size,
                0,
            )

        tabela_treino = pd.read_csv(CSV_TREINO)
        tabela_teste = pd.read_csv(CSV_TESTE)

        self.assertEqual(
            len(tabela_treino),
            len(self.treino),
        )

        self.assertEqual(
            len(tabela_teste),
            60,
        )

        relatorio = json.loads(
            JSON_RELATORIO.read_text(
                encoding="utf-8"
            )
        )

        self.assertEqual(relatorio["aula"], 9)
        self.assertFalse(
            relatorio["modelo_treinado"]
        )


if __name__ == "__main__":
    unittest.main()
