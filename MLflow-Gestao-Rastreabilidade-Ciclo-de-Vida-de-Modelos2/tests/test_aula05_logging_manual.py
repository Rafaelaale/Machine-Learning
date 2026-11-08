"""Testes da Aula 05."""

import json
import unittest

import numpy as np

from mlflow.tracking import MlflowClient

from src.aula05_logging_manual import (
    RELATORIO,
    EXPERIMENTO,
    RUN_NAME,
    configurar_tracking,
    obter_run_existente,
    preparar_metricas,
)


class TestAula05(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        configurar_tracking()

        cls.relatorio = json.loads(
            RELATORIO.read_text(
                encoding="utf-8"
            )
        )

        cls.client = MlflowClient()

        cls.mlflow_run = cls.client.get_run(
            cls.relatorio["run_id"]
        )

    def test_01_experimento(self):
        exp = self.client.get_experiment(
            self.mlflow_run.info.experiment_id
        )

        self.assertEqual(
            exp.name,
            EXPERIMENTO,
        )

    def test_02_nome_run(self):
        self.assertEqual(
            self.mlflow_run.data.tags["mlflow.runName"],
            RUN_NAME,
        )

    def test_03_run_finalizada(self):
        self.assertEqual(
            self.mlflow_run.info.status,
            "FINISHED",
        )

    def test_04_parametros(self):
        self.assertEqual(
            len(self.mlflow_run.data.params),
            18,
        )

    def test_05_metricas(self):
        self.assertEqual(
            len(self.mlflow_run.data.metrics),
            11,
        )

    def test_06_configuracao_pipeline(self):
        self.assertEqual(
            self.mlflow_run.data.params["numeric_imputer"],
            "median",
        )

        self.assertEqual(
            self.mlflow_run.data.params["categorical_encoder"],
            "OneHotEncoder",
        )

    def test_07_matriz_confusao(self):
        m = self.mlflow_run.data.metrics

        total = sum(
            m[nome]
            for nome in ("tn", "fp", "fn", "tp")
        )

        self.assertEqual(
            int(total),
            1500,
        )

    def test_08_roc_auc(self):
        roc = self.mlflow_run.data.metrics[
            "roc_auc_teste"
        ]

        self.assertGreaterEqual(roc, 0.0)
        self.assertLessEqual(roc, 1.0)

    def test_09_sem_duplicacao(self):
        anterior = obter_run_existente()

        self.assertEqual(
            anterior["run_id"],
            self.mlflow_run.info.run_id,
        )

    def test_10_metricas_sinteticas(self):
        y = np.array([0, 0, 1, 1])
        pred = np.array([0, 1, 0, 1])
        prob = np.array([0.1, 0.8, 0.3, 0.9])
        scores = np.array([0.8, 0.9])

        metricas = preparar_metricas(
            y, pred, prob, scores
        )

        self.assertEqual(metricas["tn"], 1)
        self.assertEqual(metricas["fp"], 1)
        self.assertEqual(metricas["fn"], 1)
        self.assertEqual(metricas["tp"], 1)


if __name__ == "__main__":
    unittest.main()
