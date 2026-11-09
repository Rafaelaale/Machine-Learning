# Engenharia de Dados com Apache Airflow — Vende+

Projeto prático de engenharia de dados desenvolvido em Python, Apache Airflow 3.4, Docker e VS Code.

## Tecnologias
Python, Apache Airflow, TaskFlow API, Docker Compose, PostgreSQL, Redis, HTTP, CSV, JSON e PowerShell.

## Pipeline de vendas
DAG `pipeline_vendas`: FileSensor, extração de CSV, transformação, consolidação e geração de resumo.

Validação local registrada: 80 pedidos, totalizando R$ 35.107,01.

Agendamento diário às 07h (Salvador), `catchup=False`, retries e logs.

## Pipeline de cotação
DAG `pipeline_cotacao`: consulta USD-BRL na AwesomeAPI, armazenamento de JSON e consolidação histórica em CSV.

## Recursos estudados e implementados
- DAGs, tarefas e dependências
- TaskFlow API
- Helpers e organização modular
- Logs e observabilidade
- XCom
- Airflow Variables e Connections
- FileSensor
- Agendamento cron
- Retries e callbacks de falha
- Estrutura de projeto e boas práticas
- Separação lógica DEV/PROD
- Validação de sintaxe e execuções locais

## Ambientes
O laboratório utiliza um único Airflow com configurações lógicas DEV e PROD. Não representa dois servidores independentes.

## Validação
Pipelines de vendas e cotação executados localmente. Configurações DEV/PROD verificadas. O envio de alertas por Gmail permanece pendente devido à autenticação SMTP.

## Organização
- `dags/`: orquestração dos pipelines
- `helpers/`: regras de processamento e callbacks
- `configs/`: configurações de ambientes
- `docs/`: documentação das aulas

## Segurança
Credenciais, arquivos `.env`, logs e bancos locais não devem ser publicados.

## Autor
Rafael Alexandre Oliveira Araujo

https://github.com/Rafaelaale