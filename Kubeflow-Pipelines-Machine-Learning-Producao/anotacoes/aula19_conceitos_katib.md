# Aula 19 — Conceitos Katib

## HPO
Hyperparameter Optimization: busca automatizada de hiperparâmetros.

## Katib
Componente do Kubeflow que executa experimentos
de otimização usando Kubernetes.

Compatível com diferentes modelos e bibliotecas:
- XGBoost
- TensorFlow
- PyTorch
- Scikit-learn

## Experimento
Definido por um arquivo YAML contendo:
1. Métrica objetivo.
2. Direção da otimização: maximizar ou minimizar.
3. Algoritmo de busca.
4. Hiperparâmetros e seus intervalos.
5. Configuração das execuções (trials).

## Trials
Cada trial testa uma configuração de hiperparâmetros,
treina o modelo e registra a métrica obtida.

## Nosso projeto
Modelo: XGBoost.
Métrica: val_pr_auc.
Objetivo: maximizar.

Hiperparâmetros:
- eta
- max_depth
- n_estimators

## Resultado esperado nas próximas aulas
Identificar a melhor combinação encontrada nos trials.

## Situação
Aula teórica. Nenhum experimento executado nesta etapa.
