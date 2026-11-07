# Aula 26 - A camada semantica na arquitetura de dados

## Conceito

A camada semantica traduz as estruturas tecnicas
dos dados para conceitos padronizados de negocio.

Ela fica entre as fontes analiticas e os consumidores:
Business Intelligence, relatorios, dashboards
e analises de ciencia de dados.

## Problema que resolve

Equipes diferentes podem implementar
formulas diferentes para o mesmo indicador.

Exemplo:
Um relatorio calcula ticket medio por pedido.
Outro divide faturamento por linhas de produto.

Ambos chamam o resultado de ticket medio,
mas os valores podem divergir.

## Solucao

Centralizar:
- Metricas
- Dimensoes
- Regras de calculo
- Fontes de dados
- Unidades de medida

## Metricas da Minishop

Faturamento:
Soma do valor das vendas em centavos.

Pedidos:
Quantidade distinta de pedidos de venda.

Unidades:
Soma das quantidades vendidas.

Ticket medio:
Faturamento dividido pela quantidade
distinta de pedidos.

## Dimensoes

Cliente.
Produto.
Categoria.
Mes.

Nao adicionamos cidade, inadimplencia nem
cancelamentos porque essas informacoes nao
estao presentes no modelo analitico
usado neste laboratorio.

## Duas fontes, uma definicao

Lakehouse:
DuckDB consulta Parquet da Gold analitica.

Data Warehouse:
SQLite consulta fato_vendas
e dimensoes de cliente, produto e tempo.

A camada semantica converte os nomes
de negocio em consultas SQL apropriadas
para cada uma dessas estruturas.

## Ferramentas citadas pela aula

dbt Semantic Layer.
Cube.
AtScale.
Transform.
MetricFlow.
LookML.

Essas ferramentas nao sao instaladas
neste laboratorio. Implementamos o conceito
com Python, DuckDB e SQLite.

## Consistencia

A auditoria executa:
4 metricas x 5 formas de agrupamento
= 20 comparacoes entre Lakehouse e DW.

Agrupamentos:
Sem dimensao.
Cliente.
Produto.
Categoria.
Mes.

O contrato de negocio precisa produzir
o mesmo resultado em ambas as fontes,
desde que ambas representem o mesmo snapshot.

## Limitacoes

A interface semantica e local em Python.
Ainda nao ha:
- Servidor de metricas
- API HTTP para dashboards externos
- Autenticacao de consumidores
- Controle de acesso por linha
- Catalogo corporativo em nuvem

## Proxima aula

Consumo das metricas pelas ferramentas
de BI sobre DW e Lakehouse.
