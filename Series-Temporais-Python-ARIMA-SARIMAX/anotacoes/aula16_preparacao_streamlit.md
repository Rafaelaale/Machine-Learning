# Aula 16 — Preparando dados para Streamlit

## Objetivo

Separar os resultados da modelagem dos dados
que serão apresentados na aplicação.

Nenhum modelo é treinado novamente.

## Quatro fontes para o aplicativo

outputs/tabelas/serie_historica.csv

Contém data_hora e demanda diária.

outputs/tabelas/metricas.csv

Contém modelo, MAE, RMSE e MAPE
para Baseline, ARIMA, SARIMA e SARIMAX.

outputs/tabelas/previsoes.csv

Contém data_hora, demanda real
e previsão de cada um dos quatro modelos.

outputs/tabelas/resumo_projeto.csv

Contém:

- modelo_final
- MAE
- RMSE
- MAPE
- inicio_historico
- fim_historico
- dias_historico
- dias_teste

## Melhor modelo

Selecionamos a linha com menor MAPE.

```python
melhor_modelo = metricas.sort_values("MAPE").iloc[0]
nome_melhor_modelo = melhor_modelo["modelo"]
```

No projeto, a coluna se chama modelo,
com letra minúscula.

O código não assume previamente
que o SARIMAX é o vencedor.

## Visualizações

Gráfico 1: série histórica.

Gráfico 2: demanda real versus
Baseline, ARIMA, SARIMA e SARIMAX.

## Integridade

O período de teste deve corresponder
às últimas 60 observações da série.

As métricas salvas são verificadas
contra as previsões existentes.

## Limitações

456 observações diárias não equivalem
a 456 dias corridos consecutivos.

A série possui 263 dias ausentes.

As previsões SARIMAX avaliadas utilizaram
variáveis climáticas históricas conhecidas.

Previsão operacional futura exigirá
informações exógenas futuras.

## Próxima aula

Criar o app.py e montar a aplicação Streamlit.
