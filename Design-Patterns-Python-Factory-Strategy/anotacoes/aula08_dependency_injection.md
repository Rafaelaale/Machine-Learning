# Aula 08 - Entendendo Dependency Injection

## 1. Problema: acoplamento forte

Na versao original, UserNotifier
cria EmailService internamente.

```python
class UserNotifier:
    def __init__(self):
        self.email = EmailService()
```

Problemas:
- Dificulta testes isolados.
- Dificulta substituir Email por SMS.
- Mistura criacao e utilizacao de dependencia.

## 2. Inversao de Controle

Quem utiliza a dependencia nao precisa
ser responsavel por cria-la.

```python
class UserNotifier:
    def __init__(self, sender):
        self.sender = sender
```

A dependencia e recebida de fora.

## 3. Separacao de Responsabilidades

UserNotifier notifica usuarios.

EmailSender, SmsSender e WhatsAppSender
executam o mecanismo de envio.

O notificador nao precisa conhecer
o canal utilizado.

## 4. Classe abstrata ABC

Uma ABC pode exigir que subclasses
implementem o metodo send.

```python
from abc import ABC, abstractmethod

class Sender(ABC):
    @abstractmethod
    def send(self, msg: str) -> None:
        raise NotImplementedError
```

Subclasses concretas precisam
implementar o metodo abstrato.

## 5. Duck Typing

Em Python, um objeto pode ser utilizado
com base nos metodos que oferece.

WhatsAppSender nao precisa herdar
de SenderABC para funcionar
com UserNotifier.

## 6. Protocol

Protocol permite declarar um
contrato de tipagem estrutural.

```python
from typing import Protocol

class Sender(Protocol):
    def send(self, msg: str) -> None: ...
```

O verificador de tipos da IDE pode
reconhecer classes compativeis mesmo
sem heranca explicita.

Protocol normalmente auxilia
a verificacao estatica de tipos.

runtime_checkable habilita isinstance
para verificacao estrutural simples,
mas nao valida integralmente as
assinaturas ou tipos em execucao.

## 7. Injetando implementacoes

```python
notifier = UserNotifier(EmailSender())
notifier.notify("Maria")

notifier = UserNotifier(SmsSender())
notifier.notify("Carlos")

notifier = UserNotifier(WhatsAppSender())
notifier.notify("Juliano")
```

A classe UserNotifier nao precisa mudar.

## 8. Testando sem envio

FakeSender armazena mensagens em memoria.

```python
fake = FakeSender()
notifier = UserNotifier(fake)
notifier.notify("Ana")

assert fake.mensagens == ["Olá, Ana!"]
```

Dessa forma, podemos testar o fluxo
sem depender de servicos externos.

## 9. Proximo assunto

Composition Root.

Local onde as dependencias concretas
serao montadas e injetadas, conforme
a proxima aula da Alura.
