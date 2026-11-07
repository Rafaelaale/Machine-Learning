# Aula 10 — Criando baseline e treinando ARIMA

## Objetivo

Criar uma previsão simples de referência,
treinar o primeiro ARIMA(1,1,1) e gerar
previsões para o conjunto de teste.

## Baseline

A previsão repete o último valor observado
no treino durante todo o horizonte de teste.

```python
ultimo_valor_treino = treino["demanda"].iloc[-1]

teste["previsao_baseline"] = ultimo_valor_treino
```

## ARIMA

Modelo escolhido para a aula:

ARIMA(1,1,1)

p=1: parte autorregressiva de ordem 1.

d=1: uma diferenciação não sazonal.

q=1: componente de médias móveis dos erros.

Essa escolha é inicial, não necessariamente ótima.

## Treinamento

```python
from statsmodels.tsa.arima.model import ARIMA

ordem_arima = (1, 1, 1)

modelo_arima = ARIMA(
    treino["demanda"],
    order=ordem_arima,
)

resultado_arima = modelo_arima.fit()

print(resultado_arima.summary())
```

## Previsões

```python
previsao_arima = resultado_arima.forecast(
    steps=len(teste)
)

teste["previsao_arima"] = previsao_arima.values
```

## Comparação visual

Três séries:

- Demanda real
- Previsão baseline
- Previsão ARIMA

Nesta aula não decidimos qual modelo é melhor.

A comparação quantitativa será feita na próxima aula.

## Cuidados metodológicos

O modelo utiliza somente os dados de treino.

O conjunto de teste permanece reservado
para a avaliação.

A base possui lacunas de calendário.

O ARIMA é treinado sobre observações ordenadas,
sem assumir frequência diária regular.

O baseline e o ARIMA usam o mesmo horizonte
de 60 observações futuras.

## Arquivos

src/aula10_baseline_arima.py
aulas/aula10_baseline_arima.py
tests/test_aula10_baseline_arima.py
notebooks/10_baseline_primeiro_arima.ipynb

resultados/aula10_previsoes_baseline_arima.csv
resultados/aula10_baseline_arima.json
resultados/aula10_resumo_estatistico_arima.txt

graficos/aula10_comparacao_previsoes.html
graficos/aula10_historico_e_previsoes.html

## Próxima aula

Calcular métricas de erro e comparar
baseline versus ARIMA.
