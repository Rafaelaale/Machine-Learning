"""Testes da Aula 02."""

import json
import unittest

from src.aula02_projeto_base_mlflow import (
    RAIZ,
    COMPONENTES,
    EXPERIMENTOS_EXEMPLO,
    METRICAS_CLASSIFICACAO,
    CRONOGRAMA,
    diferenciar_registros,
    validar_conteudo,
    executar,
)


class TestAula02(unittest.TestCase):

    def test_01_quatro_componentes(self):
        self.assertEqual(len(COMPONENTES), 4)

    def test_02_tracking(self):
        self.assertIn("Tracking", COMPONENTES)

    def test_03_registry(self):
        self.assertIn("Model Registry", COMPONENTES)

    def test_04_models(self):
        self.assertIn("Models", COMPONENTES)

    def test_05_projects(self):
        self.assertIn("Projects", COMPONENTES)

    def test_06_experimentos(self):
        self.assertEqual(
            len(EXPERIMENTOS_EXEMPLO),
            2,
        )

    def test_07_tipos_registro(self):
        self.assertEqual(
            set(diferenciar_registros()),
            {"parametro", "metrica", "artefato"},
        )

    def test_08_metricas(self):
        self.assertIn("f1", METRICAS_CLASSIFICACAO)
        self.assertIn("recall", METRICAS_CLASSIFICACAO)

    def test_09_cronograma(self):
        self.assertEqual(len(CRONOGRAMA), 10)

    def test_10_validacao(self):
        self.assertTrue(validar_conteudo())

    def test_11_relatorio(self):
        resultado = executar()

        arquivo = (
            RAIZ
            / "resultados"
            / "aula02_projeto_base_mlflow.json"
        )

        self.assertTrue(arquivo.is_file())

        dados = json.loads(
            arquivo.read_text(encoding="utf-8")
        )

        self.assertEqual(dados["aula"], 2)
        self.assertEqual(
            dados["projeto"],
            resultado["projeto"],
        )

    def test_12_sem_treinamento(self):
        resultado = executar()

        self.assertFalse(
            resultado["modelo_treinado"]
        )
        self.assertEqual(
            resultado["runs_criadas"],
            0,
        )


if __name__ == "__main__":
    unittest.main()
