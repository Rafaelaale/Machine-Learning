# Aula - Criando Alertas de Drift

Fonte:
https://github.com/alura-cursos/6123-alura-ml-databricks

Referencia:
https://docs.databricks.com/aws/en/sql/user/alerts/

## Objetivo

Reproduzir localmente o fluxo de alertas da aula.

1. Gerar dados de treinamento.
2. Gerar dados produtivos.
3. Calcular drift de duas features.
4. Calcular variacao relativa do target.
5. Salvar os resultados em SQLite.
6. Consultar os alertas por SQL.
7. Registrar uma notificacao local.
8. Evitar notificacoes duplicadas no mesmo periodo.

## Configuracao

Inicio: 20260501
Fim exclusivo: 20260601

Treinamento: 10000 registros.
Producao: 3100 registros.
Features: renda_mensal_k, tempo_medio_clique_segundos.
Target: comprou_eletronico.

KS:
- Limiar do p-value: 0.05.
- P-value calculado por aproximacao assintotica.
- Nao requer SciPy.

Target:
- Variacao relativa de 15%.
- A variacao da taxa do target nao prova concept drift.

## Alertas

A consulta conta apenas registros em que
drift_detectado = 1.

Se total_drift > 0:
  Status = TRIGGERED.

Caso contrario:
  Status = OK.

As notificacoes sao registradas localmente.
Nao ha envio automatico de email.

## Arquivos

monitoramento_e_alertas_local.py
CONSULTA_ALERTA_LOCAL.sql
CONSULTA_ALERTA_DATABRICKS.sql
executar_aula_alertas.ps1
dados/
logs/

## Limitacoes

Esta implementacao e local, nao e um Job remoto
do Databricks.

O agendamento automatico e o envio de email
nao foram configurados.

Os notebooks anteriores da Alura permanecem
inalterados.