"""16 testes da Aula 15 - Criacao dinamica."""

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

from src.aula15_criacao_dinamica import (
    TIPOS_DISPONIVEIS,
    MAPA_PEDIDOS,
    criar_pedido_condicional,
    criar_pedido_mapa,
    processar_pedido,
    escolher_por_input,
    analisar_criacao_dinamica,
)


class TestCriacaoDinamica(unittest.TestCase):

    def capturar(self, funcao):
        saida = io.StringIO()

        with contextlib.redirect_stdout(saida):
            resultado = funcao()

        return resultado, saida.getvalue().strip()

    def test_01_tipos_disponiveis(self):
        self.assertEqual(
            TIPOS_DISPONIVEIS,
            ["pix", "cartao", "boleto"],
        )

    def test_02_condicional_pix(self):
        pedido = criar_pedido_condicional("pix")
        self.assertIsInstance(pedido, PedidoPixFactory)

    def test_03_condicional_cartao(self):
        pedido = criar_pedido_condicional("cartao")
        self.assertIsInstance(
            pedido, PedidoCartaoFactory
        )

    def test_04_condicional_boleto(self):
        pedido = criar_pedido_condicional("boleto")
        self.assertIsInstance(
            pedido, PedidoBoletoFactory
        )

    def test_05_condicional_invalido(self):
        with self.assertRaisesRegex(
            ValueError, "Tipo de pagamento inválido"
        ):
            criar_pedido_condicional("dinheiro")

    def test_06_mapa_tres_factories(self):
        self.assertEqual(
            set(MAPA_PEDIDOS),
            {"pix", "cartao", "boleto"},
        )

    def test_07_mapa_pix(self):
        pedido = criar_pedido_mapa("pix")
        self.assertIsInstance(pedido, PedidoPixFactory)

    def test_08_mapa_cartao(self):
        pedido = criar_pedido_mapa("cartao")
        self.assertIsInstance(
            pedido, PedidoCartaoFactory
        )

    def test_09_mapa_boleto(self):
        pedido = criar_pedido_mapa("boleto")
        self.assertIsInstance(
            pedido, PedidoBoletoFactory
        )

    def test_10_mapa_invalido(self):
        with self.assertRaisesRegex(
            ValueError, "Tipo inválido"
        ):
            criar_pedido_mapa("dinheiro")

    def test_11_factories_herdam_criador(self):
        for tipo in TIPOS_DISPONIVEIS:
            pedido = criar_pedido_mapa(tipo)

            self.assertIsInstance(
                pedido, ServicoDePedidoFactory
            )

    def test_12_processamento_pix_100(self):
        pedido, saida = self.capturar(
            lambda: processar_pedido("pix", 100)
        )

        self.assertIsInstance(pedido, PedidoPixFactory)
        self.assertEqual(
            saida,
            "Pagamento via PIX de R$ 100 processado.",
        )

    def test_13_processamento_cartao_100(self):
        pedido, saida = self.capturar(
            lambda: processar_pedido("cartao", 100)
        )

        self.assertIsInstance(
            pedido, PedidoCartaoFactory
        )
        self.assertEqual(
            saida,
            "Pagamento no cartão de R$ 100 processado.",
        )

    def test_14_processamento_boleto_100(self):
        pedido, saida = self.capturar(
            lambda: processar_pedido("boleto", 100)
        )

        self.assertIsInstance(
            pedido, PedidoBoletoFactory
        )
        self.assertEqual(
            saida,
            "Pagamento via boleto de R$ 100 processado.",
        )

    def test_15_input_simulado_e_estrategia_invalida(self):
        perguntas = []

        def entrada_falsa(pergunta):
            perguntas.append(pergunta)
            return "pix"

        pedido, saida = self.capturar(
            lambda: escolher_por_input(
                150, entrada=entrada_falsa
            )
        )

        self.assertIsInstance(pedido, PedidoPixFactory)
        self.assertEqual(
            saida,
            "Pagamento via PIX de R$ 150 processado.",
        )
        self.assertEqual(
            perguntas, ["Tipo de pagamento: "]
        )

        with self.assertRaisesRegex(
            ValueError, "Estratégia inválida"
        ):
            processar_pedido(
                "pix", 100, estrategia="desconhecida"
            )

    def test_16_limitacoes_e_analise(self):
        resultado = analisar_criacao_dinamica()

        self.assertEqual(resultado["aula"], 15)
        self.assertEqual(
            resultado["mapa"]["pix"],
            "PedidoPixFactory",
        )
        self.assertTrue(
            resultado[
                "mapa_precisa_ser_editado_para_novos_tipos"
            ]
        )
        self.assertFalse(
            resultado["registro_automatico_implementado"]
        )
        self.assertFalse(
            resultado["pagamentos_reais"]
        )


if __name__ == "__main__":
    unittest.main()
