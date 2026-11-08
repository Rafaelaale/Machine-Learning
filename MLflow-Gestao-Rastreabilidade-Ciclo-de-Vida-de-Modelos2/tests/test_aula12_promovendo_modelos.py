"""Testes de promocao, aliases e inferencia."""

import json
import unittest

import numpy as np

from src.aula12_promovendo_modelos import (
    SAIDA,
    PREVISOES,
    RELATORIO,
    REGISTERED_MODEL_NAME,
    carregar_registro,
    novo_cliente,
    validar_inferencia,
    configurar_registry,
)


class TestAula12(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.dados = json.loads(
            SAIDA.read_text(encoding="utf-8")
        )

        cls.client, _ = configurar_registry()

    def test_01_modelo(self):
        self.assertEqual(
            self.dados["registered_model_name"],
            REGISTERED_MODEL_NAME,
        )

    def test_02_versao_preservada(self):
        anterior = carregar_registro()

        self.assertEqual(
            self.dados["version"],
            str(anterior["version"]),
        )

    def test_03_alias_candidate(self):
        self.verificar_alias("candidate")

    def test_04_alias_staging(self):
        self.verificar_alias("staging")

    def test_05_alias_production(self):
        self.verificar_alias("production")

    def test_06_alias_champion(self):
        self.verificar_alias("champion")

    def verificar_alias(self, nome):
        atual = self.client.get_model_version_by_alias(
            REGISTERED_MODEL_NAME,
            nome,
        )

        self.assertEqual(
            str(atual.version),
            self.dados["version"],
        )

    def test_07_lifecycle(self):
        versao = self.client.get_model_version(
            REGISTERED_MODEL_NAME,
            self.dados["version"],
        )

        self.assertEqual(
            versao.tags["lifecycle_status"],
            "production",
        )

        self.assertEqual(
            versao.tags["approval_type"],
            "simulated_course_exercise",
        )

    def test_08_inferencia_staging(self):
        resultado = validar_inferencia(
            self.dados["staging_uri"],
            novo_cliente(),
        )

        self.assertIn(
            resultado["classe_prevista"],
            (0, 1),
        )

    def test_09_inferencia_production(self):
        resultado = validar_inferencia(
            self.dados["production_uri"],
            novo_cliente(),
        )

        self.assertEqual(
            resultado["classe_prevista"],
            self.dados[
                "production_prediction"
            ]["classe_prevista"],
        )

    def test_10_probabilidades(self):
        staging = self.dados[
            "staging_prediction"
        ]["probabilidade_inadimplencia"]

        production = self.dados[
            "production_prediction"
        ]["probabilidade_inadimplencia"]

        self.assertTrue(
            np.isclose(
                staging,
                production,
                atol=1e-10,
                rtol=0,
            )
        )

    def test_11_arquivos(self):
        for arquivo in (
            SAIDA,
            PREVISOES,
            RELATORIO,
        ):
            self.assertTrue(arquivo.is_file())

            self.assertGreater(
                arquivo.stat().st_size,
                0,
            )

    def test_12_sem_novo_treinamento(self):
        self.assertEqual(
            self.dados["treinamentos"],
            0,
        )

        self.assertEqual(
            self.dados["novas_versoes"],
            0,
        )

        self.assertFalse(
            self.dados[
                "ambiente_real_de_producao"
            ]
        )


if __name__ == "__main__":
    unittest.main()
