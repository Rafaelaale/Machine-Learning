# Aula 20 - Criando o Data Lake no Minishop

## Objetivo

Aplicar a arquitetura Data Lake ao e-commerce.

Separar:
Ingestao dos dados operacionais.
Preparacao Silver.
Consolidacoes Gold.
Carga dimensional no Data Warehouse.

## Bronze

A Bronze preserva dados extraidos das tabelas.

Dominios:
Cliente.
Vendas.
Financeiro.
Logistica.

Os dados ficam em JSONL e o snapshot
SQLite original da Aula 17 e preservado.

O banco operacional nao e modificado.

## Silver

Clientes:
Dados disponiveis da origem.

Produto e Categoria:
Join previamente realizado.

Vendas:
Pedido + Item + Produto.
Somente pedidos confirmados e pagos.

Particoes:
ano=AAAA/mes=MM.

Financeiro:
Faturas preservadas sem inventar
vencimentos ou saldos.

Logistica:
Movimentos de estoque relacionados
aos pedidos.

## Parquet

Formato binario colunar.

Adequado a consultas analiticas.

Pode utilizar compressao Snappy.

A biblioteca pyarrow gera o arquivo real
se estiver instalada no ambiente.

Nao confundir extensao .parquet com
um arquivo CSV renomeado.

## Avro

Formato binario orientado a registros.

Usa esquema de serializacao.

A biblioteca fastavro gera o arquivo real
se estiver instalada no ambiente.

## Gold

Prepara indicadores mensais:
Pedidos distintos.
Itens vendidos.
Unidades.
Faturamento em centavos.

A Gold nao substitui o modelo
dimensional do Data Warehouse.

## Data Warehouse

O ETL da aula usa somente a Silver.

Reutiliza:
Dimensoes da Aula 15.
Politicas e fatos da Aula 16.

A fonte operacional nao participa
desse segundo fluxo.

## SCD Tipo 2

A dimensao cliente continua preparada
para historico com datas de vigencia.

O OLTP atual nao possui cidade,
estado ou data de nascimento.

Nao e possivel criar mudancas geograficas
historicas reais sem esses dados.

## Validacao

Verificacao de hashes SHA-256.

Reconciliacao Gold x DW.

Reprocessamento sem duplicacao.

Reconstrucao do DW sem OLTP original.

Preservacao dos snapshots anteriores.

## Limitacoes

Implementacao local e didatica.

Diretorios simulam zonas e buckets.

Nao utiliza S3, Azure Data Lake ou GCS.

Nao implementa catalogo corporativo,
permissoes distribuidas ou governanca.

A data de movimento de estoque e derivada
da data de pedido, pois nao existe campo
independente no OLTP atual.

O fato financeiro continua limitado
pela ausencia de dados de vencimento.

## Proxima aula

Conceito de Lakehouse.
