"""16 testes da Aula 13 - Simple Factory."""

import contextlib
import io
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

import src.aula13_simple_factory as modulo

from src.aula13_simple_factory import (
    ServicoDePagamento,
    ServicoDeCartao,
    ServicoDePix,
    ServicoDePedidoComFuncao,
    ServicoDePedido,
    FabricaDePagamento,
    criar_servico_pagamento,
    analisar_simple_factory,
)


class TestSimpleFactory(unittest.TestCase):

    def capturar(self, funcao):
        saida = io.StringIO()

        with contextlib.redirect_stdout(saida):
            funcao()

        return saida.getvalue().strip()

    def test_01_funcao_cria_cartao(self):
        servico = criar_servico_pagamento("cartao")

        self.assertIsInstance(
            servico,
            ServicoDeCartao,
        )

    def test_02_funcao_cria_pix(self):
        servico = criar_servico_pagamento("pix")

        self.assertIsInstance(
            servico,
            ServicoDePix,
        )

    def test_03_funcao_rejeita_tipo_invalido(self):
        with self.assertRaisesRegex(
            ValueError,
            "Tipo de pagamento inválido",
        ):
            criar_servico_pagamento("boleto")

    def test_04_servico_cartao_processa(self):
        saida = self.capturar(
            lambda: ServicoDeCartao().processar(200)
        )

        self.assertEqual(
            saida,
            "Pagamento de R$ 200 processado.",
        )

    def test_05_servico_pix_processa(self):
        saida = self.capturar(
            lambda: ServicoDePix().processar(200)
        )

        self.assertEqual(
            saida,
            "Pagamento via PIX de R$ 200 processado.",
        )

    def test_06_servicos_atendem_contrato(self):
        self.assertTrue(
            hasattr(ServicoDeCartao(), "processar")
        )

        self.assertTrue(
            hasattr(ServicoDePix(), "processar")
        )

    def test_07_pedido_funcao_recebe_pix(self):
        pedido = ServicoDePedidoComFuncao("pix")

        self.assertIsInstance(
            pedido.pagamento,
            ServicoDePix,
        )

    def test_08_pedido_funcao_finaliza(self):
        pedido = ServicoDePedidoComFuncao("pix")

        saida = self.capturar(
            lambda: pedido.finalizar_pedido(200)
        )

        self.assertEqual(
            saida,
            "Pagamento via PIX de R$ 200 processado.",
        )

    def test_09_classe_factory_cria_cartao(self):
        servico = FabricaDePagamento.criar("cartao")

        self.assertIsInstance(
            servico,
            ServicoDeCartao,
        )

    def test_10_classe_factory_cria_pix(self):
        servico = FabricaDePagamento.criar("pix")

        self.assertIsInstance(
            servico,
            ServicoDePix,
        )

    def test_11_classe_factory_rejeita_invalido(self):
        with self.assertRaises(ValueError):
            FabricaDePagamento.criar("boleto")

    def test_12_pedido_com_classe_factory_cartao(self):
        pedido = ServicoDePedido("cartao")

        self.assertIsInstance(
            pedido.pagamento,
            ServicoDeCartao,
        )

        saida = self.capturar(
            lambda: pedido.finalizar_pedido(200)
        )

        self.assertEqual(
            saida,
            "Pagamento de R$ 200 processado.",
        )

    def test_13_pedido_com_classe_factory_pix(self):
        pedido = ServicoDePedido("pix")

        self.assertIsInstance(
            pedido.pagamento,
            ServicoDePix,
        )

        saida = self.capturar(
            lambda: pedido.finalizar_pedido(150)
        )

        self.assertEqual(
            saida,
            "Pagamento via PIX de R$ 150 processado.",
        )

    def test_14_factory_cria_objetos_independentes(self):
        primeiro = FabricaDePagamento.criar("pix")
        segundo = FabricaDePagamento.criar("pix")

        self.assertIsNot(primeiro, segundo)

    def test_15_factory_substituivel_em_testes(self):
        class PagamentoFalso:
            def __init__(self):
                self.valores = []

            def processar(self, valor):
                self.valores.append(valor)

        falso = PagamentoFalso()

        with patch.object(
            modulo.FabricaDePagamento,
            "criar",
            return_value=falso,
        ) as fabrica_falsa:
            pedido = modulo.ServicoDePedido("pix")
            pedido.finalizar_pedido(99)

            fabrica_falsa.assert_called_once_with("pix")

        self.assertIs(pedido.pagamento, falso)

        self.assertEqual(
            falso.valores,
            [99],
        )

    def test_16_analise_limites_simple_factory(self):
        resultado = analisar_simple_factory()

        self.assertEqual(resultado["aula"], 13)

        self.assertTrue(
            resultado["criacao_centralizada"]
        )

        self.assertFalse(
            resultado[
                "pedido_instancia_servicos_concretos"
            ]
        )

        self.assertTrue(
            resultado[
                "factory_precisa_mudar_para_novos_tipos"
            ]
        )

        self.assertFalse(resultado["pagamentos_reais"])


if __name__ == "__main__":
    unittest.main()
