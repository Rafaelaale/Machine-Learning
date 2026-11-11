# Aula 3.4 - Treinando Modelos do Projeto

## Fonte
aula_3/aula_3_4_projeto_modelos.ipynb

## Regra de negocio
Prever compra de produtos da categoria Eletronicos.

Target:
finalizar_compra + categoria Eletronicos = 1.
Demais casos = 0.

## Estrategia temporal
Treino: janeiro a abril de 2025.
Validacao: maio e junho de 2025.
Teste futuro: julho a dezembro de 2025.

Features calculadas somente com dias anteriores.

## Algoritmos
1. Regressao Logistica
2. Random Forest
3. Gradient Boosting
4. XGBoost
5. LightGBM

## MLOps
- Feature Engineering Client
- FeatureLookup
- MLflow Tracking
- Optuna para LightGBM
- SHAP para interpretabilidade

## Correcoes
- Nao incluir eventos futuros nas features.
- Somar somente precos de compras realizadas.
- Nao otimizar com o conjunto de teste.
- Manter a divisao temporal.
- Preservar as tabelas anteriores.
- Nao promover modelos automaticamente.

## Estado
Preparacao local concluida quando a sintaxe passar.
Treinamento real somente apos executar no Databricks.