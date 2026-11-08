import json
import unittest

from src.aula16_docker_smoke import (
    RELATORIO, PREVISOES, RESUMO, COLUMNS,
    payload, predict, health, invalid_input,
)


class TestAula16(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = json.loads(RELATORIO.read_text(encoding="utf-8"))

    def test_01_api(self):
        self.assertEqual(self.report["api"], "http://127.0.0.1:5002")

    def test_02_alias(self):
        self.assertEqual(self.report["alias"], "servingCandidate")

    def test_03_colunas(self):
        self.assertEqual(payload()["dataframe_split"]["columns"], COLUMNS)

    def test_04_oito_features(self):
        self.assertEqual(len(COLUMNS), 8)

    def test_05_threshold(self):
        self.assertEqual(payload(0.4)["params"]["threshold"], 0.4)

    def test_06_threshold_invalido(self):
        with self.assertRaises(ValueError):
            payload(1.2)

    def test_07_health(self):
        checks = health()
        self.assertEqual(checks["ping"], 200)
        self.assertIn(checks["health"], (200, 404))
        self.assertIn(checks["version"], (200, 404))

    def test_08_inferencia(self):
        self.assertEqual(predict(0.3)["limiar_utilizado"], 0.3)

    def test_09_classe(self):
        self.assertIn(predict(0.5)["classe_prevista"], (0, 1))

    def test_10_probabilidade(self):
        p = predict(0.4)["probabilidade_inadimplencia"]
        self.assertTrue(0 <= p <= 1)

    def test_11_entrada_invalida(self):
        self.assertTrue(400 <= invalid_input()["http_status"] < 500)

    def test_12_arquivos(self):
        self.assertTrue(all(p.is_file() and p.stat().st_size > 0
                            for p in (RELATORIO, PREVISOES, RESUMO)))

    def test_13_mesma_probabilidade(self):
        p = self.report["predictions"]
        self.assertTrue(all(
            abs(x["probabilidade_inadimplencia"]
                - p[0]["probabilidade_inadimplencia"]) <= 1e-10
            for x in p
        ))

    def test_14_sem_retreinamento(self):
        self.assertEqual(self.report["new_trainings"], 0)
        self.assertEqual(self.report["new_runs"], 0)
        self.assertEqual(self.report["new_model_versions"], 0)


if __name__ == "__main__":
    unittest.main()
