# Aula 04 — Tendência, sazonalidade e ruído

## Objetivo

Compreender os componentes de uma série temporal
antes de começar a modelagem com ARIMA ou SARIMAX.

## Tendência

Representa movimentos mais amplos da demanda,
como crescimento, redução e mudanças de nível.

## Sazonalidade

Representa padrões que se repetem em determinado
intervalo da série.

## Resíduo ou ruído

Representa a parte da série que não foi explicada
pela tendência e pela sazonalidade estimadas.

## Média móvel de 7 observações

```python
serie_diaria["media_movel_7"] = (
    serie_diaria["demanda"]
    .rolling(window=7)
    .mean()
)
```

As primeiras seis posições recebem NaN porque
a janela de sete observações ainda não está completa.

A média móvel usada para suavização não é a mesma
coisa que o termo MA dos modelos ARIMA.

## Decomposição aditiva

Modelo conceitual:

Observado = Tendência + Sazonalidade + Resíduo

```python
from statsmodels.tsa.seasonal import seasonal_decompose

decomposicao = seasonal_decompose(
    serie_para_decompor,
    model="additive",
    period=7
)
```

## Componentes

- observado: demanda original
- tendencia: movimento suavizado
- sazonalidade: padrão periódico estimado
- residuo: parcela restante

Valores ausentes nas extremidades da tendência
e dos resíduos são esperados.

## Atenção à qualidade do calendário

O conjunto Bike Sharing Demand de treino não
contém necessariamente todas as datas do intervalo.

Portanto, aplicar period=7 diretamente sobre
observações diárias com datas ausentes NÃO comprova
sazonalidade semanal de sete dias consecutivos.

Neste laboratório, a decomposição representa
um ciclo de sete observações ordenadas.

Antes de usar essa informação em um modelo real,
é necessário tratar a frequência e as lacunas
do calendário de maneira apropriada.

Não preenchemos dias ausentes com demanda zero.

## Resultados salvos

- resultados/serie_diaria_bike.csv
- resultados/aula04_media_movel.csv
- resultados/aula04_componentes.csv
- resultados/aula04_decomposicao.json
- graficos/aula04_media_movel.html
- graficos/aula04_decomposicao.html

## Próxima aula

Estacionariedade e teste ADF.

O teste ADF não foi realizado nesta aula.
