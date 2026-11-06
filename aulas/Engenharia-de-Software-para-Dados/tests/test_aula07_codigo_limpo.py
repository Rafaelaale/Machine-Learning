"""Testes do pipeline limpo da Aula 07."""

import sys
import unittest
from pathlib import Path

import pandas as pd


BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from src.aula07_churn_limpo import (
    COLUNAS_MODELO,
    avaliar_modelo,
    carregar_clientes,
    executar_pipeline,
    preparar_dados,
    separar_treino_teste,
    treinar_regressao_logistica,
)


class TestCodigoLimpoChurn(unittest.TestCase):

    def setUp(self):
        self.clientes = pd.DataFrame({
            "total_spent": [
                100, 200, 300, 400, 500, 600, 700, 800,
            ],
            "num_orders": [1, 2, 1, 2, 7, 8, 7, 8],
            "days_since_last_purchase": [
                90, 80, 70, 60, 5, 10, 15, 20,
            ],
            "churn": [1, 1, 1, 1, 0, 0, 0, 0],
        })

    def test_01_preparacao(self):
        dados = preparar_dados(self.clientes)
        self.assertEqual(len(dados), 8)

    def test_02_atributos(self):
        self.assertEqual(len(COLUNAS_MODELO), 3)

    def test_03_coluna_ausente(self):
        incompleto = self.clientes.drop(columns=["churn"])

        with self.assertRaises(ValueError):
            preparar_dados(incompleto)

    def test_04_preserva_dataframe(self):
        original = self.clientes.copy(deep=True)

        preparar_dados(self.clientes)

        pd.testing.assert_frame_equal(
            self.clientes, original
        )

    def test_05_valores_ausentes(self):
        dados = self.clientes.copy()
        dados.loc[0, "total_spent"] = None

        resultado = preparar_dados(dados)

        self.assertEqual(len(resultado), 7)

    def test_06_divisao_reproduzivel(self):
        dados = preparar_dados(self.clientes)

        primeira = separar_treino_teste(dados)
        segunda = separar_treino_teste(dados)

        pd.testing.assert_frame_equal(
            primeira[0], segunda[0]
        )

    def test_07_proporcao_invalida(self):
        dados = preparar_dados(self.clientes)

        with self.assertRaises(ValueError):
            separar_treino_teste(
                dados, proporcao_teste=1.0
            )

    def test_08_treinamento_e_avaliacao(self):
        dados = preparar_dados(self.clientes)

        x_treino, x_teste, y_treino, y_teste = (
            separar_treino_teste(dados)
        )

        modelo = treinar_regressao_logistica(
            x_treino, y_treino
        )

        metricas = avaliar_modelo(
            modelo, x_teste, y_teste
        )

        self.assertIn("accuracy", metricas)

    def test_09_pipeline_completo(self):
        resultado = executar_pipeline(self.clientes)

        self.assertEqual(
            resultado["registros_utilizados"], 8
        )

        self.assertIn("metricas", resultado)

    def test_10_alvo_textual(self):
        dados = self.clientes.copy()

        dados["churn"] = dados["churn"].map({
            1: "Yes",
            0: "No",
        })

        resultado = preparar_dados(dados)

        self.assertEqual(
            set(resultado["churn"].unique()),
            {0, 1},
        )


if __name__ == "__main__":
    unittest.main()