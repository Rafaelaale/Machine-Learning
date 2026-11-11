# Aula 6.2 - Configurando GitHub Actions e arquivos YML

## Referencias Alura
https://github.com/alura-cursos/6123-alura-ml-databricks

Arquivos consultados:
- .github/workflows/deploy.yml
- databricks.yml
- aula_6/ingestao.py

## Estrutura

databricks.yml
resources/jobs.yml
notebooks/ingestao_databricks.py
validar_e_simular.py
VALIDAR_CATALOGOS_DATABRICKS.sql

Workflow no diretorio principal:
.github/workflows/deploy.yml

Se deploy.yml ja existir, utiliza:
.github/workflows/deploy_alura_local.yml

## Ambientes

develop -> dev
stage -> stage
main -> prod

## Promocao entre branches

develop -> stage: permitida
stage -> main: permitida
develop -> main: bloqueada

## Execucao local

A simulacao utiliza SQLite, nao Unity Catalog.

Tabelas:
dev_default_usuarios_bronze
stage_default_usuarios_bronze
prod_default_usuarios_bronze

Cada uma possui dois registros de teste.

## GitHub Actions

Quatro Jobs:
- simular-dev
- simular-stage
- validar-pr
- simular-prod

Os Jobs apenas validam YAML, codigo e tabelas locais.

O workflow so executara no GitHub depois
de ser publicado em um repositorio.

Nao ha deploy automatico do Databricks.

## Protecao de branches

A validacao de PR nao substitui a configuracao
de Branch Protection ou Rulesets do GitHub.

A protecao real ainda precisa ser configurada
no repositorio remoto.

## Segredos

Nao foram criados tokens.
Nao foram configurados Secrets.
Nao foram armazenadas credenciais.

## Pendencias

- Publicacao no GitHub: nao realizada.
- Criacao de branches remotas: nao realizada.
- Branch protection remota: nao realizada.
- GitHub Actions remoto: nao executado.
- Databricks remoto: nao conectado.
- Catalogos remotos: nao criados.
- Deploy: nao realizado.
- Criacao e execucao de Jobs remotos: nao realizada.

Todos os arquivos das aulas anteriores
devem permanecer preservados.