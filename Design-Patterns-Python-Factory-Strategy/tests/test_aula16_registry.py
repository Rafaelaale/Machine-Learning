"""16 testes da Aula 16 - Registry."""

import contextlib
import io
import sys
import unittest
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from src.aula14_factory_method import (
    ServicoDePedidoFactory,
    PedidoPixFactory,
    PedidoCartaoFactory,
    PedidoBoletoFactory,
)

from src.aula16_registry import (
    Registry,
    construir_registro,
    finalizar_pagamento,
    PagamentoTransferencia,
    PedidoTransferenciaFactory,
    demonstrar_registro_dinamico,
    demonstrar_substituicao,
    analisar_registry,
)


class TestRegistry(unittest.TestCase):

    def capturar(self, funcao):
        saida = io.StringIO()

        with contextlib.redirect_stdout(saida):
            resultado = funcao()

        return resultado, saida.getvalue().strip()

    def test_01_registro_inicialmente_vazio(self):
        registro = Registry()
        self.assertEqual(registro.mapa, {})

    def test_02_registrar_pix(self):
        registro = Registry()
        registro.registrar("pix", PedidoPixFactory)

        self.assertIs(
            registro.mapa["pix"],
            PedidoPixFactory,
        )

    def test_03_registrar_cartao(self):
        registro = Registry()
        registro.registrar("cartao", PedidoCartaoFactory)

        self.assertIs(
            registro.mapa["cartao"],
            PedidoCartaoFactory,
        )

    def test_04_registrar_boleto(self):
        registro = Registry()
        registro.registrar("boleto", PedidoBoletoFactory)

        self.assertIs(
            registro.mapa["boleto"],
            PedidoBoletoFactory,
        )

    def test_05_criar_pix(self):
        registro = construir_registro()
        self.assertIsInstance(
            registro.criar("pix"),
            PedidoPixFactory,
        )

    def test_06_criar_cartao(self):
        registro = construir_registro()
        self.assertIsInstance(
            registro.criar("cartao"),
            PedidoCartaoFactory,
        )

    def test_07_criar_boleto(self):
        registro = construir_registro()
        self.assertIsInstance(
            registro.criar("boleto"),
            PedidoBoletoFactory,
        )

    def test_08_criar_chave_invalida(self):
        registro = construir_registro()

        with self.assertRaisesRegex(
            ValueError, "Tipo inválido"
        ):
            registro.criar("inexistente")

    def test_09_factories_atendem_classe_abstrata(self):
        registro = construir_registro()

        for chave in registro.mapa:
            self.assertIsInstance(
                registro.criar(chave),
                ServicoDePedidoFactory,
            )

    def test_10_criar_novas_instancias(self):
        registro = construir_registro()

        primeiro = registro.criar("pix")
        segundo = registro.criar("pix")

        self.assertIsNot(primeiro, segundo)

    def test_11_finalizar_pix(self):
        registro = construir_registro()

        pedido, saida = self.capturar(
            lambda: finalizar_pagamento(
                registro, "pix", 100
            )
        )

        self.assertIsInstance(
            pedido, PedidoPixFactory
        )
        self.assertEqual(
            saida,
            "Pagamento via PIX de R$ 100 processado.",
        )

    def test_12_finalizar_cartao_e_boleto(self):
        registro = construir_registro()

        _, cartao = self.capturar(
            lambda: finalizar_pagamento(
                registro, "cartao", 100
            )
        )

        _, boleto = self.capturar(
            lambda: finalizar_pagamento(
                registro, "boleto", 100
            )
        )

        self.assertEqual(
            cartao,
            "Pagamento no cartão de R$ 100 processado.",
        )

        self.assertEqual(
            boleto,
            "Pagamento via boleto de R$ 100 processado.",
        )

    def test_13_registro_dinamico_transferencia(self):
        registro = construir_registro()

        registro.registrar(
            "transferencia",
            PedidoTransferenciaFactory,
        )

        pedido, saida = self.capturar(
            lambda: finalizar_pagamento(
                registro, "transferencia", 200
            )
        )

        self.assertIsInstance(
            pedido, PedidoTransferenciaFactory
        )

        self.assertIsInstance(
            pedido.criar_pagamento(),
            PagamentoTransferencia,
        )

        self.assertEqual(
            saida,
            "Pagamento via transferência de R$ 200 processado.",
        )

    def test_14_chave_duplicada_sobrescreve(self):
        registro = Registry()

        registro.registrar("especial", PedidoPixFactory)
        registro.registrar(
            "especial", PedidoCartaoFactory
        )

        self.assertEqual(len(registro.mapa), 1)

        self.assertIsInstance(
            registro.criar("especial"),
            PedidoCartaoFactory,
        )

    def test_15_registros_sao_independentes(self):
        primeiro = Registry()
        segundo = Registry()

        primeiro.registrar("pix", PedidoPixFactory)

        self.assertIn("pix", primeiro.mapa)
        self.assertNotIn("pix", segundo.mapa)

        with self.assertRaises(ValueError):
            segundo.criar("pix")

    def test_16_relatorio_e_limitacoes(self):
        dinamico = demonstrar_registro_dinamico()
        substituicao = demonstrar_substituicao()
        analise = analisar_registry()

        self.assertEqual(
            dinamico["factory"],
            "PedidoTransferenciaFactory",
        )
        self.assertFalse(
            dinamico["registry_foi_modificado"]
        )
        self.assertTrue(
            substituicao["sobrescreveu"]
        )
        self.assertEqual(
            substituicao["total_chaves"],
            1,
        )
        self.assertEqual(analise["aula"], 16)
        self.assertTrue(
            analise["registro_em_tempo_de_execucao"]
        )
        self.assertFalse(
            analise["registro_por_decorator"]
        )
        self.assertFalse(
            analise["pagamentos_reais"]
        )


if __name__ == "__main__":
    unittest.main()
