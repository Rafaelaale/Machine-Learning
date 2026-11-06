"""Testes funcionais e de integracao do pacote Python."""

import tempfile
import unittest
from pathlib import Path

import pandas as pd

from pre_processamento import PreProcessamento


class TestPacotePython(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)

        self.pasta = Path(self.temp.name)
        self.entrada = self.pasta / "clientes.csv"
        self.saida = self.pasta / "resultado.csv"

        self.base = pd.DataFrame({
            "customer_id": [1, 2, 3],
            "signup_date": [
                "2022-01-01", "invalida", "2022-01-03"
            ],
            "last_purchase_date": [
                "2022-01-20", None, "2022-01-22"
            ],
            "product_category": [
                "eletronico", None, "livros"
            ],
            "total_spent": [1000.0, 500.0, 300.0],
            "num_orders": [10, 5, 0],
            "city": ["Salvador", None, "Recife"],
            "payment_method": ["pix", None, "boleto"],
            "churn": ["no", "yes", "desconhecido"],
            "days_since_last_purchase": [10, None, 30],
        })

        self.base.to_csv(self.entrada, index=False)

        self.objeto = PreProcessamento(str(self.entrada))

    def carregar(self):
        self.objeto.carregar_dados()

    def ate_nulos(self):
        self.carregar()
        self.objeto.tratar_datas()
        self.objeto.preencher_nulos()

    def test_01_instancia(self):
        self.assertIsNone(self.objeto.df)

    def test_02_carregamento(self):
        self.carregar()
        self.assertEqual(len(self.objeto.df), 3)

    def test_03_arquivo_inexistente(self):
        objeto = PreProcessamento(
            str(self.pasta / "ausente.csv")
        )
        with self.assertRaises(FileNotFoundError):
            objeto.carregar_dados()

    def test_04_coluna_obrigatoria(self):
        self.base.drop(columns=["churn"]).to_csv(
            self.entrada, index=False
        )
        with self.assertRaises(ValueError):
            self.carregar()

    def test_05_metodo_antes_carregamento(self):
        with self.assertRaises(RuntimeError):
            self.objeto.tratar_datas()

    def test_06_conversao_data(self):
        self.carregar()
        self.objeto.tratar_datas()
        self.assertTrue(
            pd.api.types.is_datetime64_any_dtype(
                self.objeto.df["signup_date"]
            )
        )

    def test_07_data_invalida(self):
        self.carregar()
        self.objeto.tratar_datas()
        self.assertTrue(
            pd.isna(self.objeto.df.loc[1, "signup_date"])
        )

    def test_08_cidade_ausente(self):
        self.ate_nulos()
        self.assertEqual(
            self.objeto.df.loc[1, "city"],
            "Desconhecido",
        )

    def test_09_pagamento_ausente(self):
        self.ate_nulos()
        self.assertEqual(
            self.objeto.df.loc[1, "payment_method"],
            "outro",
        )

    def test_10_categoria_ausente(self):
        self.ate_nulos()
        self.assertEqual(
            self.objeto.df.loc[1, "product_category"],
            "outro",
        )

    def test_11_mediana(self):
        self.ate_nulos()
        self.assertEqual(
            self.objeto.df.loc[1, "days_since_last_purchase"],
            20,
        )

    def test_12_mediana_impossivel(self):
        self.base["days_since_last_purchase"] = None
        self.base.to_csv(self.entrada, index=False)
        self.carregar()
        with self.assertRaises(ValueError):
            self.objeto.preencher_nulos()

    def test_13_codificacao_churn(self):
        self.carregar()
        self.objeto.codificar_churn()
        self.assertEqual(
            self.objeto.df["churn"].iloc[:2].tolist(),
            [0, 1],
        )

    def test_14_churn_desconhecido(self):
        self.carregar()
        self.objeto.codificar_churn()
        self.assertTrue(
            pd.isna(self.objeto.df.loc[2, "churn"])
        )

    def test_15_fidelidade(self):
        self.ate_nulos()
        self.objeto.criar_colunas_derivadas()
        self.assertAlmostEqual(
            self.objeto.df.loc[0, "fidelidade"],
            10 / 11,
        )

    def test_16_score_gasto(self):
        self.ate_nulos()
        self.objeto.criar_colunas_derivadas()
        self.assertEqual(
            self.objeto.df.loc[0, "score_gasto"],
            10000,
        )

    def test_17_valor_negativo(self):
        self.base.loc[0, "num_orders"] = -1
        self.base.to_csv(self.entrada, index=False)
        self.ate_nulos()

        with self.assertRaises(ValueError):
            self.objeto.criar_colunas_derivadas()

    def test_18_one_hot_encoding(self):
        self.ate_nulos()
        self.objeto.codificar_categoricas()
        self.assertIn(
            "payment_method_pix",
            self.objeto.df.columns,
        )
        self.assertIn(
            "product_category_outro",
            self.objeto.df.columns,
        )

    def test_19_one_hot_binario(self):
        self.ate_nulos()
        self.objeto.codificar_categoricas()

        colunas = [
            nome
            for nome in self.objeto.df.columns
            if nome.startswith("payment_method_")
        ]

        valores = set(
            self.objeto.df[colunas].to_numpy().ravel()
        )

        self.assertTrue(valores.issubset({0, 1}))

    def test_20_pipeline_integrado(self):
        self.objeto.executar_pipeline(str(self.saida))
        resultado = pd.read_csv(self.saida)

        self.assertEqual(len(resultado), 3)
        self.assertIn("fidelidade", resultado.columns)
        self.assertIn("score_gasto", resultado.columns)

    def test_21_pipeline_preserva_origem(self):
        original = self.entrada.read_bytes()

        self.objeto.executar_pipeline(str(self.saida))

        self.assertEqual(
            self.entrada.read_bytes(),
            original,
        )

    def test_22_segunda_execucao_reproduzivel(self):
        self.objeto.executar_pipeline(str(self.saida))
        primeira = self.saida.read_bytes()

        self.objeto.executar_pipeline(str(self.saida))
        segunda = self.saida.read_bytes()

        self.assertEqual(primeira, segunda)


if __name__ == "__main__":
    unittest.main()
