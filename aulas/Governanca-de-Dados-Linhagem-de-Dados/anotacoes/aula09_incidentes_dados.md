# Aula 09 - Incidentes de dados

## Objetivo

Compreender como problemas em dados podem
interromper processos de negocio e como a
linhagem auxilia na investigacao.

## 1. Incidente de negocio

Ocorre quando um processo que gera valor
para a organizacao e interrompido.

## 2. Incidente de dados

E uma falha relacionada aos dados capaz
de comprometer um processo ou relatorio.

## 3. Exemplo da Alura

Uma area de prevencao a lavagem de dinheiro
utiliza a base de clientes ativos da newsletter
para produzir um relatorio mensal.

O processo encontra problemas nos dados.

A investigacao identifica uma falha na
origem da base, a Source of Records (SOR).

## 4. Importancia da linhagem

A linhagem permite identificar:

- A base de origem.
- As transformacoes realizadas.
- As bases intermediarias.
- Os processos dependentes.
- Os impactos de uma falha.

## 5. Recuperacao de incidentes

Acoes que podem ser necessarias:

1. Registrar o incidente.
2. Localizar a origem do problema.
3. Acionar as pessoas responsaveis.
4. Corrigir e reprocessar os dados.
5. Validar os resultados recuperados.
6. Registrar evidencias da recuperacao.

## 6. Accountability by Design

A documentacao e a linhagem ajudam
a compreender o funcionamento do processo
e a produzir evidencias para auditoria.

## 7. Laboratorio complementar

Reutilizamos o banco da Aula 04 e a
documentacao de linhagem da Aula 06.

Foi simulada a omissao de um identificador
ficticio na Source of Records.

O impacto foi rastreado ate um relatorio
regulatorio inteiramente ficticio.

Nenhum dado original foi alterado.

Nenhum reprocessamento real foi executado.

## 8. Principal aprendizado

A documentacao da linhagem facilita
a investigacao de incidentes e a avaliacao
de impactos sobre processos dependentes.

A linhagem, isoladamente, nao prova
a causa de incidentes reais.