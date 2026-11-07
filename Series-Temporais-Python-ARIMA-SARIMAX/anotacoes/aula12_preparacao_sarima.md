# Aula 12 — Entendendo sazonalidade e preparando SARIMA

## Objetivo

Preparar a série diária e reutilizar a mesma
separação temporal do ARIMA.

Nenhum modelo SARIMA será treinado nesta aula.

## Relembrando ARIMA

ARIMA combina:

- Autorregressão
- Diferenciação
- Médias móveis dos erros

Na Aula 11, a baseline apresentou menor erro
que o ARIMA(1,1,1).

## SARIMA

SARIMA acrescenta componentes sazonais
à estrutura ARIMA.

A demanda de bicicletas pode apresentar
diferenças entre dias úteis e finais de semana.

Um ciclo semanal de sete dias é uma
hipótese que será investigada.

## SARIMAX

SARIMAX também permite trabalhar
com variáveis externas, como:

- Temperatura
- Umidade
- Feriados
- Dias úteis

Essas variáveis ainda não serão utilizadas.

## Importação

```python
from statsmodels.tsa.statespace.sarimax import SARIMAX
```

## Série diária

A base contém:

- data_hora
- demanda

Referência do curso: 456 observações.

## Treino e teste

```python
tamanho_teste = 60

treino = serie_diaria.iloc[:-tamanho_teste].copy()
teste = serie_diaria.iloc[-tamanho_teste:].copy()
```

Treino esperado: 396 observações.

Teste esperado: 60 observações.

A divisão deve ser idêntica à da Aula 09.

## Cuidado com a sazonalidade

O arquivo possui dias ausentes.

Sete observações anteriores não são
necessariamente sete dias anteriores.

Não completar as lacunas com valores
inventados.

Antes do ajuste sazonal, será preciso
definir uma estratégia apropriada para
o calendário e para as observações ausentes.

## Arquivos da aula

src/aula12_preparacao_sarima.py

aulas/aula12_preparacao_sarima.py

tests/test_aula12_preparacao_sarima.py

notebooks/12_preparando_sarima.ipynb

resultados/aula12_serie_diaria.csv

resultados/aula12_treino_sarima.csv

resultados/aula12_teste_sarima.csv

resultados/aula12_dias_ausentes.csv

resultados/aula12_preparacao_sarima.json

graficos/aula12_serie_diaria.html

graficos/aula12_treino_teste_sarima.html

## Próxima aula

Definição dos parâmetros sazonais e
treinamento do SARIMA.
