# Aula 04 - Criando o OLTP da Minishop

## Objetivo

Definir as entidades, atributos, relacoes e
regras do negocio antes de criar tabelas SQL.

## Modelo Entidade-Relacionamento de Chen

Entidades:
Representam elementos do negocio.

Atributos:
Descrevem caracteristicas das entidades.

Relacionamentos:
Expressam associacoes entre entidades.

Cardinalidade:
Define o numero minimo e maximo de
ocorrencias associadas a cada entidade.

## Entidades identificadas

Cliente
Pedido
Item de pedido
Produto
Categoria
Inventario
Movimento de inventario
Fatura

O pagamento foi mantido no catalogo porque
ja integra o escopo operacional da Minishop.

## Relacoes de negocio

Cliente faz pedido.
Pedido contem item.
Item referencia produto.
Produto pertence a categoria.
Produto possui inventario.
Item gera movimento de inventario.
Pedido gera fatura.
Pedido possui pagamento.

## Cardinalidades e requisitos

As cardinalidades precisam refletir
as regras efetivas do negocio.

Exemplo:

Um cliente pode possuir zero ou varios
pedidos caso o cadastro seja permitido
antes da primeira compra.

Um pedido confirmado precisa possuir
itens e respeitar o estoque.

Um pedido pendente pode nao ter fatura.

## Validacao com usuarios

Entrevistar usuarios-chave.
Identificar entidades e verbos.
Registrar atributos.
Definir cardinalidades.
Apresentar o modelo.
Corrigir inconsistencias.
Obter aprovacao.

## Modelo conceitual versus logico

Conceitual:
Entidades, atributos e relacionamentos
independentes da tecnologia.

Logico:
Tabelas, colunas, chaves e restricoes.

Fisico:
Implementacao no SGBD escolhido.

## Observacao

Aula centrada na modelagem conceitual.

Nao modificamos o banco de dados da
Aula 01 nem o ambiente OLAP.

O catalogo ainda nao foi aprovado
por usuarios reais da empresa ficticia.

## Proxima aula

Transformar o modelo conceitual em
estrutura relacional.
