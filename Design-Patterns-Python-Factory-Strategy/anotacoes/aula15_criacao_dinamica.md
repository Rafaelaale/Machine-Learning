# Aula 15 - Criacao dinamica

## Objetivo

Escolher uma Factory Method durante
a execucao do programa.

A escolha pode vir de input(), JSON
ou de uma requisicao de usuario.

Nesta aula, o exemplo pratico
usa input() e um mapa de classes.

## 1. Reutilizacao do Factory Method

As seguintes classes ja existem
na Aula 14:

- PedidoPixFactory
- PedidoCartaoFactory
- PedidoBoletoFactory

Elas implementam o metodo
criar_pagamento().

## 2. Problema da escolha dinamica

Quando a pessoa escolhe o pagamento,
o programa ainda precisa determinar
qual Factory instanciar.

A primeira solucao usa if/elif.

## 3. Selecao condicional

```python id="blitc1"
if tipo == "pix":
    pedido = PedidoPixFactory()
elif tipo == "cartao":
    pedido = PedidoCartaoFactory()
elif tipo == "boleto":
    pedido = PedidoBoletoFactory()
else:
    raise ValueError("Tipo de pagamento inválido")
```

O problema e o crescimento das
condicoes para cada nova Factory.

## 4. Mapa com dicionario

```python id="zvr1vb"
MAPA_PEDIDOS = {
    "pix": PedidoPixFactory,
    "cartao": PedidoCartaoFactory,
    "boleto": PedidoBoletoFactory,
}
```

As classes sao guardadas como valores.

A chave e o tipo de pagamento.

## 5. Criacao dinamica

```python id="h9ca9h"
classe_pedido = MAPA_PEDIDOS.get(tipo)

if not classe_pedido:
    raise ValueError("Tipo inválido")

pedido = classe_pedido()
pedido.finalizar_pedido(100)
```

A classe concreta e selecionada
e instanciada somente durante
a execucao.

## 6. Entrada do usuario

```python id="tkp5op"
tipo = input("Tipo de pagamento: ")
```

No laboratorio, input e simulado
para permitir testes automatizados.

Tambem existe um modo interativo
opcional, iniciado com:

python aulas/aula15_criacao_dinamica.py --interativo

## 7. Beneficio

O dicionario permite localizar
a Factory por chave, evitando
uma longa estrutura condicional.

## 8. Limitacao

Para adicionar um novo pagamento,
ainda precisamos alterar MAPA_PEDIDOS.

Isso significa que o registro
das Factories continua centralizado.

Nao implementamos registro automatico
ou outro padrao nesta aula.

## 9. Diferenca entre classes e instancias

MAPA_PEDIDOS["pix"] guarda
PedidoPixFactory, a classe.

Ao executar:

MAPA_PEDIDOS["pix"]()

criamos uma instancia dessa classe.

## 10. Pagamentos simulados

Os metodos processar() apenas
imprimem mensagens.

Nenhum pagamento real e realizado.

## 11. Arquivos desta aula

src/aula15_criacao_dinamica.py
aulas/aula15_criacao_dinamica.py
tests/test_aula15_criacao_dinamica.py
anotacoes/aula15_criacao_dinamica.md
resultados/aula15_criacao_dinamica.json

## 12. Proxima etapa

Estudar o proximo padrao apresentado
pela Alura para melhorar a extensibilidade.
