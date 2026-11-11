# Aula - Criando Jobs Produtivos e Monitoramento

## Fonte oficial
https://github.com/alura-cursos/6123-alura-ml-databricks

## Objetivo

Criar um Job com duas tarefas sequenciais:

1. carga_prod
2. monitoramento_drift

A segunda tarefa depende do sucesso da primeira.

## Notebooks existentes

aulas/aula_05_02_drift_aprimorado/
- aula_5_2_gerando_dados_aprimorado.ipynb
- aula_5_2_job_dados_prod_aprimorado.ipynb
- aula_5_2_job_monitoramento_drift_aprimorado.ipynb

## Parametros

data_inicio = 20260501
data_fim = 20260601
features = renda_mensal_k,tempo_medio_clique_segundos
target = comprou_eletronico
gravar = true
catalogo = workspace
esquema = default

## Cuidados tecnicos

1. A data final e exclusiva.
2. Maio completo tem 31 dias e 3100 registros esperados.
3. A tabela de treinamento aprimorada precisa existir antes do Job.
4. Os notebooks precisam estar no workspace Databricks.
5. O caminho remoto precisa ser confirmado antes de publicar.
6. Os parametros do Job sao repassados aos notebooks.
7. O Job deve executar em computacao serverless na Free Edition.
8. A validacao local nao equivale a execucao no Databricks.
9. O parametro gravar=true permite gravacoes nas tabelas aprimoradas.

## Situacao

- Definicao JSON preparada localmente.
- Configuracao YAML preparada localmente.
- SQL de conferencia preparado.
- Criacao remota do Job ainda nao confirmada.
- Execucao remota ainda nao confirmada.

## Proxima dependencia

Depois de validar este Job, continuar com os demais
passos da Aula 5 e, posteriormente, com o pipeline da Aula 6.