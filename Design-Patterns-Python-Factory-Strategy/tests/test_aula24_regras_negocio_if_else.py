"""16 testes da Aula 24 - Regras de negocio if/else."""

import inspect
import sys
import unittest
from dataclasses import fields, is_dataclass
from pathlib import Path


RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from src.aula24_regras_negocio_if_else import (
    Cliente,
    calcular_preco_inicial,
    calcular_preco,
    CODE_SMELLS,
    analisar_aula24,
)


class TestRegrasNegocioIfElse(unittest.TestCase):

    def test_01_cliente_e_dataclass(self):
        self.assertTrue(is_dataclass(Cliente))
        self.assertEqual(
            [campo.name for campo in fields(Cliente)],
            ["nome", "tipo", "parceiro"],
        )

        cliente = Cliente("Ana", "vip")
        self.assertIsNone(cliente.parceiro)

    def test_02_inicial_vip(self):
        cliente = Cliente("Ana", "vip")
        self.assertAlmostEqual(
            calcular_preco_inicial(cliente, 100),
            80,
        )

    def test_03_inicial_novo(self):
        cliente = Cliente("Bruno", "novo")
        self.assertAlmostEqual(
            calcular_preco_inicial(cliente, 100),
            90,
        )

    def test_04_inicial_funcionario(self):
        cliente = Cliente("Carla", "funcionario")
        self.assertAlmostEqual(
            calcular_preco_inicial(cliente, 100),
            70,
        )

    def test_05_inicial_outros(self):
        cliente = Cliente("Diego", "comum")
        self.assertEqual(
            calcular_preco_inicial(cliente, 100),
            100,
        )

    def test_06_expandida_vip(self):
        cliente = Cliente("Ana", "vip")
        self.assertAlmostEqual(
            calcular_preco(cliente, 100),
            80,
        )

    def test_07_expandida_novo(self):
        cliente = Cliente("Bruno", "novo")
        self.assertAlmostEqual(
            calcular_preco(cliente, 100),
            90,
        )

    def test_08_expandida_funcionario(self):
        cliente = Cliente("Carla", "funcionario")
        self.assertAlmostEqual(
            calcular_preco(cliente, 100),
            70,
        )

    def test_09_parceria_sem_parceiro(self):
        cliente = Cliente("Eva", "parceria")
        self.assertAlmostEqual(
            calcular_preco(cliente, 100),
            85,
        )

    def test_10_parceria_empresa_x(self):
        cliente = Cliente(
            "Fabio", "parceria", "empresa_x"
        )
        self.assertAlmostEqual(
            calcular_preco(cliente, 100),
            75,
        )

    def test_11_parceria_empresa_y(self):
        cliente = Cliente(
            "Gabi", "parceria", "empresa_y"
        )
        self.assertAlmostEqual(
            calcular_preco(cliente, 100),
            80,
        )

    def test_12_parceiro_nao_altera_outro_tipo(self):
        vip = Cliente("Ana", "vip", "empresa_x")
        comum = Cliente("Diego", "comum", "empresa_y")
        desconhecido = Cliente(
            "Eva", "parceria", "empresa_z"
        )

        self.assertAlmostEqual(
            calcular_preco(vip, 100), 80
        )
        self.assertEqual(
            calcular_preco(comum, 100), 100
        )
        self.assertAlmostEqual(
            calcular_preco(desconhecido, 100), 85
        )

    def test_13_black_friday_abaixo_500(self):
        cliente = Cliente("Helena", "black_friday")
        self.assertAlmostEqual(
            calcular_preco(cliente, 400),
            200,
        )

    def test_14_black_friday_exatamente_500(self):
        cliente = Cliente("Helena", "black_friday")
        self.assertAlmostEqual(
            calcular_preco(cliente, 500),
            250,
        )

    def test_15_black_friday_acima_500(self):
        cliente = Cliente("Helena", "black_friday")
        self.assertAlmostEqual(
            calcular_preco(cliente, 600),
            270,
        )
        self.assertAlmostEqual(
            calcular_preco(cliente, 501),
            225.45,
        )

    def test_16_code_smells_e_proxima_etapa(self):
        analise = analisar_aula24()

        self.assertEqual(analise["aula"], 24)
        self.assertEqual(len(CODE_SMELLS), 7)
        self.assertEqual(
            analise["principio_afetado"],
            "aberto/fechado",
        )

        self.assertIn(
            "separar as estrategias",
            analise["solucao_proposta"],
        )

        self.assertFalse(
            analise["strategy_implementado"]
        )

        codigo = inspect.getsource(calcular_preco)

        self.assertIn(
            'cliente.tipo == "black_friday"',
            codigo,
        )

        self.assertIn(
            'cliente.parceiro == "empresa_x"',
            codigo,
        )

        self.assertIn("elif", codigo)


if __name__ == "__main__":
    unittest.main()
