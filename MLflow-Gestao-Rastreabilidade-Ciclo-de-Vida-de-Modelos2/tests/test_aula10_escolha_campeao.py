"""Testes da selecao ponderada do modelo."""

import json
import unittest

import pandas as pd
from mlflow.tracking import MlflowClient

from src.aula10_escolha_campeao import (
    RESULTADO_JSON,
    CSV,
    POLITICA_JSON,
    RESUMO_MD,
    PREPARACAO_JSON,
    POLITICA,
    buscar_candidatos,
    calcular_ranking,
    artefatos_registrados,
)


class TestAula10(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.resultado = json.loads(
            RESULTADO_JSON.read_text(encoding="utf-8")
        )
        cls.client = MlflowClient()
        cls.champion = cls.resultado["champion"]

    def test_01_tres_candidatos(self):
        _, runs = buscar_candidatos()
        self.assertEqual(len(runs), 3)

    def test_02_pesos_tecnicos(self):
        self.assertAlmostEqual(
            sum(POLITICA["technical_score"].values()),
            1.0,
        )

    def test_03_pesos_finais(self):
        self.assertAlmostEqual(
            sum(POLITICA["final_score"].values()),
            1.0,
        )

    def test_04_ranking(self):
        tabela = pd.read_csv(CSV)
        self.assertEqual(len(tabela), 3)
        self.assertTrue(
            tabela["final_score"].is_monotonic_decreasing
        )

    def test_05_recalculo(self):
        _, runs = buscar_candidatos()
        ranking = calcular_ranking(runs)

        self.assertEqual(
            ranking.iloc[0]["run_id"],
            self.champion["run_id"],
        )

    def test_06_score(self):
        valor = self.champion["final_score"]
        self.assertGreaterEqual(valor, 0)
        self.assertLessEqual(valor, 1)

    def test_07_tags_campeao(self):
        mlflow_run = self.client.get_run(
            self.champion["run_id"]
        )

        self.assertEqual(
            mlflow_run.data.tags["selection_status"],
            "champion candidate",
        )
        self.assertEqual(
            mlflow_run.data.tags["selected_for_registry"],
            "true",
        )

    def test_08_desafiantes(self):
        for item in self.resultado["ranking"][1:]:
            mlflow_run = self.client.get_run(
                item["run_id"]
            )
            self.assertEqual(
                mlflow_run.data.tags["selection_status"],
                "challenger",
            )

    def test_09_artefatos(self):
        encontrados = artefatos_registrados(
            self.client,
            self.champion["run_id"],
        )
        self.assertTrue(
            set(
                self.resultado["selection_artifacts"]
            ).issubset(encontrados)
        )

    def test_10_arquivos_locais(self):
        for arquivo in (
            RESULTADO_JSON,
            CSV,
            POLITICA_JSON,
            RESUMO_MD,
            PREPARACAO_JSON,
        ):
            self.assertTrue(arquivo.is_file())
            self.assertGreater(arquivo.stat().st_size, 0)

    def test_11_modelo_uri(self):
        modelo = self.resultado["model"]

        if modelo["localizado"]:
            self.assertTrue(
                modelo["model_uri"].startswith("models:/")
            )
        else:
            self.assertIsNone(modelo["model_uri"])

    def test_12_sem_registro(self):
        self.assertFalse(
            self.resultado["registro_model_registry"]
        )
        self.assertEqual(
            self.resultado["novas_runs"],
            0,
        )


if __name__ == "__main__":
    unittest.main()
