# Aula 14 - Modelos com PyFunc

## Objetivo

Criar uma interface de inferencia personalizada
sem treinar outro algoritmo.

## Modelo de origem

risco_credito_classifier@production

## Novo modelo

risco_credito_classifier_pyfunc

## Classe

CreditRiskPyfuncModel

Herda de mlflow.pyfunc.PythonModel.

## Metodos

__init__:
Define colunas e limiar padrao.

load_context:
Carrega o pipeline sklearn do artefato.

predict:
Valida entrada, calcula probabilidade,
aplica limiar e devolve DataFrame.

## Entrada

Oito features do dataset sintetico.

## Saida

probabilidade_inadimplencia
classe_prevista
limiar_utilizado

## Limiar

Padrao: 0.50
Alternativo: 0.30

Alterar limiar nao muda a probabilidade.
Pode mudar a classe prevista.

## Signature

Descreve features de entrada,
colunas de saida e parametro threshold.

## Registry

Aliases:
candidate
servingCandidate

## Proxima aula

Serving REST, payloads e testes HTTP.

## Governanca

Modelo educativo.
Nao utilizar para conceder ou negar
credito real sem validacoes adicionais.
