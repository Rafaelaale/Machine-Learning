# Aula 13 - Politica de versionamento

## Objetivo

Preparar o projeto de churn para futuro
controle de versoes e trabalho colaborativo.

## Situacao

Versionamento remoto nao realizado nesta aula.

Publicacao prevista somente apos a conclusao
e revisao da trilha.

## Branches estudadas

- main
- feature/preprocessamento
- fix/tratamento-nulos
- docs/documentacao
- test/cobertura

## Fluxo conceitual

1. Criar uma branch.
2. Alterar codigo e testes.
3. Executar validacoes.
4. Registrar commit.
5. Enviar a branch ao remoto.
6. Abrir pull request.
7. Fazer code review.
8. Integrar a alteracao aprovada.

O fluxo acima sera executado apenas quando
a publicacao for autorizada.

## Arquivos que exigem cuidado

Nao publicar automaticamente:

- .venv/
- __pycache__/
- .env
- chaves e credenciais
- arquivos de cobertura
- modelos binarios

Revisar antes de qualquer publicacao:

- datasets
- arquivos originais da Alura
- resultados gerados
- notebooks com dados incorporados

## Checklist de revisao

- O codigo possui testes?
- A documentacao acompanha as mudancas?
- Foram revisadas credenciais e informacoes privadas?
- Os dados podem ser distribuidos?
- Existem alteracoes acidentais?
- As dependencias estao documentadas?
- O modelo atende aos criterios de qualidade?
- Existe uma pessoa responsavel pela revisao?

## Estado do modelo

A Aula 07 registrou recall igual a zero
para a classe churn.

O projeto continua educacional.

## Limites da auditoria

A triagem automatica classifica caminhos e
extensoes. Ela nao substitui a leitura dos
arquivos nem identifica todos os segredos.

Nenhum comando Git e executado neste laboratorio.
