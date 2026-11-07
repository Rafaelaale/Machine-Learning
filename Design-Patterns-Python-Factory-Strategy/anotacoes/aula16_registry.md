# Aula 16 - Registry

## 1. Problema da Aula 15

A selecao dinamica de objetos utilizava
um dicionario fixo chamado MAPA_PEDIDOS.

Adicionar novas factories exigia
modificar o dicionario.

## 2. O que e Registry?

Registry e um mecanismo que associa
chaves a classes, objetos ou funcoes.

As classes podem ser registradas
durante a execucao do programa.

## 3. Implementacao

```python id="m3hmy5"
class Registry:
    def __init__(self):
        self.mapa = {}

    def registrar(self, chave, classe):
        self.mapa[chave] = classe

    def criar(self, chave):
        classe = self.mapa.get(chave)

        if not classe:
            raise ValueError("Tipo inválido")

        return classe()
```

## 4. Registro de factories

```python id="bxmuqd"
registro = Registry()

registro.registrar("pix", PedidoPixFactory)
registro.registrar("cartao", PedidoCartaoFactory)
registro.registrar("boleto", PedidoBoletoFactory)
```

## 5. Criacao dinamica

```python id="tx9vzo"
pedido = registro.criar("pix")
pedido.finalizar_pedido(100)
```

O cliente nao precisa conhecer
a classe concreta da Factory.

## 6. Extensibilidade

Adicionamos PedidoTransferenciaFactory
sem alterar a implementacao de Registry.

Basta registrar a nova classe:

```python id="463koz"
registro.registrar(
    "transferencia",
    PedidoTransferenciaFactory,
)
```

## 7. Comportamento com chaves duplicadas

Conforme a transcricao, registrar uma
nova classe com a mesma chave substitui
silenciosamente o registro anterior.

Isso pode ser um problema em sistemas
grandes e precisa ser documentado.

Nesta aula, mantemos esse comportamento.

## 8. Frameworks citados na transcricao

Django:
django.apps.apps.get_model()
consulta modelos conhecidos pelo
registro de aplicativos e modelos.

Django Signals:
o decorator receiver registra callbacks.

Flask:
register_blueprint() conecta um blueprint
a uma aplicacao Flask.

Click:
group() e command() permitem registrar
comandos em uma aplicacao de terminal.

A transcricao tambem menciona registros
em FastAPI, Typer, Celery, Matplotlib,
Jinja2 e SQLAlchemy.

Esses exemplos sao referencias conceituais.
Nao instalamos Django, Flask ou Click
neste laboratorio.

## 9. Beneficios

- Menor acoplamento.
- Registro dinamico em tempo de execucao.
- Inclusao de novas classes.
- Reutilizacao por diferentes clientes.
- Possibilidade de integrar decorators.

## 10. Limitacoes

- Dificuldade de localizar os registros.
- Problemas de colisao de nomes.
- Dependencia da ordem de inicializacao.
- Necessidade de documentar os registros.

## 11. Registry e Factory Method

Factory Method define como subclasses
criam produtos.

Registry permite localizar dinamicamente
a classe Factory correspondente.

Os dois mecanismos se complementam.

## 12. Limite desta aula

Nao implementamos o registro
por decorator, pois a transcricao
indica que sera estudado depois.

## 13. Arquivos

src/aula16_registry.py
aulas/aula16_registry.py
tests/test_aula16_registry.py
anotacoes/aula16_registry.md
resultados/aula16_registry.json
