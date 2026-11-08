import json
import sqlite3
import unittest
from pathlib import Path

from src.aula04_primeira_run_mlflow import RAIZ


class TestAula19(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.arquivo = (
            RAIZ / "resultados" / "aula19_servidor_remoto.json"
        )
        cls.dados = json.loads(
            cls.arquivo.read_text(encoding="utf-8")
        )
        cls.base = RAIZ / "aula19_servidor_remoto"

    def test_01_relatorio(self):
        self.assertTrue(self.arquivo.is_file())

    def test_02_status(self):
        self.assertEqual(self.dados["status"], "FINISHED")

    def test_03_http(self):
        self.assertEqual(
            self.dados["tracking_uri"],
            "http://127.0.0.1:5050",
        )

    def test_04_experimento(self):
        self.assertEqual(
            self.dados["experiment_name"],
            "aula19_tracking_remoto",
        )

    def test_05_run_id(self):
        self.assertEqual(len(self.dados["run_id"]), 32)

    def test_06_backend(self):
        self.assertTrue(
            (self.base / "tracking.db").is_file()
        )

    def test_07_artifact_store(self):
        self.assertTrue(
            (self.base / "artifacts").is_dir()
        )

    def test_08_parametro(self):
        self.assertEqual(
            self.dados["parameters"]["comunicacao"],
            "http",
        )

    def test_09_cliente(self):
        self.assertEqual(
            self.dados["parameters"]["tipo_cliente"],
            "python",
        )

    def test_10_auc(self):
        self.assertAlmostEqual(
            self.dados["metrics"]["roc_auc_exemplo"],
            0.8288,
        )

    def test_11_acuracia(self):
        self.assertAlmostEqual(
            self.dados["metrics"]["accuracy_exemplo"],
            0.7627,
        )

    def test_12_download(self):
        self.assertTrue(
            Path(self.dados["artifact_downloaded"]).is_file()
        )

    def test_13_integridade(self):
        origem = Path(self.dados["artifact_local"])
        destino = Path(self.dados["artifact_downloaded"])
        self.assertEqual(origem.read_bytes(), destino.read_bytes())
        self.assertTrue(self.dados["artifact_verified"])

    def test_14_run_no_sqlite(self):
        conexao = sqlite3.connect(
            str(self.base / "tracking.db")
        )
        try:
            resultado = conexao.execute(
                "SELECT status FROM runs WHERE run_uuid = ?",
                (self.dados["run_id"],),
            ).fetchone()
        finally:
            conexao.close()

        self.assertIsNotNone(resultado)
        self.assertEqual(resultado[0], "FINISHED")


if __name__ == "__main__":
    unittest.main()
