"""Testes de tags e artefatos do MLflow."""

import json
import unittest

from mlflow.tracking import MlflowClient

from src.aula06_tags_artefatos import (
    RELATORIO,
    ARTEFATOS,
    TAGS,
    RUN_NAME,
    EXPERIMENTO,
    PASTA_LOCAL,
    verificar_armazenamento,
    artefatos_remotos,
    consultar_run_anterior,
)


class TestAula06(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client, cls.experimento = (
            verificar_armazenamento()
        )

        cls.relatorio = json.loads(
            RELATORIO.read_text(encoding="utf-8")
        )

        # Nao utilizar cls.run: conflito com unittest.
        cls.mlflow_run = cls.client.get_run(
            cls.relatorio["run_id"]
        )

    def test_01_experimento(self):
        self.assertEqual(
            self.experimento.name,
            EXPERIMENTO,
        )

    def test_02_nome_run(self):
        self.assertEqual(
            self.mlflow_run.data.tags["mlflow.runName"],
            RUN_NAME,
        )

    def test_03_status(self):
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

    def test_06_tags(self):
        for chave, valor in TAGS.items():
            self.assertEqual(
                self.mlflow_run.data.tags[chave],
                valor,
            )

    def test_07_artefatos(self):
        encontrados = artefatos_remotos(
            self.client,
            self.mlflow_run.info.run_id,
        )

        self.assertTrue(
            set(ARTEFATOS).issubset(encontrados)
        )

    def test_08_relatorios(self):
        for nome in (
            "classification_report.txt",
            "classification_report.json",
            "run_summary.md",
        ):
            self.assertTrue(
                (PASTA_LOCAL / "reports" / nome).is_file()
            )

    def test_09_graficos(self):
        for nome in (
            "matriz_confusao.png",
            "curva_roc.png",
            "coeficientes_modelo.png",
        ):
            arquivo = PASTA_LOCAL / "plots" / nome

            self.assertTrue(arquivo.is_file())
            self.assertGreater(arquivo.stat().st_size, 0)

    def test_10_tabela_coeficientes(self):
        arquivo = (
            PASTA_LOCAL
            / "tables"
            / "coeficientes_modelo.json"
        )

        self.assertTrue(arquivo.is_file())

        dados = json.loads(
            arquivo.read_text(encoding="utf-8")
        )

        self.assertGreater(len(dados), 0)

    def test_11_perfil_dataset(self):
        arquivo = (
            PASTA_LOCAL
            / "data"
            / "dataset_profile.json"
        )

        dados = json.loads(
            arquivo.read_text(encoding="utf-8")
        )

        self.assertEqual(
            dados["n_amostras"],
            6000,
        )

        self.assertEqual(
            dados["dataset_version"],
            "synthetic_credit_v1",
        )

    def test_12_matriz_consistente(self):
        m = self.mlflow_run.data.metrics

        total = sum(
            m[nome]
            for nome in ("tn", "fp", "fn", "tp")
        )

        self.assertEqual(int(total), 1500)

    def test_13_reutilizacao(self):
        anterior = consultar_run_anterior(
            self.client,
            self.experimento,
        )

        self.assertEqual(
            anterior["run_id"],
            self.mlflow_run.info.run_id,
        )

    def test_14_mesmo_experimento_v1(self):
        anterior = json.loads(
            (
                RELATORIO.parent
                / "aula05_logging_manual.json"
            ).read_text(encoding="utf-8")
        )

        self.assertEqual(
            anterior["experiment_id"],
            self.mlflow_run.info.experiment_id,
        )

        self.assertNotEqual(
            anterior["run_id"],
            self.mlflow_run.info.run_id,
        )


if __name__ == "__main__":
    unittest.main()
