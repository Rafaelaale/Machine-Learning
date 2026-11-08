import json
import unittest
from pathlib import Path

import mlflow
import pandas as pd
import yaml

from mlflow.tracking import MlflowClient

from src.aula04_primeira_run_mlflow import RAIZ
from src.aula18_run_pipeline import encontrar_versao
from src.aula18_evaluate import FEATURES


class TestAula18(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.resumo = json.loads(
            (RAIZ / "resultados/aula18_pipeline.json")
            .read_text(encoding="utf-8")
        )

        cls.pasta = (
            RAIZ / "resultados/aula18_pipeline"
            / cls.resumo["pipeline_id"]
        )

        mlflow.set_tracking_uri(
            f"sqlite:///{(RAIZ / 'mlflow.db').resolve().as_posix()}"
        )

        cls.client = MlflowClient()

    def test_01_entrypoints(self):
        data = yaml.safe_load(
            (RAIZ / "MLproject").read_text(encoding="utf-8")
        )
        self.assertTrue(
            {"prepare", "train", "evaluate", "pipeline"}
            .issubset(data["entry_points"])
        )

    def test_02_pipeline_finalizado(self):
        self.assertEqual(self.resumo["status"], "FINISHED")

    def test_03_id(self):
        self.assertTrue(
            self.resumo["pipeline_id"].startswith("aula18_")
        )

    def test_04_parent(self):
        self.assertTrue(self.resumo["parent_run_id"])

    def test_05_prepare(self):
        self.assertTrue(self.resumo["prepare_run_id"])

    def test_06_train(self):
        self.assertTrue(self.resumo["train_run_id"])

    def test_07_evaluate(self):
        self.assertTrue(self.resumo["evaluate_run_id"])

    def test_08_runs_distintos(self):
        ids = [
            self.resumo["parent_run_id"],
            self.resumo["prepare_run_id"],
            self.resumo["train_run_id"],
            self.resumo["evaluate_run_id"],
        ]
        self.assertEqual(len(ids), len(set(ids)))

    def test_09_status_runs(self):
        for key in (
            "parent_run_id",
            "prepare_run_id",
            "train_run_id",
            "evaluate_run_id",
        ):
            run = self.client.get_run(self.resumo[key])
            self.assertEqual(run.info.status, "FINISHED")

    def test_10_parent_tags(self):
        parent = self.resumo["parent_run_id"]

        for key in (
            "prepare_run_id",
            "train_run_id",
            "evaluate_run_id",
        ):
            run = self.client.get_run(self.resumo[key])
            self.assertEqual(
                run.data.tags.get("mlflow.parentRunId"),
                parent,
            )

    def test_11_dados(self):
        pasta = RAIZ / self.resumo["data_dir"]
        self.assertTrue((pasta / "train.csv").is_file())
        self.assertTrue((pasta / "test.csv").is_file())

    def test_12_features(self):
        pasta = RAIZ / self.resumo["data_dir"]
        df = pd.read_csv(pasta / "test.csv")
        self.assertTrue(set(FEATURES).issubset(df.columns))

    def test_13_relatorios(self):
        for name in (
            "prepare.json",
            "train.json",
            "evaluation.json",
            "classification_report.txt",
            "classification_report.json",
            "confusion_matrix.json",
            "pipeline_summary.json",
        ):
            self.assertTrue((self.pasta / name).is_file())

    def test_14_metricas(self):
        for value in self.resumo["metrics"].values():
            self.assertTrue(0 <= value <= 1)

    def test_15_confusao(self):
        cm = self.resumo["confusion_matrix"]
        self.assertEqual(
            sum(cm.values()),
            self.resumo["parameters"]["n_samples"]
            * self.resumo["parameters"]["test_size"],
        )

    def test_16_registro(self):
        version = encontrar_versao(
            self.client,
            self.resumo["registered_model_name"],
            self.resumo["train_run_id"],
        )
        self.assertEqual(
            str(version.version),
            self.resumo["registered_version"],
        )


if __name__ == "__main__":
    unittest.main()
