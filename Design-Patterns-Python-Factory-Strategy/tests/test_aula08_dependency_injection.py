"""16 testes da Aula 08 - Dependency Injection."""

import contextlib
import io
import sys
import unittest
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from src.aula08_dependency_injection import (
    EmailService,
    UserNotifierAcoplado,
    SenderABC,
    EmailSenderABC,
    SmsSenderABC,
    UserNotifierABC,
    Sender,
    EmailSender,
    SmsSender,
    WhatsAppSender,
    UserNotifier,
    FakeSender,
    demonstrar_fake_sender,
    verificar_contratos,
    executar,
)


class TestDependencyInjection(unittest.TestCase):

    def capturar(self, funcao):
        saida = io.StringIO()
        with contextlib.redirect_stdout(saida):
            funcao()
        return saida.getvalue()

    def test_01_email_service_original(self):
        saida = self.capturar(
            lambda: EmailService().send("Teste")
        )
        self.assertIn("Enviando email: Teste", saida)

    def test_02_notificador_acoplado(self):
        objeto = UserNotifierAcoplado()
        self.assertIsInstance(objeto.email, EmailService)

    def test_03_notificacao_acoplada(self):
        saida = self.capturar(
            lambda: UserNotifierAcoplado().notify("Maria")
        )
        self.assertIn("Olá, Maria!", saida)

    def test_04_abc_nao_instanciavel(self):
        with self.assertRaises(TypeError):
            SenderABC()

    def test_05_email_implementa_abc(self):
        self.assertIsInstance(
            EmailSenderABC(), SenderABC
        )

    def test_06_sms_implementa_abc(self):
        self.assertIsInstance(
            SmsSenderABC(), SenderABC
        )

    def test_07_notificacao_email_abc(self):
        saida = self.capturar(
            lambda: UserNotifierABC(
                EmailSenderABC()
            ).notify("Maria")
        )
        self.assertIn("[EMAIL ABC] Olá, Maria!", saida)

    def test_08_notificacao_sms_abc(self):
        saida = self.capturar(
            lambda: UserNotifierABC(
                SmsSenderABC()
            ).notify("Carlos")
        )
        self.assertIn("[SMS ABC] Olá, Carlos!", saida)

    def test_09_email_atende_protocol(self):
        self.assertIsInstance(EmailSender(), Sender)

    def test_10_sms_atende_protocol(self):
        self.assertIsInstance(SmsSender(), Sender)

    def test_11_whatsapp_sem_heranca(self):
        objeto = WhatsAppSender()

        self.assertIsInstance(objeto, Sender)
        self.assertNotIsInstance(objeto, SenderABC)

    def test_12_notificacao_email(self):
        saida = self.capturar(
            lambda: UserNotifier(
                EmailSender()
            ).notify("Maria")
        )
        self.assertIn("[EMAIL] Olá, Maria!", saida)

    def test_13_notificacao_sms(self):
        saida = self.capturar(
            lambda: UserNotifier(
                SmsSender()
            ).notify("Juliano")
        )
        self.assertIn("[SMS] Olá, Juliano!", saida)

    def test_14_notificacao_whatsapp(self):
        saida = self.capturar(
            lambda: UserNotifier(
                WhatsAppSender()
            ).notify("Juliano")
        )
        self.assertIn("[WhatsApp] Olá, Juliano!", saida)

    def test_15_fake_sender_sem_envio_real(self):
        fake = FakeSender()
        notifier = UserNotifier(fake)

        notifier.notify("Ana")

        self.assertIs(notifier.sender, fake)
        self.assertEqual(
            fake.mensagens,
            ["Olá, Ana!"],
        )

    def test_16_relatorio_e_contratos(self):
        resultado = executar()

        self.assertEqual(resultado["aula"], 8)
        self.assertFalse(resultado["envio_real"])

        self.assertTrue(
            resultado["contratos"]["whatsapp_protocol"]
        )

        self.assertFalse(
            resultado["contratos"]["whatsapp_herda_abc"]
        )

        self.assertEqual(
            resultado["teste_sem_envio"]["quantidade"],
            2,
        )

        self.assertEqual(
            resultado["teste_sem_envio"]["mensagens"],
            ["Olá, Maria!", "Olá, Carlos!"],
        )


if __name__ == "__main__":
    unittest.main()
