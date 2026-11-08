"""Testes da primeira run MLflow."""

import json
import unittest

import numpy as np
import pandas as pd

from mlflow.tracking import MlflowClient
from sklearn.linear_model import LogisticRegression

from src.aula04_primeira_run_mlflow import (
    configurar_tracking,
    carregar_dados,
    novo_cliente,
    verificar_run_anterior,
    construir_pipeline,
    EXPERIMENTO,
    NOME_RUN,
    ARQUIVO_RELATORIO,
    ARQUIVO_PREVISOES,
    ARQUIVO_CLASSIFICACAO,
)


class TestAula04(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        configurar_tracking()

        cls.relatorio = json.loads(
            ARQUIVO_RELATORIO.read_text(
                encoding="utf-8"
            )
        )

    def test_01_experimento(self):
        self.assertEqual(
            self.relatorio["experimento"],
            EXPERIMENTO,
        )

    def test_02_nome_run(self):
        self.assertEqual(
            self.relatorio["nome_run"],
            NOME_RUN,
        )

    def test_03_run_id(self):
        self.assertEqual(
            len(self.relatorio["run_id"]),
            32,
        )

    def test_04_run_finalizada(self):
        client = MlflowClient()
        run = client.get_run(
            self.relatorio["run_id"]
        )
        self.assertEqual(
            run.info.status,
            "FINISHED",
        )

    def test_05_parametros_mlflow(self):
        client = MlflowClient()
        run = client.get_run(
            self.relatorio["run_id"]
        )

        self.assertEqual(
            run.data.params["modelo"],
            "LogisticRegression",
        )

        self.assertEqual(
            run.data.params["cv_folds"],
            "5",
        )

    def test_06_metricas_mlflow(self):
        client = MlflowClient()
        run = client.get_run(
            self.relatorio["run_id"]
        )

        self.assertEqual(
            len(run.data.metrics),
            7,
        )

        self.assertIn(
            "roc_auc_teste",
            run.data.metrics,
        )

        self.assertIn(
            "f1_inadimplente",
            run.data.metrics,
        )

    def test_07_dataset(self):
        base, Xtr, Xte, ytr, yte = carregar_dados()

        self.assertEqual(
            len(base),
            6000,
        )

        self.assertEqual(
            len(Xtr),
            4500,
        )

        self.assertEqual(
            len(Xte),
            1500,
        )

    def test_08_pipeline(self):
        modelo = construir_pipeline()

        self.assertIsInstance(
            modelo.named_steps["model"],
            LogisticRegression,
        )

    def test_09_cliente_simulado(self):
        cliente = novo_cliente()

        self.assertEqual(
            cliente.shape,
            (1, 8),
        )

    def test_10_probabilidade(self):
        p = self.relatorio[
            "simulacao_cliente"
        ]["probabilidade_inadimplencia"]

        self.assertGreaterEqual(p, 0.0)
        self.assertLessEqual(p, 1.0)

    def test_11_arquivos(self):
        for arquivo in (
            ARQUIVO_RELATORIO,
            ARQUIVO_PREVISOES,
            ARQUIVO_CLASSIFICACAO,
        ):
            self.assertTrue(
                arquivo.is_file()
            )

            self.assertGreater(
                arquivo.stat().st_size,
                0,
            )

    def test_12_reutilizacao_da_run(self):
        anterior = verificar_run_anterior()

        self.assertEqual(
            anterior["run_id"],
            self.relatorio["run_id"],
        )

    def test_13_previsoes_validas(self):
        df = pd.read_csv(
            ARQUIVO_PREVISOES
        )

        self.assertEqual(
            len(df),
            1500,
        )

        self.assertTrue(
            np.isfinite(
                df["probabilidade_inadimplente"]
            ).all()
        )

        self.assertTrue(
            df["probabilidade_inadimplente"]
            .between(0, 1)
            .all()
        )

    def test_14_sem_registry(self):
        self.assertFalse(
            self.relatorio[
                "modelo_registrado_registry"
            ]
        )


if __name__ == "__main__":
    unittest.main()
