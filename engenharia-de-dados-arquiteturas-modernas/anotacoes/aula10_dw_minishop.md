# Aula 10 - Continuando a criacao do DW da Minishop

## Objetivo

Concluir a proposta dimensional do DW,
agrupando hierarquias e separando fatos.

## Dimensao Cliente - Estrela

Nivel folha: Cliente.

Hierarquia conceitual:
Estado > Cidade > Cliente.

Faixa etaria:
Atributo derivado da data de nascimento.

Dados geograficos e demograficos ainda
nao existem no OLTP implementado.
No laboratorio ficam NULL.

## Dimensao Produto - Snowflake

Nivel folha: Produto.
Nivel superior: Categoria.

A tabela dim_produto referencia dim_categoria.

## Promocao e Acesso

Dimensoes independentes.

Nao ha hierarquia entre promocao
e canal de acesso.

Como o OLTP nao possui esses campos,
suas chaves ficam NULL na fato de vendas.

## Dimensao Tempo

Nivel folha: Data.

Atributos:
Dia, mes, trimestre, semestre e ano.

Cada data possui uma chave substituta.

## Aging List

Classificacao de contas a receber
segundo dias para vencer ou dias em atraso.

Faixas:
0-15, 16-30, 31-60, 61+.

Sem data de vencimento e saldo em aberto,
nao e possivel calcular valores financeiros.

## Fato 1: Vendas

Dimensoes:
Cliente, Produto, Tempo,
Promocao e Acesso.

Medidas:
Quantidade
Preco medio unitario
Valor total

Grao implementado:
Um produto por pedido confirmado e pago.

Numero de pedido:
Dimensao degenerada.

## Fato 2: Inventario

Dimensoes:
Produto e Tempo.

Medida:
Saida de estoque, valor negativo.

Grao:
Produto por dia.

A carga utiliza movimentos reais do OLTP.

## Fato 3: Financeiro

Dimensoes:
Cliente, Aging List e Tempo.

Medidas planejadas:
Valor a receber.
Valor em atraso.

A tabela fisica existe, mas nao possui
linhas por falta de dados suficientes.

## Modelagem mista

Cliente: Estrela.
Produto: Snowflake.

Todos os fatos utilizam chaves
substitutas das dimensoes.

## Decisoes de modelagem

A combinacao de chaves de dimensoes
nao identifica necessariamente um
pedido individual de forma unica.

A fato de vendas mantem o numero do
pedido para preservar seu grao detalhado.

As chaves substitutas pertencem
as dimensoes; nos fatos atuam como FKs.

## ETL

Extract: Extrair.
Transform: Transformar.
Load: Carregar.

O ETL nao e apenas copiar arquivos:
envolve validacao, padronizacao,
regras de negocio e integracao.

## Proxima aula

Processo de ETL do Data Warehouse.
