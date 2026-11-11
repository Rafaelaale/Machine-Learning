# Aula - Re-treino Automatizado por Drift

## Fonte
https://github.com/alura-cursos/6123-alura-ml-databricks

## Objetivo
Reproduzir localmente o re-treino condicionado ao drift.

## Fluxo
1. Carga produtiva previamente realizada.
2. Monitoramento previamente realizado.
3. Consulta dos logs de drift no SQLite.
4. Condicao: total_drift > 0.
5. Re-treino com dados produtivos.
6. Avaliacao com ROC-AUC.
7. Registro de nova versao local.
8. Atualizacao do alias Champion local.

## Parametros
data_inicio = 20260501
data_fim = 20260601 (exclusiva)

## Dados existentes
aulas/aula_05_04_alertas_locais/dados/
aulas/aula_05_04_alertas_locais/logs/

## Modelos
LightGBM sera usado quando instalado.

Caso contrario, sera utilizada regressao logistica
implementada em Python puro.

O algoritmo utilizado fica registrado nas metricas.

## Validacao
- ROC-AUC calculada com scores ou probabilidades.
- Divisao estratificada e reproduzivel.
- AUC minima didatica: 0.55.
- Champion preservado se avaliacao falhar.
- Mesmo periodo e mesmo CSV nao geram nova versao.

## Limitacoes
Nao executa Spark ou Jobs remotos.
Nao utiliza o Model Registry do Databricks.
Nao configura MLflow nem publica endpoint.
Nao agenda execucoes automaticamente.

Esta e uma equivalencia didatica local,
nao a implementacao integral em Databricks.

## Arquivos anteriores
Os arquivos das aulas 5.2, Jobs e Alertas
nao serao alterados.