import json
import unittest
from pathlib import Path

import pandas as pd
import yaml

from src.aula04_primeira_run_mlflow import RAIZ
from src.aula17_prepare_data import (
    FEATURES,
    gerar_dados,
)
from src.aula17_train import (
    build_estimator,
    make_preprocess,
)


class TestAula17(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.prep = json.loads(
            (RAIZ / "resultados/aula17_prepare.json")
            .read_text(encoding="utf-8")
        )

        cls.train = json.loads(
            (RAIZ / "resultados/aula17_train.json")
            .read_text(encoding="utf-8")
        )

        cls.data_dir = Path(cls.prep["data_dir"])

    def test_01_mlproject(self):
        self.assertTrue((RAIZ / "MLproject").is_file())

    def test_02_python_env(self):
        self.assertTrue((RAIZ / "python_env.yaml").is_file())

    def test_03_entrypoints(self):
        config = yaml.safe_load(
            (RAIZ / "MLproject").read_text(encoding="utf-8")
        )
        self.assertIn("prepare", config["entry_points"])
        self.assertIn("train", config["entry_points"])

    def test_04_ambiente(self):
        config = yaml.safe_load(
            (RAIZ / "python_env.yaml").read_text(encoding="utf-8")
        )
        self.assertEqual(str(config["python"]), "3.12")

    def test_05_total_amostras(self):
        self.assertEqual(self.prep["n_samples"], 6000)

    def test_06_divisao(self):
        self.assertEqual(self.prep["n_train"], 4500)
        self.assertEqual(self.prep["n_test"], 1500)

    def test_07_arquivos_csv(self):
        for nome in ("full.csv", "train.csv", "test.csv"):
            self.assertTrue((self.data_dir / nome).is_file())

    def test_08_features(self):
        tabela = pd.read_csv(self.data_dir / "train.csv")
        self.assertTrue(set(FEATURES).issubset(tabela.columns))

    def test_09_reprodutibilidade(self):
        a = gerar_dados(150, 42)
        b = gerar_dados(150, 42)
        pd.testing.assert_frame_equal(a, b)

    def test_10_preprocessamento(self):
        self.assertEqual(
            len(make_preprocess().transformers),
            2,
        )

    def test_11_modelos(self):
        self.assertEqual(
            build_estimator("logistic_regression", 42)
            .__class__.__name__,
            "LogisticRegression",
        )
        self.assertEqual(
            build_estimator("random_forest", 42)
            .__class__.__name__,
            "RandomForestClassifier",
        )

    def test_12_registro_separado(self):
        self.assertEqual(
            self.train["registered_model_name"],
            "risco_credito_project_model",
        )
        self.assertTrue(self.train["registered_version"])

    def test_13_metricas(self):
        metricas = self.train["metrics"]
        for nome in (
            "roc_auc_teste",
            "accuracy_teste",
            "precision_inadimplente",
            "recall_inadimplente",
            "f1_inadimplente",
        ):
            self.assertTrue(0 <= metricas[nome] <= 1)

    def test_14_rastreabilidade(self):
        self.assertEqual(
            self.prep["pipeline_id"],
            self.train["pipeline_id"],
        )
        self.assertTrue(self.prep["run_id"])
        self.assertTrue(self.train["run_id"])


if __name__ == "__main__":
    unittest.main()
