"""Testes de flavors, signature e inferencia."""

import json
import unittest

import yaml

from src.aula13_formato_mlmodel import (
    JSON_RESULTADO,
    CSV_PREVISOES,
    JSON_INVENTARIO,
    JSON_CONTRATO,
    JSON_CENARIOS,
    MD_RELATORIO,
    COPIA_MLMODEL,
    MODEL_URI,
    conferir_registry,
    novo_cliente,
    validar_flavors,
)


class TestAula13(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.resultado = json.loads(
            JSON_RESULTADO.read_text(encoding="utf-8")
        )

        cls.contrato = json.loads(
            JSON_CONTRATO.read_text(encoding="utf-8")
        )

        cls.cenarios = json.loads(
            JSON_CENARIOS.read_text(encoding="utf-8")
        )

    def test_01_alias_production(self):
        _, versao, _ = conferir_registry()

        self.assertEqual(
            str(versao.version),
            self.resultado["version"],
        )

    def test_02_model_uri(self):
        self.assertEqual(
            self.resultado["model_uri"],
            MODEL_URI,
        )

    def test_03_mlmodel(self):
        self.assertTrue(COPIA_MLMODEL.is_file())

        conteudo = yaml.safe_load(
            COPIA_MLMODEL.read_text(encoding="utf-8")
        )

        self.assertIn("flavors", conteudo)

    def test_04_flavors(self):
        self.assertIn(
            "sklearn",
            self.resultado["flavors"],
        )

        self.assertIn(
            "python_function",
            self.resultado["flavors"],
        )

    def test_05_serializacao(self):
        self.assertEqual(
            self.resultado["serialization_format"],
            "skops",
        )

    def test_06_signature(self):
        self.assertEqual(
            self.contrato["total_inputs"],
            8,
        )

    def test_07_colunas(self):
        nomes = {
            c["name"]
            for c in self.contrato["inputs"]
        }

        self.assertIn("score_interno", nomes)
        self.assertIn("renda_mensal", nomes)
        self.assertIn("idade", nomes)

    def test_08_flavors_consistentes(self):
        resultado = validar_flavors()

        self.assertEqual(
            resultado["classe_pyfunc"],
            resultado["classe_sklearn"],
        )

    def test_09_probabilidade(self):
        prob = self.resultado["predicao"][
            "probabilidade_inadimplencia"
        ]

        self.assertGreaterEqual(prob, 0)
        self.assertLessEqual(prob, 1)

    def test_10_coluna_ausente(self):
        self.assertTrue(
            self.cenarios["coluna_ausente"]["rejeitada"]
        )

    def test_11_coluna_extra(self):
        self.assertTrue(
            self.cenarios["coluna_extra"]["aceita"]
        )

        self.assertTrue(
            self.cenarios["coluna_extra"][
                "previsoes_preservadas"
            ]
        )

    def test_12_entrada_valida(self):
        self.assertEqual(
            self.cenarios["entrada_valida"][
                "quantidade_linhas"
            ],
            3,
        )

    def test_13_arquivos(self):
        for arquivo in (
            JSON_RESULTADO,
            CSV_PREVISOES,
            JSON_INVENTARIO,
            JSON_CONTRATO,
            JSON_CENARIOS,
            MD_RELATORIO,
            COPIA_MLMODEL,
        ):
            self.assertTrue(arquivo.is_file())
            self.assertGreater(arquivo.stat().st_size, 0)

    def test_14_sem_novas_runs(self):
        self.assertEqual(
            self.resultado["novas_runs"],
            0,
        )

        self.assertEqual(
            self.resultado["novas_versoes"],
            0,
        )

        self.assertEqual(
            self.resultado["novos_treinamentos"],
            0,
        )


if __name__ == "__main__":
    unittest.main()
