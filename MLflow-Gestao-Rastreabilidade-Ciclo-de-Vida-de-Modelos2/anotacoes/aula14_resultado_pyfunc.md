# Aula 14 - Modelo PyFunc personalizado

## Modelo registrado

risco_credito_classifier_pyfunc

Versao: 1
Run: 45259251a2334facbc434a303348124f

## Modelo de origem

models:/risco_credito_classifier@production
Run de origem: af091af1fa744064837cbc1fd29ffb42

## Interface de entrada

Oito features do dataset sintetico.

## Interface de saida

- probabilidade_inadimplencia
- classe_prevista
- limiar_utilizado

## Resultado com threshold 0.50

 probabilidade_inadimplencia  classe_prevista  limiar_utilizado
                    0.934974                1               0.5

## Resultado com threshold 0.30

 probabilidade_inadimplencia  classe_prevista  limiar_utilizado
                    0.934974                1               0.3

## URI para serving

models:/risco_credito_classifier_pyfunc@servingCandidate

## Seguranca e governanca

Modelo apenas didatico.
Ainda nao promovido para production.
O modelo de origem foi preservado.
