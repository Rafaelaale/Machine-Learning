# MLflow — Gestão e Rastreabilidade do Ciclo de Vida de Modelos

Projeto prático de Machine Learning e MLOps com Python, Scikit-learn, MLflow e Docker.

## Resultados

| Indicador | Resultado |
|---|---|
| Testes automatizados | 272 aprovados localmente |
| Modelo | Random Forest |
| ROC-AUC | 82,88% |
| Acurácia | 76,27% |
| Precisão | 67,85% |
| Recall | 74,79% |
| F1-score | 71,15% |

## Tecnologias

Python 3.12, MLflow, Scikit-learn, Pandas, NumPy, Docker, SQLite, PyFunc, API REST e unittest.

## Funcionalidades

- Rastreamento e comparação de experimentos
- Treinamento e avaliação de modelos de classificação
- Registro e versionamento no MLflow Model Registry
- Serving com PyFunc e API REST
- Empacotamento e validação com Docker
- Pipeline reproduzível com prepare, train, evaluate e pipeline
- Tracking Server HTTP em ambiente local
- Auditoria MLOps, Model Card e matriz de maturidade

## Modelo registrado

`models:/risco_credito_project_model/2`

## Organização

- `src/`: códigos Python
- `tests/`: testes automatizados
- `scripts/`: ferramentas auxiliares
- `notebooks/`: notebooks das aulas
- `anotacoes/`: documentação técnica
- `MLproject`: configuração dos entry points
- `python_env.yaml`: especificação do ambiente

## Execução

Com as dependências e o Tracking URI configurados, executar:

```powershell
python -m mlflow run . -e pipeline -P model_name=random_forest --env-manager local
```

O pipeline gera novas execuções e pode registrar outra versão do modelo.

## Limitações

Projeto educacional baseado em dados sintéticos. Não está aprovado para decisões reais de crédito nem representa infraestrutura corporativa em produção.

Os 272 testes foram aprovados no ambiente local original. Parte da suíte depende de dados, modelos e runs gerados durante as aulas.
