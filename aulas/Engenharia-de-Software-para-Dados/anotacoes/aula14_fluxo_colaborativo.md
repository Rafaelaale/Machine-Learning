# Aula 14 - Fluxo de Trabalho Colaborativo

## Objetivo

Estudar organizacao e colaboracao em projetos
de Ciencia de Dados.

## GitFlow

Modelo com diferentes branches.

Principais tipos:
- main: versao principal
- develop: integracao de desenvolvimento
- feature: novas funcionalidades
- release: preparacao de versoes
- hotfix: correcoes urgentes

## Trunk-Based Development

Fluxo centrado na branch principal.

Caracteristicas:
- Branches de curta duracao.
- Integracoes frequentes.
- Alteracoes pequenas.
- Automacao de testes.
- Revisao rapida de codigo.

## Code review

Revisao de alteracoes antes de integrar
codigo no projeto principal.

## Criterios de integracao

- Testes automatizados aprovados.
- Revisao aprovada.
- Politica de cobertura atendida.
- Validacao das metricas do modelo,
  quando a alteracao afeta producao.

## Cobertura nao e desempenho do modelo

A Aula 12 obteve 98,02% de cobertura
do modulo core.py.

A Aula 07 mostrou recall de 0% para churn.

Um projeto pode ter codigo bem testado
e um modelo preditivo inadequado.

## Laboratorio

Criamos um simulador de integracao que
compara GitFlow e Trunk-Based.

O laboratorio verifica bloqueios, alertas
e regras de revisao.

Nenhum comando Git foi executado.

## Observacao

Os limites de cobertura e recall utilizados
na simulacao sao didaticos.

Cada organizacao deve definir suas politicas
conforme os requisitos do negocio.

## Aprendizado

O fluxo colaborativo deve considerar
o tamanho da equipe, a frequencia de
entrega e a capacidade de automacao.
