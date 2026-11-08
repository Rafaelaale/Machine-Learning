# Model Card - Risco de credito

## Identificacao
- Projeto: MLflow - Gestao e Rastreabilidade
- Modelo: risco_credito_project_model
- Versao: 2
- Model URI: `models:/risco_credito_project_model/2`
- Pipeline ID: `aula18_7dc096cb75de`

## Objetivo
Classificacao didatica de inadimplencia com dados sinteticos.

## Dados
- Amostras: 6000
- Proporcao de teste: 0.25
- Semente: 42

## Metricas da avaliacao
- ROC-AUC: 0.8288
- Acuracia: 0.7627
- Precisao: 0.6785
- Recall: 0.7479
- F1: 0.7115

## Rastreabilidade
- Parent run: `b6d1631014f140259dee4730011c0590`
- Prepare run: `b42358c97c524f60a0ca4f9d7905a8e5`
- Train run: `9c0ab0bb72fe4630b3a36344e96b1112`
- Evaluate run: `abb2225e9045448995fd9b4519ab62e1`

## Limitacoes
- Dados sinteticos nao representam toda a populacao real.
- Nao houve validacao com dados reais de credito.
- Nao houve analise completa de fairness, bias ou drift.
- Nao existe aprovacao regulatoria ou corporativa.
- Nao foram estabelecidos SLAs de producao.

## Uso permitido
Demonstracao, estudo, testes e portfolio tecnico.

## Uso nao aprovado
Decisoes reais de concessao de credito.

## Governanca
Nenhuma promocao automatica para producao.
Aprovacao humana e avaliacao de riscos sao necessarias.
