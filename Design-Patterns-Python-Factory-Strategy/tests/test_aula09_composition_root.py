"""16 testes da Aula 09 - Composition Root e FastAPI."""

import contextlib
import io
import sys
import unittest
from dataclasses import asdict, is_dataclass
from pathlib import Path

from fastapi.testclient import TestClient


BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from src.aula09_composition_root import (
    User,
    EmailSender,
    SmsSender,
    FakeSender,
    UserNotifier,
    Logger,
    UserService,
    composition_root,
    executar_composition_root,
    executar_fake_sender,
    get_logger,
    get_user_service,
    app,
)


class TestCompositionRoot(unittest.TestCase):

    def tearDown(self):
        app.dependency_overrides.clear()

    def criar_usuario(self):
        return User(
            nome="Maria",
            email="maria@example.com",
            telefone="71999999999",
        )

    def test_01_user_e_dataclass(self):
        self.assertTrue(is_dataclass(User))

    def test_02_dataclass_posicional(self):
        usuario = User("Juliano", "email", "telefone")
        self.assertEqual(usuario.nome, "Juliano")

    def test_03_dataclass_nomeada(self):
        usuario = User(
            telefone="telefone",
            email="email",
            nome="Juliano",
        )
        self.assertEqual(usuario.email, "email")

    def test_04_dataclass_convertida_dicionario(self):
        usuario = self.criar_usuario()
        dados = asdict(usuario)

        self.assertEqual(dados["nome"], "Maria")
        self.assertIn("telefone", dados)

    def test_05_injecao_preserva_dependencia(self):
        sender = FakeSender()
        notifier = UserNotifier(sender)

        self.assertIs(notifier.sender, sender)

    def test_06_notifier_envia_nome(self):
        sender = FakeSender()
        notifier = UserNotifier(sender)

        notifier.notify(self.criar_usuario())

        self.assertEqual(
            sender.mensagens,
            ["Olá, Maria!"],
        )

    def test_07_email_sender(self):
        saida = io.StringIO()

        with contextlib.redirect_stdout(saida):
            UserNotifier(
                EmailSender()
            ).notify(self.criar_usuario())

        self.assertIn("[EMAIL] Olá, Maria!", saida.getvalue())

    def test_08_sms_sender(self):
        saida = io.StringIO()

        with contextlib.redirect_stdout(saida):
            UserNotifier(
                SmsSender()
            ).notify(self.criar_usuario())

        self.assertIn("[SMS] Olá, Maria!", saida.getvalue())

    def test_09_composition_root(self):
        notifier = composition_root()

        self.assertIsInstance(notifier, UserNotifier)
        self.assertIsInstance(notifier.sender, EmailSender)

    def test_10_execucao_composition_root(self):
        with contextlib.redirect_stdout(io.StringIO()):
            resultado = executar_composition_root()

        self.assertTrue(resultado["composicao_externa"])
        self.assertEqual(resultado["usuario"], "Maria")

    def test_11_fake_sender_sem_envio_externo(self):
        resultado = executar_fake_sender()

        self.assertTrue(resultado["sender_injetado"])
        self.assertEqual(
            resultado["mensagens"],
            ["Olá, Carlos!"],
        )

    def test_12_logger_injetavel(self):
        logger = get_logger()
        service = UserService(logger)

        self.assertIs(service.logger, logger)

    def test_13_user_service_create(self):
        class LoggerFalso:
            def __init__(self):
                self.registros = []

            def log(self, msg):
                self.registros.append(msg)

        fake = LoggerFalso()
        service = UserService(fake)

        resultado = service.create("Ana")

        self.assertEqual(resultado, {"name": "Ana"})
        self.assertEqual(fake.registros, ["Criado: Ana"])

    def test_14_fastapi_rota_inicial(self):
        with TestClient(app) as client:
            resposta = client.get("/")

        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.json()["aula"], 9)

    def test_15_fastapi_post_users(self):
        with TestClient(app) as client:
            with contextlib.redirect_stdout(io.StringIO()):
                resposta = client.post(
                    "/users",
                    params={"name": "Maria"},
                )

        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(
            resposta.json(),
            {"name": "Maria"},
        )

    def test_16_fastapi_override_dependencia(self):
        class ServicoFalso:
            def __init__(self):
                self.nomes = []

            def create(self, name):
                self.nomes.append(name)
                return {"name": name, "teste": True}

        servico = ServicoFalso()

        app.dependency_overrides[get_user_service] = (
            lambda: servico
        )

        with TestClient(app) as client:
            resposta = client.post(
                "/users",
                params={"name": "Carlos"},
            )

        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(
            resposta.json(),
            {"name": "Carlos", "teste": True},
        )
        self.assertEqual(servico.nomes, ["Carlos"])


if __name__ == "__main__":
    unittest.main()
