# Aula 5.1 - Monitoramento de Modelos e Tipos de Drift

## Objetivo da aula

Entender por que modelos de Machine Learning precisam ser monitorados,
como detectar alteracoes de dados e predicoes e quando investigar o
retreinamento. A aula introduz jobs e pipelines, mas nao os executa.

## Tipos de drift

- Feature drift: distribuicao das entradas muda, P(X) se altera.
- Prediction drift: distribuicao das previsoes do modelo muda, P(f(X)).
- Concept drift: relacao entre X e o target verdadeiro Y muda, P(Y|X).

Uma mudanca na taxa total do target P(Y), isoladamente, nao comprova
concept drift. Para investigar conceito, precisamos observar a relacao
entre X e Y com rotulos confiaveis e comparar desempenho por periodo.

## Como monitorar

1. Definir uma referencia de treinamento e uma janela de producao.
2. Conferir qualidade: faltantes, tipos, categorias e volumes.
3. Comparar distribuicoes de features e predicoes.
4. Se houver target real, comparar desempenho (AUC, recall, precisao).
5. Investigar sazonalidade e alertas antes de decidir retreinar.
6. Validar um novo modelo fora da amostra antes de promover Champion.

## Estatistica

O teste Kolmogorov-Smirnov (KS) compara distribuicoes numericas.
Um p-value pequeno sugere diferenca estatistica, nao demonstra
perda de qualidade nem causalidade. Com muitas features, controlar
multiplas comparacoes e considerar tamanho do efeito e volume.

## Observacoes no material original da Alura

- O monitoramento usa KS e variacao relativa de conversao.
- A taxa de conversao sozinha nao comprova concept drift.
- O notebook de verificacao conta alertas historicos, sem janela.
- A geracao produtiva usa append e pode duplicar periodos.
- O retreinamento original muda o alias Champion automaticamente.
- O retreinamento usa divisao aleatoria, nao uma validacao temporal.
- O conjunto sintetico de monitoramento precisa ser comparado
  com cuidado: suas features nao reproduzem exatamente as 16 da Aula 4.2.
- O YAML tem caminhos de workspace a parametrizar (<SEU_EMAIL>).

## Diretrizes para o projeto

- Preservar notebooks originais e tabelas anteriores.
- Nao instalar dependencias para esta introducao.
- Nao criar, executar ou agendar jobs nesta aula.
- Nao sobrescrever tabelas ou alterar aliases.
- Nao presumir que o modelo foi treinado na nuvem.

## Arquivos locais

- scripts/auditar_aula_05_drift.py: inspeciona notebooks e YAML da Alura.
- scripts/demonstrar_tipos_drift.py: simulacao didatica sem Databricks.
- relatorios/auditoria_aula_05_01_drift.txt: resultado da auditoria.

## Estado

Preparacao e demonstracao locais. Monitoramento real pendente no Databricks.