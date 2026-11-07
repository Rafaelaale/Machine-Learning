# Aula 12 - Lookup e Surrogate Keys

## Chave natural

Identificador recebido do sistema de origem.

Exemplos:
23400
02342
56700

Codigos com zero a esquerda devem
ser preservados como texto.

## Surrogate Key

Identificador interno do Data Warehouse.

Normalmente e um inteiro gerado
automaticamente.

A chave natural permite localizar
o registro de origem.

A surrogate key permite relacionar
os fatos com as dimensoes.

## Lookup de dimensao

Consultar codigo natural.

Se nao existir:
criar membro e gerar nova SK.

Se existir:
localizar SK e aplicar a politica
de atualizacao da dimensao.

## Slowly Changing Dimension Tipo 1

Quando os atributos mudam:
atualizar o registro existente.

A SK continua a mesma.

O historico anterior do atributo
nao e mantido nessa dimensao.

## Slowly Changing Dimension Tipo 2

Quando atributos relevantes mudam:
criar uma nova versao.

O codigo natural pode se repetir
em versoes diferentes.

Cada versao possui uma SK diferente.

Esse comportamento ja foi implementado
no laboratorio da Aula 11.

## Lookup de fato

A fonte fornece codigos naturais.

O processo ETL localiza a SK do cliente
e a SK do produto.

A tabela fato guarda as SKs como FKs.

Nao inserir fatos com dimensoes ausentes
sem uma politica explicita de tratamento.

## Sobre atualizacao desnecessaria

A transcricao descreve uma estrategia de
atualizar atributos mesmo quando iguais.

Neste laboratorio, verificamos se houve
mudanca para evitar gravacoes desnecessarias.

Ambas sao possibilidades de implementacao.

## Cenario didatico

Carga inicial:
3 clientes.

Segunda carga:
1 saldo alterado;
1 nome alterado;
1 cliente sem alteracoes;
1 cliente novo.

As vendas ilustrativas sao separadas
dos dados operacionais da Minishop.

## Limites

Este laboratorio usa SCD Tipo 1.

Nao altera o DW SCD Tipo 2 da Aula 11.

As chaves substitutas sao geradas
automaticamente pelo SQLite.

O desempenho de joins nao foi medido.

## Proxima aula

Aprofundar os mecanismos de atualizacao
de dimensoes e historico do ETL.
