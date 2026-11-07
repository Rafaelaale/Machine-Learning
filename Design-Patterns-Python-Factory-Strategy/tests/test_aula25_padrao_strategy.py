"""16 testes da Aula 25 - Padrao Strategy."""

import inspect
import sys
import unittest
from abc import ABC
from pathlib import Path


RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from src.aula25_padrao_strategy import (
    RegraDeDesconto,
    DescontoVip,
    DescontoNovo,
    DescontoFuncionario,
    SemDesconto,
    Cliente,
    calcular_preco,
    criar_clientes_exemplo,
    demonstrar_troca_estrategia,
    demonstrar_extensibilidade,
    analisar_aula25,
)


class TestPadraoStrategy(unittest.TestCase):

    def test_01_regra_de_desconto_e_abstrata(self):
        self.assertTrue(
            issubclass(RegraDeDesconto, ABC)
        )
        self.assertTrue(
            inspect.isabstract(RegraDeDesconto)
        )

    def test_02_classe_abstrata_nao_instancia(self):
        with self.assertRaises(TypeError):
            RegraDeDesconto()

    def test_03_desconto_vip(self):
        regra = DescontoVip()

        self.assertIsInstance(regra, RegraDeDesconto)
        self.assertAlmostEqual(regra.calcular(200), 160)

    def test_04_desconto_novo(self):
        regra = DescontoNovo()

        self.assertIsInstance(regra, RegraDeDesconto)
        self.assertAlmostEqual(regra.calcular(200), 180)

    def test_05_desconto_funcionario(self):
        regra = DescontoFuncionario()

        self.assertIsInstance(regra, RegraDeDesconto)
        self.assertAlmostEqual(regra.calcular(200), 140)

    def test_06_sem_desconto(self):
        regra = SemDesconto()

        self.assertIsInstance(regra, RegraDeDesconto)
        self.assertEqual(regra.calcular(200), 200)

    def test_07_cliente_armazena_estrategia(self):
        estrategia = DescontoVip()
        cliente = Cliente("Maria", estrategia)

        self.assertEqual(cliente.nome, "Maria")
        self.assertIs(
            cliente.regra_de_desconto,
            estrategia,
        )

    def test_08_maria_desconto_vip(self):
        maria = Cliente("Maria", DescontoVip())

        self.assertAlmostEqual(
            calcular_preco(maria, 200),
            160,
        )

    def test_09_joao_desconto_novo(self):
        joao = Cliente("João", DescontoNovo())

        self.assertAlmostEqual(
            calcular_preco(joao, 200),
            180,
        )

    def test_10_ana_sem_desconto(self):
        ana = Cliente("Ana", SemDesconto())

        self.assertEqual(
            calcular_preco(ana, 200),
            200,
        )

    def test_11_funcionario_desconto(self):
        funcionario = Cliente(
            "Funcionário",
            DescontoFuncionario(),
        )

        self.assertAlmostEqual(
            calcular_preco(funcionario, 200),
            140,
        )

    def test_12_troca_dinamica_de_estrategia(self):
        maria = Cliente("Maria", DescontoVip())

        primeiro = calcular_preco(maria, 200)

        maria.regra_de_desconto = DescontoNovo()

        segundo = calcular_preco(maria, 200)

        self.assertEqual(primeiro, 160)
        self.assertEqual(segundo, 180)

    def test_13_estrategia_nova_sem_alterar_funcao(self):
        class DescontoEspecial(RegraDeDesconto):
            def calcular(self, total):
                return total * 0.6

        cliente = Cliente(
            "Especial",
            DescontoEspecial(),
        )

        self.assertAlmostEqual(
            calcular_preco(cliente, 200),
            120,
        )

    def test_14_estrategia_incompleta_nao_instancia(self):
        class DescontoIncompleto(RegraDeDesconto):
            pass

        with self.assertRaises(TypeError):
            DescontoIncompleto()

    def test_15_polimorfismo_sem_condicionais(self):
        codigo = inspect.getsource(calcular_preco)

        self.assertIn(
            "cliente.regra_de_desconto.calcular(total)",
            codigo,
        )

        self.assertNotIn("if cliente.tipo", codigo)
        self.assertNotIn("elif", codigo)

        clientes = criar_clientes_exemplo()

        self.assertEqual(
            calcular_preco(clientes["maria"], 200),
            160,
        )
        self.assertEqual(
            calcular_preco(clientes["joao"], 200),
            180,
        )
        self.assertEqual(
            calcular_preco(clientes["ana"], 200),
            200,
        )

    def test_16_analise_e_demonstracoes(self):
        troca = demonstrar_troca_estrategia()
        extensao = demonstrar_extensibilidade()
        analise = analisar_aula25()

        self.assertEqual(troca["preco_com_vip"], 160)
        self.assertEqual(troca["preco_com_novo"], 180)

        self.assertAlmostEqual(
            extensao["preco_final"],
            120,
        )

        self.assertEqual(analise["aula"], 25)
        self.assertEqual(
            analise["contrato"],
            "RegraDeDesconto",
        )

        self.assertTrue(analise["polimorfismo"])
        self.assertTrue(
            analise["estrategias_intercambiaveis"]
        )
        self.assertTrue(analise["extensibilidade"])

        self.assertFalse(
            analise["strategy_com_funcoes"]
        )


if __name__ == "__main__":
    unittest.main()
