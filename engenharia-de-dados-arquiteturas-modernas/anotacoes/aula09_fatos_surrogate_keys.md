# Aula 09 - Transformando matriz em tabelas de fatos

## Objetivo

Entender como a matriz dimensao-indicador
determina agrupamentos de indicadores e
possiveis tabelas de fatos.

## Agrupamentos

Indicadores com dimensoes e granularidades
compativeis podem compartilhar um fato.

Nao basta ter dimensoes parecidas:
tambem devem representar o mesmo processo
de negocio e o mesmo nivel de detalhe.

Na Minishop, os assuntos previstos sao:
- Vendas
- Inventario
- Financeiro

Nesta aula implementamos vendas.
Inventario e financeiro continuam pendentes.

## Granularidade

A granularidade define o significado
de uma unica linha da tabela de fatos.

Fato detalhado:
uma linha por item de pedido.

Fato consolidado:
uma linha por data, cliente e produto.

O fato consolidado soma medidas aditivas,
mas deixa de identificar cada pedido.

## Dimensao degenerada

E um identificador de evento armazenado
na propria tabela de fatos, sem dimensao propria.

Exemplo:
numero do pedido.

A decisao de mante-lo depende da
necessidade de rastreabilidade analitica.

## Chave substituta

Surrogate Key ou SK:
identificador interno do Data Warehouse.

Exemplo:
cliente_sk = 1

A chave de origem tambem permanece
armazenada na dimensao para rastreamento.

## Chave composta

A tabela fato_vendas_resumo usa:
tempo_sk + cliente_sk + produto_sk

Essa combinacao identifica unicamente
cada agregado do laboratorio.

A tabela detalhada usa o numero do pedido
e a SK do produto para identificar o item.

## Dimensao tempo

No modelo novo, tempo_sk e a chave primaria.

A data de calendario permanece como atributo.

## Medidas aditivas

Quantidade e faturamento podem ser somados.

Preco medio unitario nao deve ser somado.

Formula correta:
SUM(valor_centavos) / SUM(quantidade)

## Cuidados de arquitetura

As chaves substitutas sao criadas
somente no novo Data Warehouse.

O DW da Aula 06 nao e alterado.

Para historico dimensional do tipo SCD,
seriam necessarias regras adicionais
de versionamento e vigencia das SKs.

A tabela agregada nao substitui a detalhada
quando rastreabilidade por pedido for exigida.

## Proxima etapa

Aplicar o modelo dimensional da Minishop
conforme a continuacao da trilha.
