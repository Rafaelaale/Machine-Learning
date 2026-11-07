# Aula 09 — Separando treino e teste para ARIMA

## Objetivo

Preparar a série de demanda diária para a modelagem
e realizar divisão cronológica de treino e teste.

Nesta aula ainda não treinamos ARIMA.

## ARIMA

ARIMA significa Autoregressive Integrated Moving Average.

Parâmetros:

- p: componente autorregressivo
- d: ordem da diferenciação não sazonal
- q: componente de médias móveis dos erros

## Preparação da série

Selecionamos as colunas:

```python id="6bit0b"
serie_modelagem = serie_diaria[
    ["data_hora", "demanda"]
].copy()
```

A coluna data_hora deve estar em formato datetime.

A série deve estar ordenada cronologicamente.

## Treino e teste

Reservamos as últimas 60 observações:

```python id="yvc9dx"
tamanho_teste = 60

treino = serie_modelagem.iloc[
    :-tamanho_teste
].copy()

teste = serie_modelagem.iloc[
    -tamanho_teste:
].copy()
```

Treino: passado da série.

Teste: trecho final, usado para avaliação posterior.

Não embaralhar as observações.

## Validação

Verificar:

- Quantidade de observações
- Período de treino
- Período de teste
- Ausência de sobreposição temporal
- Preservação do total de registros

## Atenção ao calendário

Nossa base possui datas não observadas.

Portanto, as últimas 60 observações podem
representar mais de 60 dias de calendário.

A aula reproduz o recorte com iloc
sem preencher datas ausentes artificialmente.

Essa limitação deverá ser considerada
quando formos ajustar e avaliar o ARIMA.

## Arquivos gerados

src/aula09_separacao_temporal.py
aulas/aula09_separacao_temporal.py
tests/test_aula09_separacao_temporal.py
notebooks/09_separando_treino_teste_arima.ipynb

resultados/aula09_serie_modelagem.csv
resultados/aula09_treino.csv
resultados/aula09_teste.csv
resultados/aula09_separacao_temporal.json

graficos/aula09_serie_modelagem.html
graficos/aula09_treino_teste.html

## Próxima aula

Criando um baseline simples para previsão.
