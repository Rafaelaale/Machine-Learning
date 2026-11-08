"""Testes de dados sinteticos e pipeline."""

import unittest

import numpy as np
import pandas as pd

from sklearn.linear_model import LogisticRegression

from src.aula03_ambiente_dataset import (
    gerar_base_credito,
    preparar_divisao,
    construir_pipeline,
    FEATURES,
    TARGET,
    NUM_COLS,
    CAT_COLS,
    DADOS,
    RESULTADOS,
    GRAFICOS,
)


class TestAula03(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.df = gerar_base_credito(6000)

        (
            cls.X_train,
            cls.X_test,
            cls.y_train,
            cls.y_test,
        ) = preparar_divisao(cls.df)

        cls.pipeline = construir_pipeline()

    def test_01_base(self):
        self.assertEqual(
            self.df.shape,
            (6000, 9),
        )

    def test_02_alvo(self):
        self.assertEqual(
            TARGET,
            "inadimplente",
        )

    def test_03_features(self):
        self.assertEqual(
            len(FEATURES),
            8,
        )

    def test_04_numericas(self):
        self.assertEqual(
            len(NUM_COLS),
            6,
        )

    def test_05_categoricas(self):
        self.assertEqual(
            len(CAT_COLS),
            2,
        )

    def test_06_classes(self):
        self.assertEqual(
            set(self.df[TARGET]),
            {0, 1},
        )

    def test_07_reprodutibilidade(self):
        outra = gerar_base_credito(6000)
        pd.testing.assert_frame_equal(
            self.df,
            outra,
        )

    def test_08_treino(self):
        self.assertEqual(
            self.X_train.shape,
            (4500, 8),
        )

    def test_09_teste(self):
        self.assertEqual(
            self.X_test.shape,
            (1500, 8),
        )

    def test_10_estratificacao(self):
        geral = self.df[TARGET].mean()
        treino = self.y_train.mean()
        teste = self.y_test.mean()

        self.assertLess(
            abs(geral - treino),
            0.002,
        )

        self.assertLess(
            abs(geral - teste),
            0.002,
        )

    def test_11_regressao_logistica(self):
        self.assertIsInstance(
            self.pipeline.named_steps["model"],
            LogisticRegression,
        )

    def test_12_class_weight(self):
        self.assertEqual(
            self.pipeline.named_steps["model"].class_weight,
            "balanced",
        )

    def test_13_nao_treinado(self):
        self.assertFalse(
            hasattr(
                self.pipeline.named_steps["model"],
                "coef_",
            )
        )

    def test_14_sem_vazamento(self):
        self.assertFalse(
            hasattr(
                self.pipeline.named_steps["prep"],
                "transformers_",
            )
        )

    def test_15_sem_nulos(self):
        self.assertFalse(
            self.df.isna().any().any()
        )

    def test_16_dados_salvos(self):
        for nome in (
            "aula03_base_credito_sintetica.csv",
            "aula03_treino_credito.csv",
            "aula03_teste_credito.csv",
        ):
            self.assertTrue(
                (DADOS / nome).is_file()
            )

    def test_17_relatorio(self):
        self.assertTrue(
            (
                RESULTADOS
                / "aula03_ambiente_dataset.json"
            ).is_file()
        )

    def test_18_graficos(self):
        for nome in (
            "aula03_distribuicao_classes.png",
            "aula03_score_por_classe.png",
            "aula03_renda_por_classe.png",
        ):
            self.assertTrue(
                (GRAFICOS / nome).is_file()
            )


if __name__ == "__main__":
    unittest.main()
