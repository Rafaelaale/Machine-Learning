# Aula 21 — Separação de ambientes DEV e PROD

## Objetivo

Compreender a diferença entre ambientes lógicos no mesmo
Airflow e ambientes fisicamente segregados.

## Ambiente lógico

Um único Airflow pode utilizar configurações diferentes
para desenvolvimento e produção.

Exemplo:

DEV:
- Conexão: awesomeapi_http_dev
- Entrada: /opt/airflow/data/dev/input
- Saída: /opt/airflow/data/dev/output

PROD (simulado):
- Conexão: awesomeapi_http
- Entrada: /opt/airflow/data/input
- Saída: /opt/airflow/data/output

## Seleção dinâmica

O módulo configs/separacao_ambientes.py permite selecionar
as configurações usando a variável ENV.

Exemplos:

get_ambiente("dev")
get_ambiente("prod")

## Ambientes fisicamente separados

Em uma arquitetura de produção real, DEV e PROD
devem possuir infraestrutura, configurações,
credenciais e recursos próprios.

Uma esteira CI/CD pode validar mudanças em DEV
antes de promovê-las para PROD.

## Situação deste projeto

O projeto possui somente um ambiente Docker Airflow.

A separação criada nesta aula é lógica e demonstrativa.

As DAGs pipeline_vendas e pipeline_cotacao
continuam com suas configurações anteriores.

Nenhuma conexão ou variável do Airflow foi modificada.

## Boas práticas

- Evitar misturar dados de desenvolvimento e produção.
- Manter nomes consistentes entre ambientes segregados.
- Evitar credenciais no código-fonte.
- Testar antes de promover alterações.
- Manter pipelines independentes e observáveis.