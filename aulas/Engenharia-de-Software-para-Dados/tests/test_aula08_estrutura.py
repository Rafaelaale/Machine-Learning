"""Testes da estrutura profissional do projeto de churn."""

import sys
import unittest
from pathlib import Path

import pandas as pd


BASE = Path(__file__).resolve().parent.parent
CHURN = BASE / "projetos" / "churn_profissional"
sys.path.insert(0, str(CHURN))

from src.data.carregamento import carregar_dados_clientes


class TestEstruturaProfissional(unittest.TestCase):

    def test_01_data_raw(self):
        self.assertTrue((CHURN / "data" / "raw").is_dir())

    def test_02_notebooks(self):
        self.assertTrue((CHURN / "notebooks").is_dir())

    def test_03_src(self):
        self.assertTrue((CHURN / "src").is_dir())

    def test_04_tests(self):
        self.assertTrue((CHURN / "tests").is_dir())

    def test_05_models(self):
        self.assertTrue((CHURN / "models").is_dir())

    def test_06_documentacao(self):
        self.assertTrue((CHURN / "doc").is_dir())

    def test_07_requirements(self):
        self.assertTrue(
            (CHURN / "requirements.txt").is_file()
        )

    def test_08_setup(self):
        self.assertTrue((CHURN / "setup.py").is_file())

    def test_09_dataset_oficial(self):
        caminho = (
            CHURN / "data" / "raw" / "dados_corretos2.csv"
        )
        clientes = carregar_dados_clientes(caminho)

        self.assertIsInstance(clientes, pd.DataFrame)
        self.assertEqual(len(clientes), 10000)

    def test_10_arquivo_inexistente(self):
        with self.assertRaises(FileNotFoundError):
            carregar_dados_clientes(
                CHURN / "data" / "raw" / "nao_existe.csv"
            )

    def test_11_esquema_incompleto(self):
        import tempfile

        with tempfile.TemporaryDirectory() as pasta:
            arquivo = Path(pasta) / "incompleto.csv"
            arquivo.write_text(
                "cliente_id,nome\n1,Teste\n",
                encoding="utf-8",
            )

            with self.assertRaises(ValueError):
                carregar_dados_clientes(arquivo)

    def test_12_readme(self):
        self.assertTrue((CHURN / "README.md").is_file())


if __name__ == "__main__":
    unittest.main()
