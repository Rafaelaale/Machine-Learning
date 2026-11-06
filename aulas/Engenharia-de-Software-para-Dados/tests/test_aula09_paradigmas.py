"""Testes de comportamento da Aula 09."""

import sys
import unittest
from dataclasses import FrozenInstanceError
from datetime import date

from pathlib import Path

import pandas as pd


BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from src.aula09_paradigmas import (
    ClienteChurn,
    adicionar_risco,
    calcular_dias_inativos,
    classificar_risco,
    criar_alerta,
    preparar_base,
    resumir_riscos,
)


class TestParadigmas(unittest.TestCase):

    def setUp(self):
        self.referencia = date(2026, 11, 6)

        self.cliente = ClienteChurn(
            cliente_id="C001",
            ultima_atividade=date(2026, 8, 1),
            produto_id="P100",
            valor_total_compras=200.0,
            frequencia_compras=1,
            tempo_desde_primeira_compra=365,
            status_churn=False,
        )

        self.base = pd.DataFrame({
            "total_spent": [100.0, 200.0, 300.0, 400.0],
            "num_orders": [1, 8, 0, 5],
            "days_since_last_purchase": [90, 10, 60, 30],
            "churn": [1, 0, 1, 0],
        })

    def test_01_instancia(self):
        self.assertEqual(self.cliente.cliente_id, "C001")

    def test_02_objeto_imutavel(self):
        with self.assertRaises(FrozenInstanceError):
            self.cliente.cliente_id = "ALTERADO"

    def test_03_tempo_inatividade(self):
        self.assertEqual(
            self.cliente.calcular_tempo_inatividade(
                self.referencia
            ),
            97,
        )

    def test_04_data_futura_rejeitada(self):
        with self.assertRaises(ValueError):
            calcular_dias_inativos(
                date(2027, 1, 1),
                self.referencia,
            )

    def test_05_limiar_exato(self):
        self.assertTrue(classificar_risco(60, 2))

    def test_06_abaixo_do_limiar(self):
        self.assertFalse(classificar_risco(59, 2))

    def test_07_frequencia_alta(self):
        self.assertFalse(classificar_risco(90, 8))

    def test_08_valores_negativos(self):
        with self.assertRaises(ValueError):
            classificar_risco(-1, 0)

    def test_09_previsao_com_regra(self):
        self.assertTrue(
            self.cliente.prever_churn(self.referencia)
        )

    def test_10_injecao_de_regra(self):
        self.assertFalse(
            self.cliente.prever_churn(
                self.referencia,
                regra=lambda dias, compras: False,
            )
        )

    def test_11_alerta_de_risco(self):
        self.assertIn(
            "C001",
            self.cliente.notificar_cliente(self.referencia),
        )

    def test_12_sem_alerta(self):
        self.assertIsNone(criar_alerta("C002", False))

    def test_13_cliente_invalido(self):
        with self.assertRaises(ValueError):
            ClienteChurn(
                cliente_id="",
                ultima_atividade=date(2026, 8, 1),
                produto_id=None,
                valor_total_compras=100.0,
                frequencia_compras=1,
                tempo_desde_primeira_compra=None,
                status_churn=False,
            )

    def test_14_coluna_obrigatoria(self):
        incompleta = self.base.drop(columns=["churn"])

        with self.assertRaises(ValueError):
            preparar_base(incompleta)

    def test_15_valores_ausentes(self):
        base = self.base.copy()
        base.loc[0, "total_spent"] = None

        self.assertEqual(len(preparar_base(base)), 3)

    def test_16_preservacao_dataframe(self):
        original = self.base.copy(deep=True)

        adicionar_risco(self.base)

        pd.testing.assert_frame_equal(
            self.base, original
        )

    def test_17_integracao_classificacao(self):
        resultado = adicionar_risco(self.base)

        self.assertEqual(
            resultado["risco_regra"].tolist(),
            [True, False, True, False],
        )

    def test_18_integracao_resumo(self):
        resultado = resumir_riscos(self.base)

        self.assertEqual(resultado["total_clientes"], 4)
        self.assertEqual(resultado["clientes_em_risco"], 2)
        self.assertEqual(resultado["clientes_sem_risco"], 2)
        self.assertEqual(resultado["percentual_risco"], 50.0)


if __name__ == "__main__":
    unittest.main()
