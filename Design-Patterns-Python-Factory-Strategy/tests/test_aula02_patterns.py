"""16 testes da Aula 02 - Introducao aos Design Patterns."""

import sys
import unittest
from pathlib import Path


BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from src.aula02_introducao_patterns import (
    CATEGORIAS,
    Notificacao,
    criar_notificacao,
    MensagemFormatada,
    MensagemComPrefixo,
    aplicar_comportamento,
    aplicar_desconto,
    aplicar_acrescimo,
    classificar_exemplo,
)


class TestIntroducaoPatterns(unittest.TestCase):

    def test_01_tres_categorias(self):
        self.assertEqual(
            len(CATEGORIAS),
            3,
        )

    def test_02_categoria_criacional(self):
        self.assertIn(
            "Singleton",
            CATEGORIAS["criacional"]["exemplos"],
        )

    def test_03_categoria_estrutural(self):
        self.assertIn(
            "Adapter",
            CATEGORIAS["estrutural"]["exemplos"],
        )

    def test_04_categoria_comportamental(self):
        self.assertIn(
            "Strategy",
            CATEGORIAS["comportamental"]["exemplos"],
        )

    def test_05_criacao_notificacao(self):
        notificacao = criar_notificacao(
            "cliente@exemplo.com",
            "Ola",
        )

        self.assertIsInstance(
            notificacao,
            Notificacao,
        )

    def test_06_canal_padrao(self):
        notificacao = criar_notificacao(
            "cliente@exemplo.com",
            "Ola",
        )

        self.assertEqual(
            notificacao.canal,
            "email",
        )

    def test_07_notificacao_sms(self):
        notificacao = criar_notificacao(
            "5511999999999",
            "Codigo enviado",
            "sms",
        )

        self.assertEqual(
            notificacao.canal,
            "sms",
        )

    def test_08_rejeita_canal_invalido(self):
        with self.assertRaises(ValueError):
            criar_notificacao(
                "cliente",
                "Mensagem",
                "fax",
            )

    def test_09_rejeita_destinatario_vazio(self):
        with self.assertRaises(ValueError):
            criar_notificacao(
                " ",
                "Mensagem",
            )

    def test_10_rejeita_mensagem_vazia(self):
        with self.assertRaises(ValueError):
            criar_notificacao(
                "cliente",
                " ",
            )

    def test_11_mensagem_original(self):
        mensagem = MensagemFormatada("Ola")

        self.assertEqual(
            mensagem.renderizar(),
            "Ola",
        )

    def test_12_composicao(self):
        mensagem = MensagemFormatada("Ola")
        formatada = MensagemComPrefixo(
            mensagem,
            "[INFO] ",
        )

        self.assertEqual(
            formatada.renderizar(),
            "[INFO] Ola",
        )

    def test_13_objeto_original_preservado(self):
        mensagem = MensagemFormatada("Ola")

        MensagemComPrefixo(
            mensagem,
            "[INFO] ",
        )

        self.assertEqual(
            mensagem.renderizar(),
            "Ola",
        )

    def test_14_comportamento_desconto(self):
        resultado = aplicar_comportamento(
            100.0,
            aplicar_desconto,
        )

        self.assertEqual(resultado, 90.0)

    def test_15_comportamento_acrescimo(self):
        resultado = aplicar_comportamento(
            100.0,
            aplicar_acrescimo,
        )

        self.assertEqual(resultado, 110.0)

    def test_16_rejeita_comportamento_invalido(self):
        with self.assertRaises(TypeError):
            aplicar_comportamento(
                100.0,
                "desconto",
            )


if __name__ == "__main__":
    unittest.main()
