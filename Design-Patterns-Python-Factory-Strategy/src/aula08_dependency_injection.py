"""Aula 08 - Entendendo Dependency Injection.

Estudo de:
- Acoplamento forte
- Inversao de controle
- Separacao de responsabilidades
- Classes abstratas (ABC)
- Duck Typing
- Protocol
- Testes com objetos falsos
"""

from abc import ABC, abstractmethod
from typing import Protocol, runtime_checkable


# 1. EXEMPLO ORIGINAL: ACOPLAMENTO FORTE

class EmailService:
    def send(self, msg: str) -> None:
        print(f"Enviando email: {msg}")


class UserNotifierAcoplado:
    def __init__(self):
        # Dependencia criada dentro da propria classe.
        self.email = EmailService()

    def notify(self, user: str) -> None:
        self.email.send(f"Olá, {user}!")


# 2. CONTRATO POR CLASSE ABSTRATA

class SenderABC(ABC):

    @abstractmethod
    def send(self, msg: str) -> None:
        """Envia uma mensagem."""
        raise NotImplementedError


class EmailSenderABC(SenderABC):
    def send(self, msg: str) -> None:
        print(f"[EMAIL ABC] {msg}")


class SmsSenderABC(SenderABC):
    def send(self, msg: str) -> None:
        print(f"[SMS ABC] {msg}")


class UserNotifierABC:
    def __init__(self, sender: SenderABC):
        self.sender = sender

    def notify(self, user: str) -> None:
        self.sender.send(f"Olá, {user}!")


# 3. CONTRATO FLEXIVEL COM PROTOCOL

@runtime_checkable
class Sender(Protocol):
    def send(self, msg: str) -> None:
        """Contrato estrutural de envio."""
        ...


class EmailSender:
    def send(self, msg: str) -> None:
        print(f"[EMAIL] {msg}")


class SmsSender:
    def send(self, msg: str) -> None:
        print(f"[SMS] {msg}")


class WhatsAppSender:
    """Nao herda de Sender. Usa duck typing."""

    def send(self, msg: str) -> None:
        print(f"[WhatsApp] {msg}")


class UserNotifier:
    def __init__(self, sender: Sender):
        # A dependencia chega pronta.
        self.sender = sender

    def notify(self, user: str) -> None:
        self.sender.send(f"Olá, {user}!")


# 4. TEST DOUBLE: NAO ENVIA MENSAGENS REAIS

class FakeSender:
    def __init__(self):
        self.mensagens = []

    def send(self, msg: str) -> None:
        self.mensagens.append(msg)


# 5. DEMONSTRACAO COM RESULTADOS VERIFICAVEIS

def demonstrar_fake_sender():
    sender = FakeSender()
    notifier = UserNotifier(sender)

    notifier.notify("Maria")
    notifier.notify("Carlos")

    return {
        "quantidade": len(sender.mensagens),
        "mensagens": list(sender.mensagens),
        "mesmo_sender": notifier.sender is sender,
    }


def verificar_contratos():
    return {
        "email_protocol": isinstance(EmailSender(), Sender),
        "sms_protocol": isinstance(SmsSender(), Sender),
        "whatsapp_protocol": isinstance(WhatsAppSender(), Sender),
        "fake_protocol": isinstance(FakeSender(), Sender),
        "email_abc": isinstance(EmailSenderABC(), SenderABC),
        "sms_abc": isinstance(SmsSenderABC(), SenderABC),
        "whatsapp_herda_abc": isinstance(
            WhatsAppSender(), SenderABC
        ),
    }


def executar():
    return {
        "aula": 8,
        "titulo": "Entendendo Dependency Injection",
        "principios": [
            "Inversao de controle",
            "Separacao de responsabilidades",
            "Acoplamento reduzido",
        ],
        "contratos": verificar_contratos(),
        "teste_sem_envio": demonstrar_fake_sender(),
        "envio_real": False,
    }
