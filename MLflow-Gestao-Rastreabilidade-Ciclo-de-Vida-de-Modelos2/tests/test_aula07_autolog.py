"""Testes da Aula 07 - Autolog MLflow."""

import json
import unittest

import pandas as pd

from mlflow.tracking import MlflowClient
from sklearn.base import clone
from sklearn.pipeline import Pipeline

from src.aula07_autolog import (
    ARQUIVO_CSV,
    ARQUIVO_JSON,
    EXPERIMENT_NAME,
    METRICAS_PADRONIZADAS,
    buscar_run_concluida,
    configurar_experimento,
    make_candidates,
    make_pipeline,
    make_preprocess,
)


class TestAula07(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client, cls.experimento, _ = (
            configurar_experimento()
        )

        cls.resumo = json.loads(
            ARQUIVO_JSON.read_text(
                encoding="utf-8"
            )
        )

        cls.tabela = pd.read_csv(
            ARQUIVO_CSV
        )

    def test_01_experimento(self):
        self.assertEqual(
            self.experimento.name,
            EXPERIMENT_NAME,
        )

    def test_02_tres_candidatos(self):
        self.assertEqual(
            len(make_candidates()),
            3,
        )

    def test_03_preprocessador(self):
        self.assertEqual(
            len(make_preprocess().transformers),
            2,
        )

    def test_04_pipeline(self):
        candidato = make_candidates()[
            "logistic_regression"
        ]

        pipe = make_pipeline(candidato)

        self.assertIsInstance(
            pipe,
            Pipeline,
        )

        self.assertEqual(
            list(pipe.named_steps),
            ["prep", "model"],
        )

    def test_05_tres_runs(self):
        self.assertEqual(
            self.resumo["total_runs"],
            3,
        )

        self.assertEqual(
            len(self.tabela),
            3,
        )

    def test_06_nomes(self):
        self.assertEqual(
            set(self.tabela["modelo"]),
            set(make_candidates()),
        )

    def test_07_status_finalizado(self):
        for _, linha in self.tabela.iterrows():
            mlflow_run = self.client.get_run(
                linha["run_id"]
            )

            self.assertEqual(
                mlflow_run.info.status,
                "FINISHED",
            )

    def test_08_metricas_padronizadas(self):
        for _, linha in self.tabela.iterrows():
            mlflow_run = self.client.get_run(
                linha["run_id"]
            )

            for metrica in METRICAS_PADRONIZADAS:
                self.assertIn(
                    metrica,
                    mlflow_run.data.metrics,
                )

    def test_09_tags(self):
        for _, linha in self.tabela.iterrows():
            mlflow_run = self.client.get_run(
                linha["run_id"]
            )

            self.assertEqual(
                mlflow_run.data.tags["tracking_type"],
                "hybrid_autolog",
            )

    def test_10_parametros(self):
        for _, linha in self.tabela.iterrows():
            mlflow_run = self.client.get_run(
                linha["run_id"]
            )

            self.assertIn(
                "candidate_name",
                mlflow_run.data.params,
            )

            self.assertGreater(
                len(mlflow_run.data.params),
                4,
            )

    def test_11_matriz_confusao(self):
        for _, linha in self.tabela.iterrows():
            total = sum(
                linha[c]
                for c in ("tn", "fp", "fn", "tp")
            )

            self.assertEqual(
                int(total),
                1500,
            )

    def test_12_roc_auc(self):
        self.assertTrue(
            self.tabela["roc_auc_teste"]
            .between(0, 1)
            .all()
        )

    def test_13_cv(self):
        self.assertEqual(
            self.resumo["cv_folds"],
            3,
        )

    def test_14_ranking(self):
        valores = (
            self.tabela["roc_auc_teste"].tolist()
        )

        self.assertEqual(
            valores,
            sorted(valores, reverse=True),
        )

    def test_15_reutilizacao(self):
        for _, linha in self.tabela.iterrows():
            encontrada = buscar_run_concluida(
                self.client,
                self.experimento.experiment_id,
                linha["run_name"],
            )

            self.assertIsNotNone(encontrada)

            self.assertEqual(
                encontrada.info.run_id,
                linha["run_id"],
            )

    def test_16_baseline_preservado(self):
        antigo = self.client.get_experiment_by_name(
            "risco_credito_baseline"
        )

        self.assertIsNotNone(antigo)

    def test_17_dados(self):
        self.assertEqual(
            self.resumo["n_train"],
            4500,
        )

        self.assertEqual(
            self.resumo["n_test"],
            1500,
        )

    def test_18_sem_campeao_definitivo(self):
        self.assertFalse(
            self.resumo[
                "campeao_definitivo_selecionado"
            ]
        )


if __name__ == "__main__":
    unittest.main()
