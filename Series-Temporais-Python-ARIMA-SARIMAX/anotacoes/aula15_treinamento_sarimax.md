# Aula 15 — Incluindo variáveis exógenas no SARIMAX

## Objetivo

Treinar SARIMAX(1,1,1)x(1,0,1,7) com as 12
variáveis externas da Aula 14.

## Dados

- X_treino: 396 linhas, 12 colunas
- X_teste: 60 linhas, 12 colunas
- y_treino: demanda observada no treino
- y_teste: demanda observada no teste

## Treinamento

A classe SARIMAX recebe y_treino e exog=X_treino.

O modelo usa:

- order=(1,1,1)
- seasonal_order=(1,0,1,7)
- enforce_stationarity=False
- enforce_invertibility=False

## Previsões

O forecast recebe steps=60 e exog=X_teste.

## Métricas

São calculadas MAE, RMSE e MAPE.

Os resultados são comparados com:

- Baseline
- ARIMA
- SARIMA
- SARIMAX

## Limitações

O clima usado no teste é histórico e conhecido.

Em previsões futuras, o clima deverá ser
fornecido por previsões meteorológicas ou cenários.

Existem 263 dias ausentes na base.

O ciclo de sete observações não equivale
necessariamente a sete dias de calendário.

A convergência numérica e o MAPE são
registrados separadamente.

## Próxima aula

Organização dos resultados para aplicação.
