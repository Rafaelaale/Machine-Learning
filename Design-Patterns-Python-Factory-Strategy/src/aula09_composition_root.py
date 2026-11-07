"""Aula 09 - Dependency Injection e Composition Root.

Conteudos:
- dataclass
- Protocol
- Inversao de controle
- Injecao pelo construtor
- Composition Root
- FastAPI Depends
"""

from dataclasses import dataclass
from typing import Protocol

from fastapi import Depends, FastAPI


# PARTE 1 - DATACLASS

@dataclass
class User:
    nome: str
    email: str
    telefone: str


# PARTE 2 - CONTRATO DE NOTIFICACAO

class Sender(Protocol):
    def send(self, msg: str) -> None:
        ...


class EmailSender:
    def send(self, msg: str) -> None:
        print(f"[EMAIL] {msg}")


class SmsSender:
    def send(self, msg: str) -> None:
        print(f"[SMS] {msg}")


class FakeSender:
    """Captura notificacoes sem envio externo."""

    def __init__(self):
        self.mensagens = []

    def send(self, msg: str) -> None:
        self.mensagens.append(msg)


# PARTE 3 - INJECAO PELO CONSTRUTOR

class UserNotifier:
    def __init__(self, sender: Sender):
        self.sender = sender

    def notify(self, user: User) -> None:
        self.sender.send(f"Olá, {user.nome}!")


# PARTE 4 - COMPOSITION ROOT

def composition_root():
    """Cria e conecta as dependencias da aplicacao."""
    sender = EmailSender()
    notifier = UserNotifier(sender)
    return notifier


def executar_composition_root():
    notifier = composition_root()

    user = User(
        nome="Maria",
        email="maria@example.com",
        telefone="71999999999",
    )

    notifier.notify(user)

    return {
        "usuario": user.nome,
        "email": user.email,
        "telefone": user.telefone,
        "sender": type(notifier.sender).__name__,
        "composicao_externa": True,
    }


# PARTE 5 - FASTAPI E DEPENDS

app = FastAPI(
    title="Aula 09 - Dependency Injection",
    description="Laboratorio de Composition Root e Depends",
    version="1.0.0",
)


class Logger:
    def log(self, msg: str) -> None:
        print(msg)


class UserService:
    def __init__(self, logger: Logger):
        self.logger = logger

    def create(self, name: str) -> dict:
        self.logger.log(f"Criado: {name}")
        return {"name": name}


def get_logger() -> Logger:
    return Logger()


def get_user_service(
    logger: Logger = Depends(get_logger),
) -> UserService:
    return UserService(logger)


@app.get("/")
def inicio():
    return {
        "aula": 9,
        "titulo": "Dependency Injection",
        "status": "ok",
    }


@app.post("/users")
def create_user(
    name: str,
    service: UserService = Depends(get_user_service),
):
    return service.create(name)


# PARTE 6 - SIMULACAO SEM ENVIO

def executar_fake_sender():
    fake = FakeSender()
    notifier = UserNotifier(fake)

    usuario = User(
        nome="Carlos",
        email="carlos@example.com",
        telefone="71988888888",
    )

    notifier.notify(usuario)

    return {
        "usuario": usuario.nome,
        "mensagens": fake.mensagens,
        "sender_injetado": notifier.sender is fake,
    }
