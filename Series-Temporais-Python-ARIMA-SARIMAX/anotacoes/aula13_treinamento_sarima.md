# Aula 13 — Treinando o modelo SARIMA sazonal

## Objetivo

Treinar SARIMA(1,1,1)x(1,0,1,7),
prever as 60 observações de teste,
calcular métricas e comparar três modelos.

## Parâmetros não sazonais

- p = 1: autorregressão
- d = 1: diferenciação
- q = 1: médias móveis dos erros

## Parâmetros sazonais

- P = 1: autorregressão sazonal
- D = 0: sem diferenciação sazonal extra
- Q = 1: médias móveis sazonais
- s = 7: ciclo de sete observações

## Treinamento

```python id="ndoqcf"
from statsmodels.tsa.statespace.sarimax import SARIMAX

ordem_sarima = (1, 1, 1)
ordem_sazonal = (1, 0, 1, 7)

modelo_sarima = SARIMAX(
    treino["demanda"],
    order=ordem_sarima,
    seasonal_order=ordem_sazonal,
    enforce_stationarity=False,
    enforce_invertibility=False,
)

resultado_sarima = modelo_sarima.fit(disp=False)
```

## Previsão

```python id="rtqovm"
previsao_sarima = resultado_sarima.forecast(
    steps=len(teste)
)

teste["previsao_sarima"] = previsao_sarima.values
```

## Avaliação

As métricas são:

- MAE
- RMSE
- MAPE

Comparar:

- Baseline
- ARIMA(1,1,1)
- SARIMA(1,1,1)x(1,0,1,7)

Menor MAPE representa menor erro percentual
neste conjunto de teste.

## Resíduos

Resíduo SARIMA = demanda real - previsão SARIMA.

Valores positivos representam subestimativa.
Valores negativos representam superestimativa.

## Atenção ao calendário

A série tem datas ausentes.

Por esse motivo, o experimento com s=7
não garante interpretação semanal real.

Este exercício mantém a sequência de observações
para reproduzir o fluxo didático da Alura.

Um estudo posterior deverá considerar
a regularização do índice temporal sem
fabricar demandas para datas não observadas.

## Arquivos

src/aula13_treinamento_sarima.py
aulas/aula13_treinamento_sarima.py
tests/test_aula13_treinamento_sarima.py
notebooks/13_treinamento_sarima.ipynb

resultados/aula13_previsoes_sarima.csv
resultados/aula13_metricas_sarima.csv
resultados/aula13_comparacao_modelos.csv
resultados/aula13_residuos_sarima.csv
resultados/aula13_relatorio_sarima.json
resultados/aula13_resumo_sarima.txt

modelos/aula13_sarima_111_1017.pkl

graficos/aula13_real_vs_sarima.html
graficos/aula13_comparacao_mape.html
graficos/aula13_residuos_sarima.html

## Próxima aula

Inclusão de variáveis externas com SARIMAX:
temperatura, umidade e calendário.
