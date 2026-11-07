# Aula 07 - Transformando matriz em tabelas

## Objetivo

Transformar uma modelagem dimensional
conceitual em estruturas fisicas de banco.

## Modelo estrela

Atributos e hierarquias podem ficar
na mesma tabela de dimensao.

Exemplo:
estrela_dim_produtos

Colunas:
produto_id
produto_nome
categoria

Vantagens:
- Consultas mais simples.
- Menos joins.
- Interpretacao facilitada.

Desvantagem:
- Redundancia de atributos dimensionais.

## Modelo Snowflake

Normaliza partes da dimensao em
tabelas relacionadas.

Exemplo:
snow_dim_produtos
snow_dim_categorias

Vantagens:
- Menor repeticao de dados dimensionais.
- Hierarquias explicitadas em tabelas.

Desvantagens:
- Mais joins.
- Consultas mais complexas.

Menos joins nao garante automaticamente
melhor desempenho em todo banco e consulta.

## Hierarquia regular

Todos os elementos percorrem os mesmos
niveis ate o topo.

Exemplo:
Brasil > Bahia > Salvador

## Hierarquia irregular

Alguns elementos nao possuem todos
os niveis intermediarios.

Exemplo:
Monaco > Monaco

Nesse caso, nao ha estado intermediario.

Hierarquias irregulares tambem podem ser
modeladas com nulos ou tabelas auxiliares,
dependendo das regras adotadas.

## Modelo pai-filho

Representa a ligacao de cada elemento
com seu elemento superior.

Colunas:
no_id
nome
tipo
pai_id

Uma CTE recursiva permite reconstruir
os caminhos hierarquicos.

## Aplicacao na Minishop

Fonte:
Data Warehouse da Aula 06.

Modelos:
estrela e snowflake.

Fato:
vendas.

Dimensoes:
clientes e produtos.

Categoria:
desnormalizada na estrela;
normalizada no snowflake.

As duas estruturas precisam apresentar
os mesmos indicadores para os mesmos dados.

## Limites

A demonstracao utiliza pequeno volume
de vendas e nao compara desempenho real.

A geografia e apenas um exemplo didatico,
sem vinculacao com os clientes da Minishop.

Nenhum banco anterior e modificado.

## Proxima etapa

Continuar a implementacao da modelagem
dimensional e o desenho do Data Warehouse.
