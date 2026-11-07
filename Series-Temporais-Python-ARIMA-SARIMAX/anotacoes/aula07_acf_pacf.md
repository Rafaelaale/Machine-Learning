# Aula 07 — Entendendo ACF e PACF

## Objetivo

Investigar a memória temporal da demanda
de bicicletas após a primeira diferenciação.

## Lag

Lag é um atraso na sequência temporal.

Lag 1: observação anterior.
Lag 2: duas observações atrás.
Lag 7: sete observações atrás.
Lag 30: trinta observações atrás.

Importante: em uma série com datas ausentes,
lag 7 não necessariamente corresponde
a sete dias de calendário.

## ACF — Autocorrelation Function

Mede a autocorrelação total da série
com suas versões defasadas.

```python id="se4r2h"
valores_acf = acf(
    serie_diferenciada["demanda_diff"],
    nlags=30
)
```

## PACF — Partial Autocorrelation Function

Estima a correlação parcial em cada lag,
controlando as defasagens intermediárias.

```python id="c1gqqa"
valores_pacf = pacf(
    serie_diferenciada["demanda_diff"],
    nlags=30,
    method="ywm"
)
```

O método ywm corresponde a uma variante
do estimador Yule-Walker.

## Lag zero

ACF(0) = 1.
PACF(0) = 1.

Não utilizar lag zero para escolher parâmetros.

## Faixa de referência

Nesta aula usamos uma referência aproximada:

+/- 1,96 / sqrt(n)

A ultrapassagem dessa faixa indica
um lag candidato para investigação.

Não é confirmação automática de
significância nem do melhor modelo.

## Relação com ARIMA

PACF pode sugerir valores candidatos de p.

ACF pode sugerir valores candidatos de q.

A diferenciação feita anteriormente
corresponde a d = 1.

ARIMA(p, d, q) ainda não foi treinado.

## Resultados

resultados/aula07_acf.csv
resultados/aula07_pacf.csv
resultados/aula07_comparacao_lags.csv
resultados/aula07_acf_pacf.json

graficos/aula07_acf.html
graficos/aula07_pacf.html
graficos/aula07_acf_pacf_comparacao.html

## Próxima aula

Modelos AR, MA e ARMA.
