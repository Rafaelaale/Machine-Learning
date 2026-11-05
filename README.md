# Machine Learning — AWS para Ciência de Dados

Projeto educacional completo de Ciência de Dados, Machine Learning
e Engenharia de Dados, desenvolvido durante uma trilha da Alura.

## Objetivo

Explorar dados históricos de doenças cardíacas, realizar
pré-processamento, treinar classificadores, avaliar modelos
e construir um fluxo de dados para consultas SQL.

## Tecnologias

- Python 3.11
- Pandas e NumPy
- Scikit-learn
- Matplotlib
- Joblib
- PyArrow e Parquet
- DuckDB e SQL
- PowerShell
- VS Code

## Serviços AWS estudados

- Amazon S3
- IAM
- Amazon SageMaker
- AWS Glue e Data Catalog
- Amazon Athena
- Gerenciamento de custos

**Importante:** os serviços AWS foram estudados e suas
funcionalidades reproduzidas em laboratório local gratuito.
Este projeto não representa implantação real na AWS.

## Fluxo desenvolvido

1. Organização do Data Lake local.
2. Análise exploratória de 918 registros.
3. Separação em treinamento e teste.
4. Pré-processamento sem ajuste no conjunto de teste.
5. Treinamento de Regressão Logística e KNN.
6. Avaliação com métricas e matriz de confusão.
7. Persistência do modelo com Joblib.
8. Catalogação de dados e ETL.
9. Conversão de CSV para Parquet com Snappy.
10. Análises SQL com DuckDB.

## Resultados de Machine Learning

| Métrica | Regressão Logística | KNN |
|---|---:|---:|
| Acurácia | 88,70% | 83,91% |
| Precisão | 89,15% | 85,16% |
| Recall | 90,55% | 85,83% |
| F1-score | 89,84% | 85,49% |

A Regressão Logística apresentou 12 falsos negativos
no conjunto de teste, contra 18 do KNN.

## Estrutura

- `aulas/`: códigos e materiais de estudo.
- `resultados/`: relatórios, gráficos e métricas.
- `s3_local/hospital-dados/raw/`: dataset original.
- `s3_local/hospital-dados/processed/`: dados transformados.
- `s3_local/hospital-dados/predictions/`: modelo e previsões.

## Limitações

Este é um projeto educacional com um dataset histórico.
Não deve ser utilizado para diagnóstico, triagem ou
decisões clínicas. Os resultados não comprovam causalidade.

O modelo serializado requer o pré-processamento compatível
e deve ser carregado somente de origem confiável.

## Autor

Rafael Alexandre Oliveira Araujo

GitHub: https://github.com/Rafaelaale
