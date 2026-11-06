"""Testes das politicas de colaboracao da Aula 14."""

import sys
import unittest
from pathlib import Path


BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from src.aula14_fluxo_colaborativo import (
    Mudanca,
    avaliar_integracao,
    comparar_fluxos,
    recomendar_fluxo,
    validar_branch,
)


class TestFluxoColaborativo(unittest.TestCase):

    def setUp(self):
        self.mudanca = Mudanca(
            identificador="CHURN-014",
            branch="feature/preprocessamento",
            arquivos_alterados=3,
            dias_aberta=1,
            testes_aprovados=True,
            revisao_aprovada=True,
            cobertura=98.02,
        )

    def test_01_branch_feature(self):
        self.assertTrue(
            validar_branch("feature/preprocessamento")
        )

    def test_02_branch_hotfix(self):
        self.assertTrue(
            validar_branch("hotfix/erro-producao")
        )

    def test_03_branch_release(self):
        self.assertTrue(
            validar_branch("release/1.2.0")
        )

    def test_04_branch_invalida(self):
        self.assertFalse(
            validar_branch("feature/dados novos")
        )

    def test_05_branch_principal(self):
        self.assertTrue(validar_branch("main"))
        self.assertTrue(validar_branch("develop"))

    def test_06_cobertura_invalida(self):
        with self.assertRaises(ValueError):
            Mudanca(
                "X", "feature/teste", 2, 1,
                True, True, 105.0,
            )

    def test_07_tempo_negativo(self):
        with self.assertRaises(ValueError):
            Mudanca(
                "X", "feature/teste", 2, -1,
                True, True, 95.0,
            )

    def test_08_integracao_aprovada(self):
        resultado = avaliar_integracao(
            self.mudanca, "trunk"
        )
        self.assertTrue(resultado["aprovada"])

    def test_09_bloqueio_por_testes(self):
        mudanca = Mudanca(
            "X", "feature/teste", 2, 1,
            False, True, 98.0,
        )
        resultado = avaliar_integracao(mudanca, "trunk")

        self.assertFalse(resultado["aprovada"])
        self.assertIn(
            "Testes automatizados falharam",
            resultado["impedimentos"],
        )

    def test_10_bloqueio_por_revisao(self):
        mudanca = Mudanca(
            "X", "feature/teste", 2, 1,
            True, False, 98.0,
        )
        resultado = avaliar_integracao(mudanca, "gitflow")

        self.assertFalse(resultado["aprovada"])

    def test_11_cobertura_insuficiente(self):
        mudanca = Mudanca(
            "X", "feature/teste", 2, 1,
            True, True, 70.0,
        )
        resultado = avaliar_integracao(mudanca, "trunk")

        self.assertFalse(resultado["aprovada"])

    def test_12_limite_configuravel(self):
        mudanca = Mudanca(
            "X", "feature/teste", 2, 1,
            True, True, 88.0,
        )

        self.assertTrue(
            avaliar_integracao(
                mudanca,
                "trunk",
                cobertura_minima=85,
            )["aprovada"]
        )

    def test_13_branch_longa_alerta(self):
        mudanca = Mudanca(
            "X", "feature/teste", 2, 8,
            True, True, 95.0,
        )
        resultado = avaliar_integracao(mudanca, "trunk")

        self.assertTrue(resultado["aprovada"])
        self.assertTrue(resultado["alertas"])

    def test_14_mudanca_grande_alerta(self):
        mudanca = Mudanca(
            "X", "feature/teste", 15, 1,
            True, True, 95.0,
        )
        resultado = avaliar_integracao(mudanca, "trunk")

        self.assertTrue(resultado["alertas"])

    def test_15_recall_zero_bloqueado(self):
        mudanca = Mudanca(
            "X", "feature/modelo-churn", 3, 1,
            True, True, 98.02,
            recall_churn=0.0,
            altera_modelo=True,
        )

        resultado = avaliar_integracao(
            mudanca,
            "trunk",
            destino_producao=True,
            recall_minimo=0.60,
        )

        self.assertFalse(resultado["aprovada"])
        self.assertIn(
            "Recall abaixo do criterio de negocio",
            resultado["impedimentos"],
        )

    def test_16_recall_ausente_bloqueado(self):
        mudanca = Mudanca(
            "X", "feature/modelo", 2, 1,
            True, True, 98.0,
            altera_modelo=True,
        )

        resultado = avaliar_integracao(
            mudanca,
            "trunk",
            destino_producao=True,
            recall_minimo=0.60,
        )

        self.assertFalse(resultado["aprovada"])

    def test_17_comparar_fluxos(self):
        resultado = comparar_fluxos(self.mudanca)

        self.assertIn("gitflow", resultado)
        self.assertIn("trunk", resultado)

    def test_18_recomendacao_de_fluxo(self):
        self.assertEqual(
            recomendar_fluxo(True, True, False),
            "trunk",
        )
        self.assertEqual(
            recomendar_fluxo(False, False, True),
            "gitflow",
        )


if __name__ == "__main__":
    unittest.main()
