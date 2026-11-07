# Aula 13 - Slowly Changing Dimensions

## Objetivo

Estudar o tratamento de alteracoes nos
atributos das dimensoes do Data Warehouse.

## SCD Tipo 1

Sobrescreve um atributo existente.

A surrogate key nao muda.
O historico antigo deixa de ser distinguido
pelo valor anterior do atributo.

Exemplo:
Niteroi passa a Santos.
Todas as vendas aparecem em Santos.

Aplicacao comum:
Correcao ortografica sem relevancia historica.

## SCD Tipo 2

Preserva varias versoes de um mesmo membro.

Cada versao recebe uma nova surrogate key.

A chave natural continua a mesma.

Campos:
cliente_sk
codigo_natural
cidade
inicio
fim
atual

## SCD Tipo 3

Guarda o valor atual e um historico limitado,
geralmente uma coluna de valor anterior.

Conceito apenas documentado nesta aula.

## IsCurrent / Atual

O sinalizador identifica a versao corrente.

Pode servir para cargas de eventos atuais.

Nao e suficiente para identificar a versao
correta em cargas retroativas.

## Datas de vigencia

Este laboratorio usa:
inicio inclusivo
fim exclusivo

Exemplo:

Niteroi:
inicio = 1900-01-01
fim = 2024-05-01

Santos:
inicio = 2024-05-01
fim = NULL

Logo, uma venda em 2024-04-30 usa Niteroi
e uma venda em 2024-05-01 usa Santos.

Este criterio evita datas sobrepostas.

## Lookup historico

SELECT cliente_sk
FROM cliente_scd2
WHERE codigo_natural = ?
AND inicio <= data_evento
AND (fim IS NULL OR data_evento < fim)

## Exemplo numerico

Janeiro a abril de 2024:
4 vendas de R$ 10 em Niteroi.

Maio de 2024:
1 venda de R$ 15 em Santos.

Carga retroativa:
Dezembro de 2023, R$ 10 em Niteroi.

Total:
R$ 65.

SCD Tipo 1:
Santos = R$ 65.

SCD Tipo 2:
Niteroi = R$ 50.
Santos = R$ 15.

## Limites

A mudanca de cidade e uma simulacao didatica.

Para historico real, precisamos conhecer
a data efetiva em que a mudanca ocorreu.

Alteracoes retroativas nas proprias dimensoes
exigem politica adicional de reprocessamento.

A implementacao nao cobre exclusoes,
mudancas retroativas das vigencias e
reorganizacao de historicos complexos.

## Proxima etapa

Dimensao Tempo e politicas de carga no ETL.
