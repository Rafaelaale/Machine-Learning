# Aula 6.5 - Gerenciamento de Acessos Unity Catalog

## Objetivo

Aprender a controlar acesso de leitura, escrita
e administracao nos catalogos de desenvolvimento,
homologacao e producao.

## Comandos

GRANT: concede privilegios.
REVOKE: revoga privilegios.
SHOW GRANTS: consulta grants.

SELECT: leitura.
MODIFY: modificacao de dados.
CREATE TABLE: criacao de tabelas.
MANAGE: gestao de privilegios e objetos.

## Conceitos importantes

Para ler uma tabela, normalmente precisamos de:
USE CATALOG + USE SCHEMA + SELECT.

Privilegios podem ser herdados de catalogos
e schemas.

Revogar um privilegio direto de uma tabela
nao remove necessariamente acesso herdado.

ALL PRIVILEGES nao inclui MANAGE.

A autorizacao para DROP depende de propriedade
e permissoes administrativas apropriadas.

## Proposta de seguranca

DEV:
Ambiente de desenvolvimento com permissoes
de alteracao para a equipe autorizada.

STAGE:
Ambiente controlado para testes e homologacao.

PROD:
Equipe de analise com privilegios de leitura.
Identidade dedicada de pipeline para tarefas
autorizadas de escrita e implantacao.
Permissoes administrativas restritas.

## Arquivos da aula

PERMISSOES_UNITY_CATALOG.sql:
Exemplos SQL comentados e nao executados.

simular_permissoes.py:
Simulacao didatica local, sem Databricks.

resultados/AUDITORIA_UNITY_CATALOG.json:
Resultados dos testes locais.

## Limitacoes

A simulacao nao e um motor real de autorizacao
do Unity Catalog.

Nao cobre ownership, grupos aninhados,
todas as regras de heranca ou administracao.

Os comandos SQL nao foram executados remotamente.

Nao houve mudanca em usuarios, tabelas,
catalogos ou privilegios reais.

## Documentacao oficial

https://docs.databricks.com/aws/en/sql/language-manual/security-revoke

https://docs.databricks.com/aws/en/data-governance/unity-catalog/access-control/permissions-concepts