# Aula 03 — Ambiente e dataset

Curso: MLflow — gestão e rastreabilidade do ciclo
de vida de modelos.

## Objetivo

Gerar a base sintética de risco de crédito,
explorar a variável-alvo, separar treino e teste
e preparar o baseline de regressão logística.

## Base de dados

6000 registros sintéticos.

Variável-alvo:
inadimplente

0 = adimplente
1 = inadimplente

### Variáveis numéricas

- idade
- renda_mensal
- tempo_emprego_anos
- score_interno
- valor_solicitado
- num_parcelas

### Variáveis categóricas

- tipo_renda
- possui_restricao

## Reprodutibilidade

Utilizamos RANDOM_STATE = 42.

A base é gerada por um gerador NumPy
com semente definida.

Os dados são inteiramente sintéticos
e não devem representar decisões reais de crédito.

## Divisão dos dados

test_size = 0.25
stratify = y
random_state = 42

Treino: 4500 registros.
Teste: 1500 registros.

A classe minoritária mantém proporções
aproximadamente iguais em ambos os conjuntos.

## Pré-processamento

Numéricas:
SimpleImputer(strategy="median")
StandardScaler()

Categóricas:
SimpleImputer(strategy="most_frequent")
OneHotEncoder(handle_unknown="ignore")

ColumnTransformer conecta cada transformação
às respectivas colunas.

## Baseline

LogisticRegression(
    max_iter=2000,
    class_weight="balanced",
    random_state=42
)

O classificador foi incluído no Pipeline,
mas ainda não foi treinado.

## Evitando vazamento de dados

As transformações aprenderão os parâmetros
apenas durante fit() no treino.

O teste não será utilizado para ajustar
imputação, padronização ou codificação.

## Próxima etapa

Treinar o baseline.
Calcular métricas de classificação.
Registrar a primeira run no MLflow.

## Observação

A transcrição menciona 65% de treino e,
mais adiante, 4000 registros. O código
efetivamente apresentado utiliza 75%
de 6000, ou seja, 4500 observações.
