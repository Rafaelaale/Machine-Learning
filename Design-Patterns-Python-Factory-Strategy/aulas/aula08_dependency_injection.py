"""Laboratorio da Aula 08 - Dependency Injection."""

import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from src.aula08_dependency_injection import (
    UserNotifierAcoplado,
    UserNotifierABC,
    UserNotifier,
    EmailSenderABC,
    SmsSenderABC,
    EmailSender,
    SmsSender,
    WhatsAppSender,
    FakeSender,
    executar,
)


def main():
    print("===== AULA 08 - DEPENDENCY INJECTION =====")

    print("\n1. CODIGO ACOPLADO")
    UserNotifierAcoplado().notify("Maria")

    print("\n2. INJECAO COM ABC")
    UserNotifierABC(EmailSenderABC()).notify("Maria")
    UserNotifierABC(SmsSenderABC()).notify("Carlos")

    print("\n3. INJECAO COM PROTOCOL")
    UserNotifier(EmailSender()).notify("Maria")
    UserNotifier(SmsSender()).notify("Juliano")

    print("\n4. DUCK TYPING")
    UserNotifier(WhatsAppSender()).notify("Juliano")

    print("\n5. TESTE SEM ENVIO REAL")
    fake = FakeSender()
    notifier = UserNotifier(fake)

    notifier.notify("Ana")

    print("Mensagens capturadas:", fake.mensagens)
    print("Mesmo objeto injetado:", notifier.sender is fake)

    resultado = executar()

    print("\n6. CONTRATOS")
    print(json.dumps(
        resultado["contratos"],
        ensure_ascii=False,
        indent=2,
    ))

    print("\n7. RELATORIO")
    print(json.dumps(
        resultado,
        ensure_ascii=False,
        indent=2,
    ))

    destino = (
        BASE / "resultados"
        / "aula08_dependency_injection.json"
    )

    destino.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    destino.write_text(
        json.dumps(
            resultado,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print("\nRELATORIO SALVO:", destino)
    print("AULA 08 EXECUTADA COM SUCESSO!")


if __name__ == "__main__":
    main()
