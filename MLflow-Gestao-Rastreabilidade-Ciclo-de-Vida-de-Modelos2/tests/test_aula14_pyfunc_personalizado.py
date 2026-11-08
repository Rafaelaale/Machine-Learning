"""Testes de contrato, limiar e Registry."""

import json
import unittest

import numpy as np

from src.aula14_pyfunc_personalizado import (
    ARQUIVO_RESULTADO,
    ARQUIVO_PREVISOES,
    ARQUIVO_RELATORIO,
    PYFUNC_MODEL_NAME,
    SOURCE_URI,
    CreditRiskPyfuncModel,
    configurar,
    conferir_origem,
    testar_wrapper_local,
    testar_registrado,
)


class TestAula14(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.dados = json.loads(
            ARQUIVO_RESULTADO.read_text(encoding="utf-8")
        )

        cls.client, _ = configurar()

    def test_01_modelo_registrado(self):
        self.assertEqual(
            self.dados["registered_model_name"],
            PYFUNC_MODEL_NAME,
        )

    def test_02_versao(self):
        self.assertGreaterEqual(
            int(self.dados["version"]),
            1,
        )

    def test_03_run_finalizada(self):
        run = self.client.get_run(
            self.dados["run_id"]
        )

        self.assertEqual(
            run.info.status,
            "FINISHED",
        )

    def test_04_origem(self):
        origem = conferir_origem(
            self.client
        )

        self.assertEqual(
            origem.run_id,
            self.dados["source_run_id"],
        )

        self.assertEqual(
            self.dados["source_model_uri"],
            SOURCE_URI,
        )

    def test_05_alias_candidate(self):
        versao = self.client.get_model_version_by_alias(
            PYFUNC_MODEL_NAME,
            "candidate",
        )

        self.assertEqual(
            str(versao.version),
            self.dados["version"],
        )

    def test_06_alias_serving(self):
        versao = self.client.get_model_version_by_alias(
            PYFUNC_MODEL_NAME,
            "servingCandidate",
        )

        self.assertEqual(
            str(versao.version),
            self.dados["version"],
        )

    def test_07_saida(self):
        esperado = [
            "probabilidade_inadimplencia",
            "classe_prevista",
            "limiar_utilizado",
        ]

        self.assertEqual(
            self.dados["output_columns"],
            esperado,
        )

    def test_08_wrapper_local(self):
        entrada, saida = testar_wrapper_local()

        self.assertEqual(len(entrada), 5)
        self.assertEqual(len(saida), 5)

    def test_09_limiar_padrao(self):
        self.assertAlmostEqual(
            self.dados["default_prediction"][
                "limiar_utilizado"
            ],
            0.5,
        )

    def test_10_limiar_alternativo(self):
        self.assertAlmostEqual(
            self.dados["alternative_prediction"][
                "limiar_utilizado"
            ],
            0.3,
        )

    def test_11_mesma_probabilidade(self):
        p1 = self.dados["default_prediction"][
            "probabilidade_inadimplencia"
        ]

        p2 = self.dados["alternative_prediction"][
            "probabilidade_inadimplencia"
        ]

        self.assertTrue(
            np.isclose(p1, p2, atol=1e-12)
        )

    def test_12_entrada_invalida(self):
        self.assertTrue(
            self.dados["invalid_column_rejected"]
        )

    def test_13_threshold_invalido(self):
        from src.aula12_promovendo_modelos import (
            novo_cliente,
        )

        from src.aula14_pyfunc_personalizado import (
            testar_wrapper_local,
        )

        entrada, _ = testar_wrapper_local()

        modelo = CreditRiskPyfuncModel(
            required_columns=list(entrada.columns)
        )

        with self.assertRaises(ValueError):
            modelo.predict(
                None,
                entrada,
                params={"threshold": 1.5},
            )

    def test_14_inferencia_registrada(self):
        padrao, ajustado = testar_registrado(
            self.dados["serving_alias_uri"]
        )

        self.assertEqual(len(padrao), 1)
        self.assertEqual(len(ajustado), 1)

    def test_15_arquivos(self):
        for arquivo in (
            ARQUIVO_RESULTADO,
            ARQUIVO_PREVISOES,
            ARQUIVO_RELATORIO,
        ):
            self.assertTrue(arquivo.is_file())
            self.assertGreater(
                arquivo.stat().st_size, 0
            )

    def test_16_sem_treinamento(self):
        self.assertFalse(
            self.dados["trained_new_algorithm"]
        )

        self.assertFalse(
            self.dados["production_promoted"]
        )


if __name__ == "__main__":
    unittest.main()
