# Aula 11 - Funcionalidades da OpenMetadata

## Objetivo

Conhecer as funcionalidades da OpenMetadata
para exploracao, governanca e linhagem de dados.

## Sandbox do curso

https://sandbox.open-metadata.org/

## Exemplo apresentado pelo instrutor

Tabela: customers_clean

Caminho apresentado:
RedshiftProd / dev / demo_dbt_jaffle / customers_clean

A disponibilidade atual da tabela nao foi verificada.

## Schema

Apresenta nomes, tipos, descricoes, tags
e termos de glossario associados aos campos.

## Activity Feeds & Tasks

Permite examinar historicos de atividades
e tarefas relacionadas aos ativos.

## Sample Data

Exibe exemplos de registros das tabelas.

O instrutor demonstra a visualizacao
de campos de nomes mascarados.

## Queries

Consulta comandos SQL associados
aos ativos de dados.

## Profiler & Data Quality

Apresenta indicadores estatisticos, como:

- Quantidade de linhas.
- Quantidade de colunas.
- Percentual de valores nulos.
- Valores distintos.
- Unicidade.
- Indicadores e regras de qualidade.

No exemplo do curso, customer_id apresenta
100% de valores distintos e nenhum nulo.

## Lineage

Permite examinar as origens, transformacoes
e destinos das informacoes.

A funcionalidade sera aprofundada
na proxima aula.

## Custom Properties

Permite trabalhar com propriedades
adicionais associadas aos metadados.

## Laboratorio complementar

Usamos a tabela sor_assinantes da Aula 04.

O programa realiza:

- Leitura do esquema SQLite.
- Perfil estatistico por coluna.
- Mascaramento de uma amostra.
- Criacao de catalogo local em JSON.
- Exportacao de relatorios CSV.

Nao existe conexao entre o laboratorio
e a API oficial do OpenMetadata.

As classificacoes sao apenas didaticas.

## Aprendizado principal

Um catalogo de metadados facilita
a descoberta, compreensao, documentacao
e avaliacao da qualidade dos ativos de dados.

A linhagem acrescenta a rastreabilidade
das origens e transformacoes.