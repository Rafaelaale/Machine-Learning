# Aula 03 - Como nascem novas bases

## Conceito principal

Organizacoes data-driven frequentemente criam
novos ativos de dados a partir de bases existentes.

O volume de novas bases pode crescer mais rapido
do que a documentacao de suas origens.

Isso torna a linhagem importante para a governanca.

## Exemplo apresentado na Alura

Uma empresa de avaliacao de ativos financeiros
possui assinantes de uma newsletter mensal.

O marketing deseja identificar antigos clientes
que mantiveram uma assinatura por 1 a 3 meses.

## Base original

- Assinantes cadastrados

## Tres novas bases

1. Clientes ativos.
2. Clientes inativos.
3. Clientes que ficaram ativos entre 1 e 3 meses
   e depois cancelaram a assinatura.

## Linhagem

Uma origem alimenta tres transformacoes.

Cada transformacao produz uma base derivada
que pode atender a uma finalidade de negocio.

## Laboratorio complementar

Implementamos o exemplo em Python e SQLite.

A base de origem possui oito clientes ficticios.

Foram criadas tres VIEWs SQL e exportados
arquivos CSV para representar seus resultados.

A definicao de meses completos de calendario
e um criterio adotado neste laboratorio.
O material da aula nao especifica o calculo exato.

## Aprendizado

Nao basta criar novas bases.

Tambem precisamos documentar de onde os dados
vieram, quais regras foram aplicadas e quais
ativos de dados foram produzidos.