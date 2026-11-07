# Aula 14 - Factory Method

## Objetivo

Evoluir da Simple Factory para um padrao
que permita adicionar novos tipos de
pagamento criando subclasses.

## 1. Problema da Simple Factory

Na Aula 13, a fabrica possuia if/elif.

Adicionar boleto exigiria editar
a fabrica existente.

## 2. Factory Method

O padrao define uma interface de criacao.

As subclasses decidem qual produto
concreto sera instanciado.

## 3. Criador abstrato

```python
from abc import ABC, abstractmethod

class ServicoDePedidoFactory(ABC):
    @abstractmethod
    def criar_pagamento(self):
        pass

    def finalizar_pedido(self, total):
        pagamento = self.criar_pagamento()
        pagamento.processar(total)
```

criar_pagamento e o Factory Method.

finalizar_pedido e o algoritmo comum.

## 4. Produtos concretos

PagamentoCartao:
processa pagamentos simulados no cartao.

PagamentoPix:
processa pagamentos simulados via PIX.

## 5. Criadores concretos

```python
class PedidoCartaoFactory(ServicoDePedidoFactory):
    def criar_pagamento(self):
        return PagamentoCartao()


class PedidoPixFactory(ServicoDePedidoFactory):
    def criar_pagamento(self):
        return PagamentoPix()
```

## 6. Utilizacao

```python
pedido1 = PedidoPixFactory()
pedido1.finalizar_pedido(250)

pedido2 = PedidoCartaoFactory()
pedido2.finalizar_pedido(180)
```

## 7. Extensao sem modificar implementacoes

No laboratorio, adicionamos:

PagamentoBoleto
PedidoBoletoFactory

Nao foi necessario modificar
ServicoDePedidoFactory nem as fabricas
de PIX e cartao.

Este e um exemplo de extensibilidade
pelo principio Open/Closed.

## 8. Principio Open/Closed

Aberto para extensao.
Fechado para modificacao.

Podemos acrescentar comportamentos
por meio de novas classes.

## 9. Beneficios

- Maior extensibilidade.
- Menor dependencia de produtos concretos.
- Reutilizacao do metodo finalizar_pedido.
- Organizacao da criacao por subclasses.

## 10. Limitacoes

- Aumento do numero de classes.
- Mais linhas de codigo para manter.
- Camada extra de abstracao.
- Requer compreender heranca e polimorfismo.

## 11. Diferenca para Simple Factory

Simple Factory:
uma funcao ou classe decide por if/elif.

Factory Method:
as subclasses implementam o metodo
responsavel pela criacao.

## 12. Limite desta aula

As fabricas concretas sao conhecidas
pelo codigo que as instancia.

Ainda nao implementamos uma selecao
dinamica a partir de JSON ou entrada
do usuario. Esse sera outro problema.

## 13. Arquivos

src/aula14_factory_method.py
aulas/aula14_factory_method.py
tests/test_aula14_factory_method.py
anotacoes/aula14_factory_method.md
resultados/aula14_factory_method.json

## 14. Proxima etapa

Continuar a aula seguinte da Alura,
que abordara a selecao dinamica
da implementacao de pagamento.
