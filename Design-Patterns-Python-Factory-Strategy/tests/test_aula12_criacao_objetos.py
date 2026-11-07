"""16 testes da Aula 12 - Criacao de objetos."""

import contextlib
import io
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

import src.aula12_criacao_objetos as modulo

from src.aula12_criacao_objetos import (
    ServicoDePagamento,
    ServicoDePix,
    ServicoDePedidoRigido,
    ServicoDePedido,
    analisar_acoplamento,
)


class TestCriacaoObjetos(unittest.TestCase):

    def capturar(self, funcao):
        saida = io.StringIO()

        with contextlib.redirect_stdout(saida):
            funcao()

        return saida.getvalue().strip()

    def test_01_servico_cartao_processa(self):
        saida = self.capturar(
            lambda: ServicoDePagamento().processar(120)
        )

        self.assertEqual(
            saida,
            "Pagamento de R$ 120 processado.",
        )

    def test_02_servico_pix_processa(self):
        saida = self.capturar(
            lambda: ServicoDePix().processar(120)
        )

        self.assertEqual(
            saida,
            "Pagamento via PIX de R$ 120 processado.",
        )

    def test_03_pedido_rigido_cria_cartao(self):
        pedido = ServicoDePedidoRigido()

        self.assertIsInstance(
            pedido.pagamento,
            ServicoDePagamento,
        )

    def test_04_pedido_rigido_finaliza(self):
        pedido = ServicoDePedidoRigido()

        saida = self.capturar(
            lambda: pedido.finalizar_pedido(50)
        )

        self.assertEqual(
            saida,
            "Pagamento de R$ 50 processado.",
        )

    def test_05_pedidos_rigidos_criam_servicos_separados(self):
        primeiro = ServicoDePedidoRigido()
        segundo = ServicoDePedidoRigido()

        self.assertIsNot(
            primeiro.pagamento,
            segundo.pagamento,
        )

    def test_06_tipo_padrao_e_cartao(self):
        pedido = ServicoDePedido()

        self.assertEqual(
            pedido.tipo_pagamento,
            "cartao",
        )
        self.assertIsInstance(
            pedido.pagamento,
            ServicoDePagamento,
        )

    def test_07_cartao_explicito(self):
        pedido = ServicoDePedido("cartao")

        self.assertIsInstance(
            pedido.pagamento,
            ServicoDePagamento,
        )

    def test_08_pix_explicito(self):
        pedido = ServicoDePedido("pix")

        self.assertIsInstance(
            pedido.pagamento,
            ServicoDePix,
        )

    def test_09_finalizar_cartao(self):
        pedido = ServicoDePedido("cartao")

        saida = self.capturar(
            lambda: pedido.finalizar_pedido(120)
        )

        self.assertEqual(
            saida,
            "Pagamento de R$ 120 processado.",
        )

    def test_10_finalizar_pix(self):
        pedido = ServicoDePedido("pix")

        saida = self.capturar(
            lambda: pedido.finalizar_pedido(120)
        )

        self.assertEqual(
            saida,
            "Pagamento via PIX de R$ 120 processado.",
        )

    def test_11_tipo_invalido(self):
        with self.assertRaisesRegex(
            ValueError,
            "Tipo de pagamento inválido",
        ):
            ServicoDePedido("boleto")

    def test_12_tipo_nao_normalizado(self):
        # A aula nao implementa normalizacao.
        # "PIX" e diferente de "pix".
        with self.assertRaises(ValueError):
            ServicoDePedido("PIX")

    def test_13_construtor_nao_processa_pagamento(self):
        saida = self.capturar(
            lambda: ServicoDePedido("pix")
        )

        self.assertEqual(saida, "")

    def test_14_pedidos_independentes(self):
        cartao = ServicoDePedido("cartao")
        pix = ServicoDePedido("pix")

        self.assertIsNot(
            cartao.pagamento,
            pix.pagamento,
        )

        self.assertNotEqual(
            type(cartao.pagamento),
            type(pix.pagamento),
        )

    def test_15_comprova_criacao_acoplada(self):
        class ServicoFalso:
            def __init__(self):
                self.valores = []

            def processar(self, valor):
                self.valores.append(valor)

        # A substituicao precisa atingir o nome
        # utilizado dentro do modulo do pedido.
        # Isso ilustra o acoplamento com a classe.
        with patch.object(
            modulo,
            "ServicoDePagamento",
            ServicoFalso,
        ):
            pedido = modulo.ServicoDePedidoRigido()
            pedido.finalizar_pedido(90)

            self.assertIsInstance(
                pedido.pagamento,
                ServicoFalso,
            )

            self.assertEqual(
                pedido.pagamento.valores,
                [90],
            )

    def test_16_analise_do_problema(self):
        resultado = analisar_acoplamento()

        self.assertTrue(
            resultado["abordagem_rigida"][
                "pedido_cria_dependencia"
            ]
        )

        self.assertEqual(
            resultado["abordagem_condicional"]["tipos"],
            ["cartao", "pix"],
        )

        self.assertTrue(
            resultado["abordagem_condicional"][
                "exige_alterar_pedido_para_novo_tipo"
            ]
        )

        self.assertFalse(
            resultado["factory_implementado"]
        )

        self.assertFalse(
            resultado["pagamentos_reais"]
        )


if __name__ == "__main__":
    unittest.main()
