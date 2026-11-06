import sys
import unittest
from pathlib import Path

import pandas as pd


BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from src.aula06_codigo_limpo import (
    validar_colunas,
    preencher_valores_ausentes,
    calcular_tempo_do_pedido,
    normalizar_valor_da_compra,
    preprocessar_pedidos,
)


DADOS = BASE / "dados" / "aula06_pedidos_ficticios.csv"


class TestCodigoLimpo(unittest.TestCase):

    def setUp(self):
        self.df = pd.read_csv(DADOS)

    def test_carregamento(self):
        self.assertEqual(len(self.df), 6)

    def test_colunas_obrigatorias(self):
        self.assertIsNone(validar_colunas(self.df))

    def test_coluna_ausente(self):
        df = self.df.drop(columns=["valor_compra"])
        with self.assertRaises(ValueError):
            validar_colunas(df)

    def test_preenche_quantidade(self):
        resultado = preencher_valores_ausentes(self.df)
        self.assertEqual(
            resultado["quantidade_pedida"].isna().sum(), 0
        )

    def test_preenche_categoria(self):
        resultado = preencher_valores_ausentes(self.df)
        self.assertEqual(
            resultado["categoria"].isna().sum(), 0
        )
        self.assertIn(
            "desconhecido", resultado["categoria"].tolist()
        )

    def test_ano_referencia(self):
        resultado = calcular_tempo_do_pedido(
            self.df, 2026
        )
        self.assertEqual(
            int(resultado.loc[0, "tempo_pedido_anos"]), 1
        )

    def test_ano_referencia_invalido(self):
        with self.assertRaises(TypeError):
            calcular_tempo_do_pedido(self.df, "2026")

    def test_data_futura(self):
        with self.assertRaises(ValueError):
            calcular_tempo_do_pedido(self.df, 2020)

    def test_normalizacao_minmax(self):
        resultado = normalizar_valor_da_compra(self.df)

        valores = resultado["valor_compra_normalizado"]

        self.assertEqual(float(valores.min()), 0.0)
        self.assertEqual(float(valores.max()), 1.0)

    def test_normalizacao_valores_iguais(self):
        df = pd.DataFrame({
            "valor_compra": [100, 100, 100]
        })

        resultado = normalizar_valor_da_compra(df)

        self.assertTrue(
            (resultado["valor_compra_normalizado"] == 0).all()
        )

    def test_pipeline_nao_modifica_original(self):
        original = self.df.copy(deep=True)

        preprocessar_pedidos(self.df, 2026)

        pd.testing.assert_frame_equal(self.df, original)

    def test_pipeline_completo(self):
        resultado = preprocessar_pedidos(self.df, 2026)

        self.assertEqual(len(resultado), 6)
        self.assertIn(
            "tempo_pedido_anos", resultado.columns
        )
        self.assertIn(
            "valor_compra_normalizado", resultado.columns
        )
        self.assertEqual(
            int(resultado["categoria"].isna().sum()), 0
        )


if __name__ == "__main__":
    unittest.main()