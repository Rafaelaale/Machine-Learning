# Aula 11 — Avaliando métricas do modelo ARIMA

## Objetivo

Comparar a previsão baseline com o ARIMA(1,1,1)
utilizando MAE, RMSE e MAPE.

Usar as previsões já geradas na Aula 10.

## MAE — Mean Absolute Error

Erro absoluto médio.

Quanto menor, melhor.

É apresentado na unidade de bicicletas.

## RMSE — Root Mean Squared Error

Raiz quadrada do erro quadrático médio.

Penaliza mais os erros de grande magnitude.

```python
rmse = np.sqrt(
    mean_squared_error(y_real, y_pred)
)
```

## MAPE — Mean Absolute Percentage Error

Erro percentual absoluto médio.

```python
mascara = y_real != 0

mape = np.mean(
    np.abs(
        (
            y_real[mascara]
            - y_pred[mascara]
        ) / y_real[mascara]
    )
) * 100
```

Valores reais iguais a zero são excluídos
do denominador do MAPE.

Se todos os valores reais forem zero,
o MAPE é considerado indefinido.

## Comparação

A baseline repete o último valor do treino.

O ARIMA(1,1,1) já foi treinado na Aula 10.

As métricas são calculadas nas mesmas
60 observações reservadas para teste.

## Resíduos

Resíduo = demanda real - previsão ARIMA.

Resíduo positivo: modelo subestimou.

Resíduo negativo: modelo superestimou.

## Interpretação

Menor MAE é melhor.

Menor RMSE é melhor.

Menor MAPE é melhor.

O melhor modelo por MAPE será identificado
a partir dos resultados reais do projeto.

Não copiar os números do vídeo da Alura
sem executar os cálculos.

## Cuidados

A série pode possuir lacunas de calendário.

A convergência do modelo da Aula 10
deve ser consultada separadamente.

Nenhum ARIMA será treinado novamente
durante esta aula.

## Arquivos

src/aula11_metricas_arima.py
aulas/aula11_metricas_arima.py
tests/test_aula11_metricas_arima.py
notebooks/11_avaliacao_metricas_arima.ipynb

resultados/aula11_previsoes_arima.csv
resultados/aula11_metricas_arima.csv
resultados/aula11_residuos_arima.csv
resultados/aula11_avaliacao_arima.json

graficos/aula11_comparacao_metricas.html
graficos/aula11_residuos_arima.html

## Próxima aula

Introdução ao SARIMA e à sazonalidade.
