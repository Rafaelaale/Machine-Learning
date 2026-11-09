# Aula 13 — Construindo a DAG de cotacao USD-BRL

## DAG
pipeline_cotacao

## Arquivo
dags/pipeline_cotacao.py

## Helper
helpers/cotacao.py

Importacao padronizada:
import helpers.cotacao as cotacao_helper

## Tarefas

1. buscar_e_salvar_cotacao
2. consolidar

Dependencia:
buscar_e_salvar_cotacao >> consolidar

## Configuracoes

- schedule=None
- catchup=False
- retries=3
- retry_delay=5 minutos
- URL fixa da AwesomeAPI
- Sem FileSensor
- Sem Airflow Variables
- Sem XCom explicito
- Sem email
- Sem get_config()

## Arquivos de saida

JSON bruto:
data/cotacao/raw/cotacao_YYYY-MM-DD.json

CSV consolidado:
data/cotacao/consolidated/historico_7dias.csv

## Objetivo da aula

Criar a DAG, validar a sintaxe, importar o helper
e confirmar que a DAG aparece no Airflow.

A execucao real sera realizada na proxima aula.
