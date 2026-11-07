<!-- PORTFOLIO_TECNOLOGIA_2026 -->

# Portfólio Técnico | Python, Dados e Engenharia de Software

**Desenvolvimento Python | Engenharia de Dados | Machine Learning**

Portfólio de estudos e implementações práticas em Python,
desenvolvimento de software, testes automatizados,
engenharia de dados e aprendizado de máquina.

Os projetos apresentam código-fonte, laboratórios,
documentação técnica e resultados de testes.

## Projetos em destaque

### 1. Design Patterns em Python

[Explorar projeto](Design-Patterns-Python-Factory-Strategy/)

Trilha prática com 27 aulas implementadas em Python.

**Conteúdos estudados:**
- Singleton e concorrência
- Injeção de dependências e Composition Root
- Lazy Loading e Proxy
- Simple Factory e Factory Method
- Registry
- Decorator, closures e nonlocal
- Strategy com classes, funções e lambdas
- Introdução a Template Method
- Testes automatizados com unittest

**Validação:** 432 testes aprovados na última execução local registrada.

**Competências demonstradas:** orientação a objetos,
organização de código, padrões de projeto e testes.

### 2. Engenharia de Dados — Minishop

[Explorar projeto](engenharia-de-dados-arquiteturas-modernas/)

Projeto educacional de arquitetura moderna de dados.

**Conteúdos:**
- Python e SQL
- OLTP e OLAP
- Data Warehouse e modelagem dimensional
- ETL e transformação de dados
- Data Lake e arquitetura Bronze, Silver e Gold
- Lakehouse, DuckDB e Parquet
- Qualidade, linhagem e catálogo de dados

**Validação registrada no projeto:** 408 testes locais aprovados.

### 3. Machine Learning e AWS para Ciência de Dados

[Consultar documentação original](#documentacao-original-do-projeto-machine-learning)

Estudo aplicado a registros históricos de doenças cardíacas,
utilizando pré-processamento e modelos de classificação.

**Tecnologias documentadas:**
- Pandas e NumPy
- Scikit-learn
- Regressão Logística e KNN
- SQL e DuckDB
- Avaliação com precisão, recall, F1-score e matriz de confusão
- Organização de dados para análises

O estudo registra acurácia de 88,70% para Regressão Logística.
É um experimento educacional, sem finalidade diagnóstica.

## Competências técnicas

| Área | Evidências no repositório |
|---|---|
| Python | Funções, classes, tratamento de regras e aplicações |
| Engenharia de Software | Design Patterns, orientação a objetos e testes |
| Engenharia de Dados | SQL, ETL, modelagem, Data Lake e Lakehouse |
| Machine Learning | Preparação de dados, treinamento e métricas |
| Qualidade de Software | Laboratórios e testes automatizados |
| Documentação | Anotações, resultados e instruções técnicas |

## Organização e reprodução

Cada projeto possui arquivos próprios de implementação,
testes e documentação.

Os resultados de testes informados são de execuções locais.
A reprodução requer as dependências de cada projeto.

Os laboratórios AWS descritos neste repositório foram
executados localmente; não representam implantação real na nuvem.

## Outros estudos e projetos

Acesse o perfil completo para explorar outras implementações
em IA, desenvolvimento de APIs e Salesforce:

[Ver todos os repositórios](https://github.com/Rafaelaale?tab=repositories)

## Autor

Rafael Alexandre Oliveira Araujo

[Perfil no GitHub](https://github.com/Rafaelaale)

---

## Documentação original do projeto Machine Learning

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
