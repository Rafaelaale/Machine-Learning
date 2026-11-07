"""Testes da Aula 02."""
import unittest
import pandas as pd

from src.preparacao_bikes import (
    carregar_base, preparar_base, SAIDA, GRAFICO, RELATORIO,
)


class TestAula02(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = carregar_base()
        cls.temporal = preparar_base(cls.original)

    def test_registros(self):
        self.assertEqual(len(self.original), 10886)

    def test_colunas_originais(self):
        self.assertEqual(len(self.original.columns), 12)

    def test_datetime(self):
        self.assertIsInstance(
            self.temporal.index, pd.DatetimeIndex
        )

    def test_ordenacao(self):
        self.assertTrue(
            self.temporal.index.is_monotonic_increasing
        )

    def test_indice_unico(self):
        self.assertTrue(self.temporal.index.is_unique)

    def test_demanda(self):
        self.assertIn("demanda", self.temporal.columns)

    def test_calendario(self):
        for nome in ("ano", "mes", "dia", "hora", "dia_semana"):
            self.assertIn(nome, self.temporal.columns)

    def test_arquivos(self):
        for caminho in (SAIDA, GRAFICO, RELATORIO):
            self.assertTrue(caminho.is_file())


if __name__ == "__main__":
    unittest.main()
