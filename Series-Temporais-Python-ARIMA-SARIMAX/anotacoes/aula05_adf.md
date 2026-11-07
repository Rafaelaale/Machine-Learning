# Aula 05 — Teste ADF de estacionariedade

## Objetivo

Investigar se a demanda diária apresenta
evidência contra a presença de raiz unitária.

## Hipóteses

H0: a série possui raiz unitária.

H1: a série não possui raiz unitária,
conforme as condições da especificação do ADF.

## Nível de significância

Alfa = 0,05.

Se p-valor <= 0,05:
rejeitar H0.

Se p-valor > 0,05:
não rejeitar H0.

Não rejeitar H0 não significa provar H0.

## Função principal

```python
resultado = adfuller(serie.dropna())
```

## Resultados

- Estatística ADF
- p-valor
- lags utilizados
- número de observações
- valores críticos de 1%, 5% e 10%

## Valores críticos

A estatística ADF também pode ser comparada
aos valores críticos conforme o nível de significância.

## Resultado apresentado na Alura

O vídeo informa p-valor de aproximadamente 0,2855.

O projeto calcula seu próprio resultado
com os dados disponíveis e autolag=AIC.

## Limitação da base

A sequência contém dias não observados.

O teste é aplicado à sequência de dias
com registros, sem preencher lacunas.

Isso deve ser considerado na interpretação
e no planejamento da modelagem temporal.

## Arquivos

src/aula05_adf.py
aulas/aula05_adf.py
tests/test_aula05_adf.py
notebooks/05_teste_adf.ipynb

resultados/resultados_adf_original.csv
resultados/aula05_adf.json

O arquivo resultados/componentes_serie_bike.csv
também é salvo quando os componentes da Aula 04
estão disponíveis.

## Próxima aula

Diferenciação da série e repetição do teste ADF.
