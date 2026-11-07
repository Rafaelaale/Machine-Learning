# Aula 02 - O que e OLAP?

## Definicao

OLAP significa Online Analytical Processing.

Seu objetivo e analisar dados, identificar
tendencias e apoiar decisoes de negocio.

## Diferencas

OLTP:
- Operacoes individuais.
- Muitas escritas e atualizacoes.
- Foco em consistencia transacional.
- Consultas por identificador.
- Dados frequentemente normalizados.

OLAP:
- Consultas analiticas.
- Agregacoes e comparacoes.
- Leitura intensiva.
- Dados historicos.
- Estruturas orientadas a analise.

## Exemplo Minishop

OLTP:
Registrar o pedido de um cliente.

OLAP:
Calcular o faturamento mensal da empresa.

## Modelo dimensional inicial

Tabela de fatos:
- fato_vendas

Tabelas de dimensao:
- dim_clientes
- dim_produtos
- dim_tempo

Grao da tabela de fatos:
Uma linha por item de pedido confirmado e pago.

## Metricas

Faturamento:
Soma do valor dos itens vendidos.

Ticket medio:
Faturamento dividido pelo numero de pedidos.

Unidades vendidas:
Soma das quantidades dos itens.

## Separacao dos ambientes

O banco de origem e aberto somente para leitura.

O ambiente analitico e gravado em outro arquivo.

A carga cria uma fotografia dos dados disponiveis.

Novas vendas exigem nova carga para aparecer
nos indicadores.

## Limites do exemplo

O banco ainda nao possui categoria, regiao
ou historico de varios anos.

Nao podemos calcular lucro ou rentabilidade,
pois nao ha dados de custos.

SQLite e usado apenas como laboratorio local.

A carga e integral, nao incremental.

A demonstracao nao comprova desempenho
em grandes volumes ou sob concorrencia real.

## Proxima etapa

Comparar estruturalmente as caracteristicas
de OLTP e OLAP e evoluir a arquitetura.
