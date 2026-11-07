# Aula 08 - Criando o DW da Minishop

## Objetivo

Construir a matriz dimensao-indicador,
relacionando indicadores de negocio
com as perspectivas de analise.

## Indicadores de vendas

- Quantidade vendida
- Preco medio unitario
- Valor vendido

Cruzamentos pretendidos:
tempo, cliente, produto, categoria,
cidade, estado, faixa etaria,
canal de acesso e promocao.

## Indicador de inventario

- Saida de inventario

Cruzamentos:
tempo, produto e categoria.

Saida de inventario nao deve ser
confundida com quantidade vendida
sem validacao dos movimentos reais.

## Indicadores financeiros

- Valor a cobrar
- Valor em mora

Cruzamentos:
tempo, cliente, cidade, estado,
faixa etaria e faixas de vencimento.

## Aging List

Classifica contas a receber
segundo o tempo ate o vencimento
ou o tempo de atraso.

Faixas iniciais:
0 a 15 dias;
16 a 30 dias;
31 a 60 dias;
mais de 60 dias.

A classificacao deve considerar
data de referencia e saldo em aberto.

## Dados ainda ausentes

- Endereco estruturado
- Data de nascimento
- Canal da compra
- Promocao na data da venda
- Vencimento da fatura
- Saldo financeiro em aberto
- Fatos de movimentacao de estoque

Esses dados nao devem ser inventados.

## Estado do laboratorio

Disponivel:
Consultas analiticas de vendas
por tempo, cliente, produto e categoria.

Pendente:
Indicadores financeiros, inventario
e dimensoes ainda sem dados.

Nao aplicavel:
Cruzamentos sem finalidade gerencial
na matriz de negocio definida.

## Granularidade

A fato_vendas da Aula 06 representa
cada produto de um pedido confirmado
e pago, dentro de um lote de carga.

A consulta usa o lote mais recente
para nao somar fotografias repetidas.

## Preco medio

Preco medio unitario ponderado:

soma(valor_centavos) / soma(quantidade)

Nao somar precos medios individuais.

## Proxima etapa

Continuar a modelagem do Data Warehouse
e definir as dimensoes e fatos fisicos.
