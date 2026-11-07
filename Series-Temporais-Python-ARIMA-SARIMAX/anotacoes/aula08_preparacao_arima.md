# Aula 08 — Conectando ACF e PACF ao ARIMA

## Objetivo

Organizar os conceitos AR, MA, ARMA e ARIMA
e registrar o papel dos parâmetros p, d e q.

## AR — Autoregressive

O componente autorregressivo utiliza
valores passados da própria série.

Parâmetro: p.

Referência inicial: PACF.

## MA — Moving Average

O componente MA utiliza erros passados do modelo.

Parâmetro: q.

Referência inicial: ACF.

Não confundir o MA do ARIMA com a
média móvel aplicada para suavizar gráficos.

## ARMA

Combina os componentes AR e MA.

## ARIMA

Autoregressive Integrated Moving Average.

Combina:

- AR: valores passados.
- I: diferenciação.
- MA: erros passados.

## Parâmetros p, d, q

p: memória dos valores passados.

d: quantidade de diferenciações não sazonais.

q: memória dos erros passados.

## Código da aula

```python
parametros_iniciais = pd.DataFrame({
    "parametro": ["p", "d", "q"],
    "ideia": [
        "Memória dos valores passados",
        "Número de diferenciações",
        "Memória dos erros passados",
    ],
    "Ponto de partida": [
        "Avaliar pela PACF",
        "1",
        "Avaliar pela ACF",
    ],
})
```

## Evidências anteriores

Aula 05: teste ADF da série original.

Aula 06: diferenciação de primeira ordem
e repetição do teste ADF.

Aula 07: ACF e PACF com 30 lags.

O parâmetro d=1 é um ponto de partida,
não uma escolha definitiva de modelo.

## Importante

ACF e PACF sugerem parâmetros candidatos.

A escolha do modelo dependerá de ajuste,
validação temporal e métricas.

A base também possui lacunas no calendário;
esse aspecto deve ser considerado ao modelar.

## Arquivos salvos

src/aula08_preparacao_arima.py

aulas/aula08_preparacao_arima.py

tests/test_aula08_preparacao_arima.py

notebooks/08_conectando_acf_pacf_arima.ipynb

resultados/aula08_parametros_iniciais.csv

resultados/aula08_preparacao_arima.json

## Próxima aula

Primeiro ARIMA na prática.

Separação temporal de treino e teste,
ajuste de parâmetros e geração de previsões.
