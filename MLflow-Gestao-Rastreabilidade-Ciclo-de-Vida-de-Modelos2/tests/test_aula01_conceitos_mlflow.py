"""Testes da Aula 01."""

import unittest

from src.aula01_conceitos_mlflow import (
    CONCEITOS,
    validar_conceitos,
    executar,
)


class TestAula01(unittest.TestCase):

    def test_01_numero_aula(self):
        self.assertEqual(CONCEITOS["aula"], 1)

    def test_02_projeto(self):
        self.assertIn("credito", CONCEITOS["projeto"])

    def test_03_criterios(self):
        self.assertEqual(
            len(CONCEITOS["criterios_sucesso"]), 3
        )

    def test_04_rastreabilidade(self):
        self.assertIn(
            "parametros", CONCEITOS["elementos_mlflow"]
        )
        self.assertIn(
            "metricas", CONCEITOS["elementos_mlflow"]
        )

    def test_05_sem_treinamento(self):
        self.assertFalse(CONCEITOS["modelo_treinado"])

    def test_06_sem_dados_inventados(self):
        self.assertFalse(CONCEITOS["dados_carregados"])

    def test_07_validacao(self):
        self.assertTrue(validar_conceitos())

    def test_08_execucao(self):
        resultado = executar()
        self.assertEqual(resultado["aula"], 1)


if __name__ == "__main__":
    unittest.main()
