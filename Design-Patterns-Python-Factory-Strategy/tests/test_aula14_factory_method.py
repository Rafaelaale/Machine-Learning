"""16 testes da Aula 14 - Factory Method."""

import contextlib
import io
import inspect
import sys
import unittest
from pathlib import Path
from unittest.mock import Mock


BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from src.aula14_factory_method import (
    ServicoDePedidoFactory,
    PagamentoCartao,
    PagamentoPix,
    PagamentoBoleto,
    PedidoCartaoFactory,
    PedidoPixFactory,
    PedidoBoletoFactory,
    analisar_factory_method,
)


class TestFactoryMethod(unittest.TestCase):

    def capturar(self, funcao):
        saida = io.StringIO()

        with contextlib.redirect_stdout(saida):
            funcao()

        return saida.getvalue().strip()

    def test_01_criador_e_abstrato(self):
        self.assertTrue(
            inspect.isabstract(ServicoDePedidoFactory)
        )

    def test_02_criador_nao_instanciavel(self):
        with self.assertRaises(TypeError):
            ServicoDePedidoFactory()

    def test_03_metodo_fabrica_e_abstrato(self):
        self.assertIn(
            "criar_pagamento",
            ServicoDePedidoFactory.__abstractmethods__,
        )

    def test_04_cartao_factory_herda_criador(self):
        self.assertIsInstance(
            PedidoCartaoFactory(),
            ServicoDePedidoFactory,
        )

    def test_05_pix_factory_herda_criador(self):
        self.assertIsInstance(
            PedidoPixFactory(),
            ServicoDePedidoFactory,
        )

    def test_06_cartao_factory_cria_produto(self):
        pagamento = PedidoCartaoFactory().criar_pagamento()

        self.assertIsInstance(pagamento, PagamentoCartao)

    def test_07_pix_factory_cria_produto(self):
        pagamento = PedidoPixFactory().criar_pagamento()

        self.assertIsInstance(pagamento, PagamentoPix)

    def test_08_cartao_processa_180(self):
        saida = self.capturar(
            lambda: PagamentoCartao().processar(180)
        )

        self.assertEqual(
            saida,
            "Pagamento no cartão de R$ 180 processado.",
        )

    def test_09_pix_processa_250(self):
        saida = self.capturar(
            lambda: PagamentoPix().processar(250)
        )

        self.assertEqual(
            saida,
            "Pagamento via PIX de R$ 250 processado.",
        )

    def test_10_pedido_cartao_finaliza(self):
        pedido = PedidoCartaoFactory()

        saida = self.capturar(
            lambda: pedido.finalizar_pedido(180)
        )

        self.assertEqual(
            saida,
            "Pagamento no cartão de R$ 180 processado.",
        )

    def test_11_pedido_pix_finaliza(self):
        pedido = PedidoPixFactory()

        saida = self.capturar(
            lambda: pedido.finalizar_pedido(250)
        )

        self.assertEqual(
            saida,
            "Pagamento via PIX de R$ 250 processado.",
        )

    def test_12_cada_chamada_cria_novo_pagamento(self):
        fabrica = PedidoPixFactory()

        primeiro = fabrica.criar_pagamento()
        segundo = fabrica.criar_pagamento()

        self.assertIsNot(primeiro, segundo)

    def test_13_metodo_concreto_e_herdado(self):
        self.assertIs(
            PedidoPixFactory.finalizar_pedido,
            ServicoDePedidoFactory.finalizar_pedido,
        )

        self.assertIs(
            PedidoCartaoFactory.finalizar_pedido,
            ServicoDePedidoFactory.finalizar_pedido,
        )

    def test_14_metodo_comum_delega_ao_produto(self):
        class FabricaFalsa(ServicoDePedidoFactory):
            def __init__(self, pagamento):
                self.pagamento = pagamento

            def criar_pagamento(self):
                return self.pagamento

        pagamento = Mock()
        fabrica = FabricaFalsa(pagamento)

        fabrica.finalizar_pedido(99)

        pagamento.processar.assert_called_once_with(99)

    def test_15_extensao_boleto_sem_modificar_base(self):
        fabrica = PedidoBoletoFactory()

        self.assertIsInstance(
            fabrica,
            ServicoDePedidoFactory,
        )

        self.assertIsInstance(
            fabrica.criar_pagamento(),
            PagamentoBoleto,
        )

        saida = self.capturar(
            lambda: fabrica.finalizar_pedido(120)
        )

        self.assertEqual(
            saida,
            "Pagamento via boleto de R$ 120 processado.",
        )

    def test_16_analise_factory_method(self):
        resultado = analisar_factory_method()

        self.assertEqual(resultado["aula"], 14)

        self.assertEqual(
            resultado["metodo_fabrica"],
            "criar_pagamento",
        )

        self.assertTrue(
            resultado["principio_open_closed"]
        )

        self.assertFalse(
            resultado[
                "necessita_editar_fabrica_existente_para_boleto"
            ]
        )

        self.assertFalse(
            resultado["criacao_dinamica_por_json"]
        )

        self.assertFalse(
            resultado["pagamentos_reais"]
        )


if __name__ == "__main__":
    unittest.main()
