# Aula 07 — Autolog e comparação de modelos

## Objetivo

Comparar três modelos de classificação
de risco de crédito usando MLflow autolog
e registro manual complementar.

## Experimento

risco_credito_comparacao_modelos

## Modelos

1. logistic_regression
2. decision_tree
3. random_forest

## Configuração

### Regressão logística

max_iter = 2000
class_weight = balanced
random_state = 42

### Árvore de decisão

max_depth = 5
min_samples_leaf = 50
class_weight = balanced
random_state = 42

### Random Forest

n_estimators = 100
max_depth = 8
min_samples_leaf = 20
class_weight = balanced
n_jobs = -1
random_state = 42

## Dados

Base sintética preparada na Aula 03.

Treinamento: 4500 registros.
Teste: 1500 registros.

## Pré-processamento

Para cada modelo, criamos um novo
ColumnTransformer com:

- SimpleImputer para numéricas;
- StandardScaler para numéricas;
- SimpleImputer para categóricas;
- OneHotEncoder para categóricas.

## Validação cruzada

StratifiedKFold com 3 folds.

Autolog fica desativado durante CV.

## Treinamento

Cada modelo é ajustado dentro de uma run
com o autolog ativado.

O autolog registra informações técnicas
do pipeline e do estimador.

## Registro manual complementar

Registramos métricas padronizadas:

- ROC-AUC teste;
- ROC-AUC CV média;
- ROC-AUC CV desvio;
- acurácia;
- precisão, recall e F1 dos inadimplentes;
- TN, FP, FN e TP.

## Comparação

O ranking inicial usa ROC-AUC no teste.

Isso ainda não define o campeão definitivo:
a decisão posterior deve considerar métricas
de negócio, estabilidade e custos operacionais.

## Arquivos gerados

resultados/aula07_comparacao_autolog.csv
resultados/aula07_comparacao_autolog.json

## Cuidados

Autolog pode registrar muitos parâmetros,
métricas e arquivos.

Durante esta aula, a observação dos modelos
automáticos é suficiente.

A análise interna do formato MLmodel fica
para uma etapa posterior.

## Próxima aula

Comparação das runs na interface e API.
