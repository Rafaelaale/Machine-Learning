# Aula 21 - Introducao ao Lakehouse

## Objetivo

Entender a convergencia entre Data Lake
e Data Warehouse.

## Data Warehouse

Modelo analitico estruturado.

Possui:
Tabelas de dimensao.
Tabelas de fato.
Regras de negocio.
Consultas SQL.
Indicadores para Business Intelligence.

## Data Lake

Armazena dados em diferentes formatos.

Permite preservar dados brutos.

Pode organizar dados nas camadas:
Bronze.
Silver.
Gold.

## Lakehouse

Abordagem que combina vantagens do
Data Lake e do Data Warehouse.

A proposta e permitir consultas
analiticas e estruturas de tabelas
sobre os dados armazenados no Lake.

Pode reduzir duplicacao de dados e
movimentacoes desnecessarias.

## Laboratorio

As camadas existentes sao preservadas.

A Silver fornece:
Clientes.
Produtos e categorias.
Vendas.
Movimentos de estoque.

O Python interpreta esses arquivos e
os disponibiliza em um SQLite em memoria.

Consultamos:
Quantidade de vendas.
Faturamento.
Produtos.
Clientes.
Totais mensais.

O SQLite nao e salvo no disco.

## SQL sobre o Lake

Exemplo:

SELECT
    produto_id,
    SUM(quantidade) AS unidades,
    SUM(valor_total_centavos) AS faturamento
FROM vendas
GROUP BY produto_id;

## Reconciliacao

Os indicadores SQL da Silver sao
comparados aos indicadores Gold.

Ambos devem refletir o mesmo snapshot.

## Versionamento didatico

O Data Lake da Minishop preserva
diferentes snapshots de origem.

Um snapshot anterior pode continuar
disponivel depois de novas vendas.

Isso NAO equivale ao versionamento
transacional de tabelas de um Lakehouse.

## Lakehouse de producao

Tecnologias que podem ser estudadas:
Apache Iceberg.
Delta Lake.
Apache Hudi.

Recursos importantes:
Metadados de tabelas.
Evolucao de esquema.
Transacoes ACID.
Versionamento de tabelas.
Time travel quando suportado.
Controle de concorrencia.

Nenhum desses formatos de tabela
foi implementado nesta aula.

## Limites da demonstracao

O SQLite em memoria copia os registros
da Silver para executar consultas SQL.

Nao consulta Parquet diretamente.

Nao oferece transacoes distribuidas
sobre arquivos do Lake.

Nao substitui uma engine corporativa
de consultas sobre Data Lake.

O objetivo deste video da Alura e
introduzir o conceito arquitetural.

## Proxima aula

Aprofundar a arquitetura Lakehouse e
seus principais componentes.
