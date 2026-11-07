# Aula 09 - Explorando Dependency Injection

## 1. Revisao: Dependency Injection

Uma classe recebe as dependencias que utiliza,
em vez de criar diretamente suas implementacoes.

Isso reduz o acoplamento e facilita testes.

## 2. Dataclass

O decorador @dataclass gera automaticamente
metodos comuns para representar dados.

Exemplo:

```python id="lo4e9r"
from dataclasses import dataclass

@dataclass
class User:
    nome: str
    email: str
    telefone: str
```

Pode ser instanciada com argumentos
posicionais ou nomeados.

## 3. Inversao de Controle

UserNotifier nao cria seu sender.

```python id="42xx3g"
class UserNotifier:
    def __init__(self, sender: Sender):
        self.sender = sender
```

A dependencia e recebida pelo construtor.

## 4. Separacao de Responsabilidades

UserNotifier decide quando notificar.

EmailSender e SmsSender definem como
a mensagem e enviada.

## 5. Composition Root

Composition Root e o ponto do programa
responsavel por montar dependencias.

```python id="lzjniz"
def composition_root():
    sender = EmailSender()
    notifier = UserNotifier(sender)
    return notifier
```

A classe UserNotifier continua desacoplada
da implementacao concreta.

## 6. FastAPI e Depends

FastAPI permite declarar dependencias
para endpoints e outras dependencias.

```python id="zehgm7"
def get_logger() -> Logger:
    return Logger()

def get_user_service(
    logger: Logger = Depends(get_logger)
):
    return UserService(logger)
```

A rota recebe o servico atraves de Depends:

```python id="wd7n5s"
@app.post("/users")
def create_user(
    name: str,
    service: UserService = Depends(get_user_service)
):
    return service.create(name)
```

Neste exemplo, name e recebido como
parametro de consulta (query parameter).

## 7. Testes sem servidor externo

TestClient permite chamar a aplicacao
diretamente dentro dos testes.

Exemplo:

```python id="qi49h3"
with TestClient(app) as client:
    response = client.post(
        "/users",
        params={"name": "Maria"}
    )
```

## 8. Substituir dependencias em testes

FastAPI oferece:

app.dependency_overrides

Isso permite injetar um servico falso
sem modificar a implementacao da rota.

Depois do teste:

app.dependency_overrides.clear()

## 9. Diferenca entre testes

Testes unitarios:
validam classes isoladas usando FakeSender
e LoggerFalso.

Testes da API:
validam a integracao das dependencias
e a resposta HTTP com TestClient.

## 10. Proximo assunto

Continuar o proximo padrao de projeto
conforme a trilha apresentada pela Alura.
