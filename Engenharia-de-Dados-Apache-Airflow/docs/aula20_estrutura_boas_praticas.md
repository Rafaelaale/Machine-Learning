# Aula 20 — Estrutura do projeto e boas práticas

## Objetivo

Revisar a arquitetura do projeto Vende+ e manter separadas
a orquestração do Airflow e as regras de negócio.

## Estrutura

- config/: configurações internas do Airflow
- configs/: parâmetros por ambiente (dev e prod)
- dags/: definição e orquestração dos pipelines
- data/: arquivos de entrada, temporários e resultados
- docs/: documentação técnica e histórico das aulas
- helpers/: regras de negócio e callbacks
- logs/: registros de execução
- plugins/: extensões do Airflow
- scripts/: utilitários e geração de dados
- .env: variáveis locais e configurações sensíveis
- docker-compose.yaml: serviços do ambiente Docker

## Pipelines

### pipeline_vendas

Responsável pelo processamento diário das vendas.

Componentes desenvolvidos nas aulas anteriores:

- FileSensor para aguardar o arquivo de vendas
- Extração dos dados
- Transformação dos dados
- Carregamento do resumo
- XCom para metadados
- Agendamento diário às 07h, horário de Salvador

### pipeline_cotacao

Responsável pela consulta da cotação USD-BRL.

Componentes:

- Consulta à AwesomeAPI
- Armazenamento do JSON bruto
- Consolidação do histórico
- Uso de Variables e Connection do Airflow

## Boas práticas revisadas

1. Separar DAGs das regras de negócio.
2. Usar nomes claros e padronizados.
3. Definir tags descritivas.
4. Manter catchup=False quando apropriado.
5. Utilizar start_date fixo.
6. Configurar retries e retry_delay.
7. Registrar logs relevantes.
8. Usar XCom apenas para dados leves e metadados.
9. Implementar callbacks de falha.
10. Testar tasks isoladamente.
11. Evitar lógica pesada durante a importação das DAGs.
12. Utilizar TaskFlow API quando apropriado.

## Ambientes

O módulo configs/ambientes.py apresenta configurações
separadas para desenvolvimento e produção.

Nesta aula, ele é apenas demonstrativo.

As DAGs existentes continuam usando as Variables e
Connections configuradas anteriormente.

Os caminhos de produção são exemplos e precisam ser
adaptados antes de uma implantação real.

## Pendência conhecida

O callback de notificação foi implementado na Aula 19.

O teste de envio pelo Gmail apresentou erro SMTP 535,
indicando autenticação recusada pelo Google.

A entrega de e-mails permanece pendente.

## Observação

A Aula 20 é uma revisão estrutural. Nenhuma DAG precisa
ser reescrita para acompanhar o conteúdo apresentado.