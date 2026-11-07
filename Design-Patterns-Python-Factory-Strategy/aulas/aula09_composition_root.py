"""Executa o laboratorio completo da Aula 09."""

import json
import sys
from pathlib import Path

from fastapi.testclient import TestClient


BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from src.aula09_composition_root import (
    User,
    EmailSender,
    SmsSender,
    UserNotifier,
    app,
    executar_composition_root,
    executar_fake_sender,
)


def main():
    print("===== AULA 09 - EXPLORANDO DEPENDENCY INJECTION =====")

    print("\n1. DATACLASS")
    usuario = User(
        nome="Juliano",
        email="juliano@example.com",
        telefone="71999990000",
    )

    print(usuario)

    print("\n2. INJECAO PELO CONSTRUTOR")
    UserNotifier(EmailSender()).notify(usuario)
    UserNotifier(SmsSender()).notify(usuario)

    print("\n3. COMPOSITION ROOT")
    composicao = executar_composition_root()
    print(json.dumps(
        composicao,
        indent=2,
        ensure_ascii=False,
    ))

    print("\n4. TESTE COM FAKE SENDER")
    falso = executar_fake_sender()
    print(json.dumps(
        falso,
        indent=2,
        ensure_ascii=False,
    ))

    print("\n5. FASTAPI DEPENDS")
    with TestClient(app) as client:
        resposta_inicio = client.get("/")
        resposta_usuario = client.post(
            "/users",
            params={"name": "Maria"},
        )

    print(
        "GET /:",
        resposta_inicio.status_code,
        resposta_inicio.json(),
    )

    print(
        "POST /users:",
        resposta_usuario.status_code,
        resposta_usuario.json(),
    )

    if resposta_inicio.status_code != 200:
        raise RuntimeError("Falha na rota inicial")

    if resposta_usuario.status_code != 200:
        raise RuntimeError("Falha na rota de usuarios")

    if resposta_usuario.json() != {"name": "Maria"}:
        raise RuntimeError("Resposta incorreta da API")

    relatorio = {
        "aula": 9,
        "titulo": "Explorando Dependency Injection",
        "dataclass": {
            "nome": usuario.nome,
            "email": usuario.email,
            "telefone": usuario.telefone,
        },
        "composition_root": composicao,
        "fake_sender": falso,
        "fastapi": {
            "get_status": resposta_inicio.status_code,
            "post_status": resposta_usuario.status_code,
            "usuario_criado": resposta_usuario.json(),
        },
        "envio_real": False,
    }

    destino = (
        BASE / "resultados"
        / "aula09_composition_root.json"
    )

    destino.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    destino.write_text(
        json.dumps(
            relatorio,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print("\nRELATORIO:", destino)
    print("AULA 09 EXECUTADA COM SUCESSO!")


if __name__ == "__main__":
    main()
