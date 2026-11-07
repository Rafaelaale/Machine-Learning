# Aula 06 — Diferenciação da série temporal

## Objetivo

Aplicar a primeira diferenciação à demanda diária
e comparar o teste ADF antes e depois da transformação.

## Diferenciação

A primeira diferença é:

demanda_diff[t] = demanda[t] - demanda[t-1]

Exemplo:

985 -> 801: -184 bicicletas
801 -> 1349: +548 bicicletas

## Código

```python
serie_diaria["demanda_diff"] = (
    serie_diaria["demanda"].diff()
)

serie_diferenciada = (
    serie_diaria.dropna(subset=["demanda_diff"])
).copy()
```

A primeira diferença recebe NaN porque não existe
uma observação anterior.

## Interpretação

Valor positivo: demanda aumentou.
Valor negativo: demanda diminuiu.
Valor zero: demanda permaneceu igual.

Diferenciação não é uma previsão.

## Teste ADF

Reutilizamos teste_adf() da Aula 05.

H0: presença de raiz unitária.

Com alfa = 0,05:

p-valor <= 0,05: rejeitar H0.
p-valor > 0,05: não rejeitar H0.

O p-valor deve ser calculado, não presumido.

Um p-valor impresso como 0.0000 pode ser
positivo e extremamente pequeno.

## Parâmetro ARIMA

Primeira diferença não sazonal:
d = 1.

Diferenciação sazonal é representada por D.

Ainda não treinamos ARIMA, SARIMA ou SARIMAX.

## Cuidado com datas ausentes

O método diff() compara observações consecutivas.

Se houver dias ausentes no calendário, uma diferença
pode abranger mais de um dia.

O código registra o intervalo entre as observações.

## Arquivos da aula

src/aula06_diferenciacao.py
aulas/aula06_diferenciacao.py
tests/test_aula06_diferenciacao.py
notebooks/06_diferenciacao_estacionariedade.ipynb

resultados/aula06_serie_diferenciada.csv
resultados/aula06_adf_diferenciado.csv
resultados/aula06_comparacao_adf.csv
resultados/aula06_diferenciacao.json

graficos/aula06_original_vs_diferenciada.html

## Próxima aula

ACF e PACF: autocorrelação e autocorrelação parcial.
