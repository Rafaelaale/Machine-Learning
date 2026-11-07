# Aula 14 — Incorporando variáveis exógenas no SARIMAX

## Objetivo

Preparar temperatura, sensação térmica, umidade,
vento, feriado, dia útil e dia da semana
para o futuro treinamento SARIMAX.

Nesta aula ainda não treinamos o SARIMAX.

## SARIMA versus SARIMAX

SARIMA utiliza a estrutura temporal e sazonal.

SARIMAX acrescenta variáveis exógenas,
também chamadas de variáveis externas.

## Dados de origem

A base original possui registros horários.

As variáveis originais são traduzidas
para os nomes utilizados no curso.

## Agregações diárias

Demanda: soma.

Temperatura: média.

Sensação térmica: média.

Umidade: média.

Velocidade do vento: média.

Feriado: máximo.

Dia útil: máximo.

Dia da semana: primeiro valor.

Mês: primeiro valor.

Antes da agregação, o código verifica
se as informações de calendário permanecem
constantes dentro de cada dia.

## Codificação categórica

O dia da semana é codificado com:

```python
pd.get_dummies(
    categorias,
    prefix="dia_semana",
    drop_first=True,
    dtype=float
)
```

Seis colunas são geradas:

dia_semana_1 até dia_semana_6.

A categoria 0 é a referência.

## Variáveis externas

- temperatura_media
- sensacao_termica_media
- umidade_media
- velocidade_vento_media
- feriado
- dia_util
- dia_semana_1
- dia_semana_2
- dia_semana_3
- dia_semana_4
- dia_semana_5
- dia_semana_6

O mês permanece disponível na base,
mas não integra este primeiro X.

## Divisão temporal

396 observações de treino.

60 observações de teste.

Mesma divisão do ARIMA e SARIMA.

## Separação de X e y

```python
y_treino = treino["demanda"].astype(float)
y_teste = teste["demanda"].astype(float)

X_treino = treino[variaveis_externas].astype(float)
X_teste = teste[variaveis_externas].astype(float)
```

## Atenção aos dados futuros

No teste histórico, já sabemos o clima observado.

Em previsão real, a temperatura, umidade e vento
do futuro ainda não são conhecidos.

Serão necessárias previsões climáticas
ou cenários externos disponíveis antecipadamente.

Também existem datas sem registros de demanda.

Não inventamos valores para preencher lacunas.

## Próxima aula

Treinar SARIMAX e avaliar suas previsões.
