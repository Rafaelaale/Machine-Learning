# Aula 13 - Simple Factory

## 1. Problema da aula anterior

Na Aula 12, ServicoDePedido conhecia
diretamente as implementacoes de pagamento.

Adicionar novos meios exigia alterar
a propria classe de pedido.

## 2. O que e Simple Factory?

A Simple Factory centraliza
a criacao de objetos relacionados.

O cliente informa um tipo,
e a fabrica cria o objeto adequado.

## 3. Factory por funcao

```python
def criar_servico_pagamento(tipo):
    if tipo == "cartao":
        return ServicoDeCartao()
    elif tipo == "pix":
        return ServicoDePix()
    else:
        raise ValueError("Tipo de pagamento inválido")
```

## 4. Pedido utilizando uma funcao

```python
class ServicoDePedido:
    def __init__(self, tipo_pagamento):
        self.pagamento = criar_servico_pagamento(
            tipo_pagamento
        )

    def finalizar_pedido(self, total):
        self.pagamento.processar(total)
```

Agora o pedido delega a criacao
para uma funcao externa.

## 5. Factory por classe

```python
class FabricaDePagamento:
    @staticmethod
    def criar(tipo):
        if tipo == "cartao":
            return ServicoDeCartao()
        elif tipo == "pix":
            return ServicoDePix()
        else:
            raise ValueError(
                "Tipo de pagamento inválido"
            )
```

## 6. Pedido utilizando a classe Factory

```python
class ServicoDePedido:
    def __init__(self, tipo_pagamento):
        self.pagamento = FabricaDePagamento.criar(
            tipo_pagamento
        )

    def finalizar_pedido(self, total):
        self.pagamento.processar(total)
```

## 7. Diferenca em relacao a Aula 12

Aula 12:
O pedido decide qual classe instanciar.

Aula 13:
A fabrica decide qual classe instanciar.

O pedido apenas utiliza o servico retornado.

## 8. Beneficios

- Criacao centralizada.
- Menor acoplamento da classe de pedido.
- Fabrica reutilizavel.
- Facilidade para substituir a fabrica nos testes.
- Maior previsibilidade ao adicionar tipos.

## 9. Limitacao

A Simple Factory ainda precisa ser
alterada quando um novo tipo de
pagamento e adicionado.

Por isso, a abordagem ainda
nao e totalmente extensivel.

## 10. Observacao da transcricao

O metodo processar pertence
ao servico de pagamento.

O metodo finalizar_pedido pertence
ao ServicoDePedido.

Por isso, no laboratorio,
chamamos finalizar_pedido no pedido,
nao no objeto de pagamento.

## 11. Relacao com outros padroes

Simple Factory e uma tecnica
de centralizacao de criacao.

Nao deve ser confundida automaticamente
com Factory Method do catalogo GoF.

## 12. Arquivos criados

src/aula13_simple_factory.py
aulas/aula13_simple_factory.py
tests/test_aula13_simple_factory.py
anotacoes/aula13_simple_factory.md
resultados/aula13_simple_factory.json

## 13. Proxima etapa

Estudar a melhoria de extensibilidade
apresentada na proxima aula da Alura.
