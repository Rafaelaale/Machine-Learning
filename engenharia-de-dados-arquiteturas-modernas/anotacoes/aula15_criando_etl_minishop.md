# Aula 15 - Criando ETL do Minishop

## Objetivo

Projetar o processo ETL do MiniShop e definir
as politicas dimensionais antes da orquestracao.

## Tres abordagens de ETL

### Procedures SQL

Vantagens:
Processamento proximo aos dados.
Pode ter alto desempenho na mesma plataforma.

Desvantagens:
Complexidade das transformacoes em SQL procedural.
Menor flexibilidade para fontes externas.

### Programa Python, Java ou C#

Vantagens:
Flexibilidade.
Facilidade para incorporar APIs e arquivos.
Testabilidade e modularizacao.

Desvantagens:
Lookups, logs, politicas de carga e
agendamento precisam ser implementados.

### Ferramenta ETL especializada

Vantagens:
Conectores prontos.
Transformacoes.
Monitoramento.
Orquestracao e escalabilidade.

Desvantagens:
Custos possiveis.
Aprendizagem da ferramenta.
Dependencia de fornecedor.

## Escolha para o laboratorio

Python e SQLite.

A orquestracao completa das tabelas de fatos
sera tratada na proxima etapa do curso.

## Cliente: SCD Tipo 2

Atributos historicos:
Cidade.
Estado.
Faixa etaria.

Campos:
cliente_sk
cod_cliente
nome_cliente
cod_cidade
nome_cidade
cod_estado
nome_estado
faixa_etaria
valid_from
valid_to

Uma chave natural pode ter varias
surrogate keys ao longo do tempo.

O periodo e definido como:
valid_from inclusivo;
valid_to exclusivo.

NULL em valid_to significa versao atual.

## Nome do cliente

Neste laboratorio, uma correcao de nome
usa politica Tipo 1 na versao corrente.

## Produto: SCD Tipo 1

Uma chave natural por produto.

Alteracoes de nome ou categoria
mantem a mesma surrogate key.

A categoria permanece em tabela separada
para praticar a modelagem snowflake.

## Promocao: SCD Tipo 1

Sem historico dimensional nesta etapa.

Nao existe fonte de promocoes no
OLTP atual da Minishop.

## Tempo: SCD Tipo 1

Chave deterministica AAAAMMDD.

Uma data corresponde a uma unica SK.

## Integracao com OLTP

O banco da Aula 05 possui:
Clientes.
Produtos.
Categorias.
Pedidos.
Pagamentos.

Ele nao possui:
Cidade de residencia.
Estado.
Data de nascimento.
Historico de mudancas geograficas.
Promocao associada ao pedido.

Esses dados nao devem ser inventados.

## Lookup historico

O lookup da dimensao cliente deve
considerar codigo natural e data do fato.

SELECT cliente_sk
FROM dim_cliente
WHERE cod_cliente = ?
AND valid_from <= ?
AND (valid_to IS NULL OR ? < valid_to);

## Limites

A carga real deste laboratorio popula
as dimensoes com informacoes disponiveis.

Mudancas historicas de cidade e estado
sao demonstradas nos testes.

A API registrar_cliente exige uma data efetiva
de mudanca conhecida e processa em ordem.

Nao suporta inserir uma versao SCD2
retroativamente entre versoes ja existentes.

A orquestracao dos fatos, monitoramento
e agendamento sera aprofundada depois.

## Proxima aula

Orquestrar a transferencia do OLTP
para o Data Warehouse.
