# Aula 12 - Criando objetos do jeito errado

## 1. Objetivo

Estudar problemas de criacao rigida de objetos
e o aumento do acoplamento entre classes.

Esta aula apresenta o problema.
A solucao com Factory ainda nao foi implementada.

## 2. Primeira versao: criacao rigida

```python
class ServicoDePagamento:
    def processar(self, valor):
        print(f"Pagamento de R$ {valor} processado.")


class ServicoDePedido:
    def __init__(self):
        self.pagamento = ServicoDePagamento()

    def finalizar_pedido(self, total):
        self.pagamento.processar(total)
```

A classe de pedido conhece diretamente
a implementacao do servico de pagamento.

Se quisermos utilizar PIX, precisaremos
modificar a implementacao do pedido.

## 3. Segunda versao: criacao condicional

```python
class ServicoDePedido:
    def __init__(self, tipo_pagamento="cartao"):
        if tipo_pagamento == "cartao":
            self.pagamento = ServicoDePagamento()
        elif tipo_pagamento == "pix":
            self.pagamento = ServicoDePix()
        else:
            raise ValueError("Tipo de pagamento inválido")
```

Agora existem dois meios de pagamento.

Entretanto, a classe de pedido continua
responsavel por escolher e criar os objetos.

## 4. Alto acoplamento

O acoplamento aparece porque
ServicoDePedido conhece concretamente
ServicoDePagamento e ServicoDePix.

Adicionar novos tipos significa
modificar o codigo de ServicoDePedido.

## 5. Baixa flexibilidade

A segunda implementacao suporta
cartao e PIX.

Se o projeto crescer e exigir diversos
meios de pagamento, sera necessario
expandir as condicoes.

## 6. Relacao com Dependency Injection

Na Aula 08, estudamos que uma classe
pode receber a dependencia pronta.

Aqui, a criacao ainda acontece
dentro da classe que a utiliza.

Portanto, a responsabilidade de criar
nao foi separada da responsabilidade
de processar o pedido.

## 7. Quando a abordagem simples funciona?

Conforme discutido na transcricao,
um projeto pequeno pode utilizar essa
estrutura sem grandes problemas.

Os padroes de projeto sao ferramentas
que devem ser escolhidas conforme
as necessidades e o crescimento do sistema.

## 8. Simulacao

Nenhum pagamento real e realizado.

As classes apenas imprimem mensagens
para demonstrar o fluxo do codigo.

## 9. Arquivos criados

src/aula12_criacao_objetos.py
aulas/aula12_criacao_objetos.py
tests/test_aula12_criacao_objetos.py
anotacoes/aula12_criacao_objetos.md
resultados/aula12_criacao_objetos.json

## 10. Proxima etapa

Estudar a proxima melhoria apresentada
pela Alura, sem antecipar implementacoes
que ainda nao foram abordadas.
