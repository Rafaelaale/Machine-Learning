# Aula 05 - Continuando a criacao do OLTP

## Objetivo

Transformar o modelo conceitual da Minishop
em um modelo logico relacional.

## Regras de transformacao

1. Entidades se tornam tabelas.
2. Atributos se tornam colunas.
3. Identificadores se tornam chaves primarias.
4. Relacoes 1:N recebem chave estrangeira no lado N.
5. Relacoes 1:1 podem utilizar UNIQUE.
6. Chaves compostas podem identificar registros.

## Exemplos

Cliente 1:N Pedido:
pedidos.cliente_id referencia clientes.cliente_id.

Categoria 1:N Produto:
produtos.categoria_id referencia categorias.categoria_id.

Pedido 1:N Item:
itens_pedido.pedido_id referencia pedidos.pedido_id.

Produto 1:N Item:
itens_pedido.produto_id referencia produtos.produto_id.

## Chave primaria composta

Tabela itens_pedido:

PRIMARY KEY (pedido_id, produto_id)

No modelo desta aula, o mesmo produto nao pode
aparecer duas vezes no mesmo pedido.

## Fatura

Uma fatura possui seu identificador proprio.

A coluna pedido_id e unica, estabelecendo
no maximo uma fatura por pedido.

## Estoque

A tabela estoque registra a quantidade atual.

A tabela movimentos_estoque registra uma
saida associada ao item vendido.

## Observacao sobre o laboratorio

O esquema desta aula e uma nova demonstracao.

Nao alteramos os bancos anteriores.

A venda, a fatura e o pagamento sao simulados
na mesma transacao local.

Em sistemas reais, pagamentos externos exigem
tratamento adicional.

## Decisoes ainda pendentes

O modelo ainda precisa considerar regras
especificas de devolucao, multiplos depositos,
faturamento e integracao financeira.

## Proximo passo

Evoluir a arquitetura de dados a partir
do OLTP formalizado.
