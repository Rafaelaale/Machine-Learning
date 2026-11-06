# Aula 12 - Linhagem de dados na OpenMetadata

## Objetivo

Compreender a visualizacao de linhagem de dados
por tabela e por coluna utilizando OpenMetadata.

## 1. Exemplo do instrutor

Tabela: customers_clean

A ferramenta mostra bases de origem e produtos
que dependem dessa tabela.

## 2. Upstream

Representa as origens dos dados.

No exemplo da Alura aparecem ativos como:

- raw_customers
- raw_orders
- raw_payments
- customers
- New Orders
- json_schema_record

Esses ativos estao relacionados por processos
e transformacoes apresentados no curso.

## 3. Downstream

Representa os destinos e consumidores dos dados.

O instrutor demonstra exemplos com:

- Looker
- Power BI
- Tableau

Dashboards podem depender de tabelas e de
outros produtos de dados.

## 4. Linhagem por tabela

Mostra quais tabelas alimentam outras tabelas
e quais ativos dependem delas.

## 5. Linhagem por coluna

Permite examinar dependencias de campos
especificos entre os ativos.

O painel Edge Information apresenta
informacoes sobre as ligacoes e transformacoes.

## 6. Analise de impacto

A linhagem ajuda a identificar consumidores
que podem ser afetados por alteracoes
ou falhas em bases de origem.

## 7. Laboratorio complementar

Utilizamos o banco SQLite da Aula 04 e a
linhagem documentada na Aula 06.

O programa realiza:

- Busca upstream.
- Busca downstream.
- Leitura dos esquemas SQLite.
- Identificacao de correspondencias de colunas.
- Simulacao de consumidores analiticos.
- Analise de impacto.
- Exportacao CSV e JSON.

Os produtos adicionais de BI, ML e relatorio
regulatorio sao ficticios.

## 8. Ressalva sobre colunas

A coincidencia entre nomes de campos nao
comprova uma transformacao SQL.

O laboratorio marca as correspondencias
como pendentes de validacao.

## 9. Principal aprendizado

Conhecer a origem e o destino dos dados
facilita a identificacao de dependencias,
a manutencao dos pipelines e a investigacao
de possiveis impactos.

A OpenMetadata permite explorar essas
relacoes visualmente no seu catalogo.