# Módulo 01 - Do repositório ao modelo treinado

## Objetivo
Desenvolver um classificador de anomalias em motores industriais.

## Aulas
1. Repositório e primeiros passos
2. Análise exploratória de dados
3. Desenvolvimento de modelo de Machine Learning
4. Estrutura inicial do projeto

## Fonte de dados esperada
Banco SQLite: motor.db

Tabelas:
- motores
- leituras
- tipos_falha

Sensores:
- rotacao_rpm
- vibracao_mm_s
- temperatura_c
- corrente_a

## Engenharia de Machine Learning
- Features temporais por motor
- GroupBy e Rolling
- Pipeline StandardScaler + RandomForestClassifier
- Class Weight Balanced
- F1 Macro
- StratifiedKFold
- RandomizedSearchCV
- Joblib

## Regras do laboratório
- Python 3.11
- Ambiente virtual exclusivo
- Preservar o banco original
- Não criar dados fictícios como se fossem reais
- Salvar todos os códigos das aulas
- Validar cada implementação
- Verificar custos antes de qualquer uso da AWS

## Status
Visão geral registrada.
Aulas práticas ainda não executadas.
