"""Testes do Model Registry e dos aliases."""

import json
import unittest

from mlflow.tracking import MlflowClient

from src.aula11_model_registry import (
    RESULTADO,
    ANOTACAO,
    REGISTERED_MODEL_NAME,
    carregar_decisao,
    build_estimator,
    configurar_registry,
    buscar_versao_existente,
)


class TestAula11(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client, _ = configurar_registry()

        cls.dados = json.loads(
            RESULTADO.read_text(encoding="utf-8")
        )

        cls.versao = cls.client.get_model_version(
            REGISTERED_MODEL_NAME,
            cls.dados["version"],
        )

    def test_01_nome_registrado(self):
        self.assertEqual(
            self.versao.name,
            REGISTERED_MODEL_NAME,
        )

    def test_02_versao_numerica(self):
        self.assertGreaterEqual(
            int(self.versao.version),
            1,
        )

    def test_03_run_origem(self):
        self.assertEqual(
            self.versao.run_id,
            self.dados["registration_run_id"],
        )

    def test_04_run_finalizada(self):
        mlflow_run = self.client.get_run(
            self.versao.run_id
        )

        self.assertEqual(
            mlflow_run.info.status,
            "FINISHED",
        )

    def test_05_alias_candidate(self):
        alias = self.client.get_model_version_by_alias(
            REGISTERED_MODEL_NAME,
            "candidate",
        )

        self.assertEqual(
            str(alias.version),
            str(self.versao.version),
        )

    def test_06_alias_algoritmo(self):
        alias = self.client.get_model_version_by_alias(
            REGISTERED_MODEL_NAME,
            self.dados["champion_model_name"],
        )

        self.assertEqual(
            str(alias.version),
            str(self.versao.version),
        )

    def test_07_tag_ciclo_vida(self):
        from pathlib import Path
        import json

        registro_aula12 = (
            RESULTADO.parent
            / "aula12_promocao_modelos.json"
        )

        esperado = "candidate"

        if registro_aula12.is_file():
            dados = json.loads(
                registro_aula12.read_text(
                    encoding="utf-8"
                )
            )
            if (
                dados["version"]
                == str(self.versao.version)
            ):
                esperado = "production"

        self.assertEqual(
            self.versao.tags["lifecycle_status"],
            esperado,
        )

    def test_08_tags_registradas(self):
        modelo = self.client.get_registered_model(
            REGISTERED_MODEL_NAME
        )

        self.assertEqual(
            modelo.tags["project"],
            "risco_credito",
        )

    def test_09_modelo_reconstruido(self):
        decisao = carregar_decisao()

        estimador = build_estimator(
            decisao["model_name"]
        )

        self.assertIsNotNone(estimador)

    def test_10_sem_duplicacao(self):
        versao = buscar_versao_existente(
            self.client,
            self.dados["selection_run_id"],
        )

        self.assertIsNotNone(versao)

        self.assertEqual(
            str(versao.version),
            str(self.versao.version),
        )

    def test_11_arquivos(self):
        self.assertTrue(RESULTADO.is_file())
        self.assertTrue(ANOTACAO.is_file())

    def test_12_nao_producao(self):
        self.assertFalse(
            self.dados["production_promoted"]
        )


if __name__ == "__main__":
    unittest.main()
