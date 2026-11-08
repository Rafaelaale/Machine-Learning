import json
import unittest

from src.aula04_primeira_run_mlflow import RAIZ


class TestAula20(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.arquivo = (
            RAIZ / "resultados/aula20_auditoria_mlops.json"
        )
        cls.dados = json.loads(
            cls.arquivo.read_text(encoding="utf-8")
        )

    def test_01_relatorio(self):
        self.assertTrue(self.arquivo.is_file())

    def test_02_status(self):
        self.assertEqual(
            self.dados["status"],
            "AUDITORIA_CONCLUIDA",
        )

    def test_03_aula(self):
        self.assertEqual(self.dados["aula"], 20)

    def test_04_pipeline(self):
        self.assertTrue(self.dados["pipeline_id"])

    def test_05_modelo(self):
        self.assertTrue(
            self.dados["model_uri"].startswith("models:/")
        )

    def test_06_versao(self):
        self.assertGreaterEqual(
            int(self.dados["registered_version"]),
            1,
        )

    def test_07_quatro_runs(self):
        self.assertEqual(len(self.dados["runs"]), 4)

    def test_08_runs_finalizados(self):
        self.assertTrue(all(
            item["status"] == "FINISHED"
            for item in self.dados["runs"].values()
        ))

    def test_09_entrypoints(self):
        self.assertEqual(
            set(self.dados["entry_points"]),
            {"prepare", "train", "evaluate", "pipeline"},
        )

    def test_10_evidencias(self):
        self.assertTrue(all(
            self.dados["evidencias"].values()
        ))

    def test_11_metricas(self):
        for valor in self.dados["metrics"].values():
            self.assertGreaterEqual(valor, 0)
            self.assertLessEqual(valor, 1)

    def test_12_model_card(self):
        self.assertTrue(
            (RAIZ / "anotacoes/aula20_model_card.md").is_file()
        )

    def test_13_maturidade(self):
        m = self.dados["maturidade"]
        self.assertEqual(
            m["tracking_http_local"],
            "validado",
        )
        self.assertEqual(
            m["servidor_remoto_real"],
            "nao_implementado",
        )

    def test_14_governanca(self):
        self.assertFalse(
            self.dados["producao_aprovada"]
        )
        self.assertTrue(
            (RAIZ / "notebooks/20_stack_mlops.ipynb").is_file()
        )


if __name__ == "__main__":
    unittest.main()
