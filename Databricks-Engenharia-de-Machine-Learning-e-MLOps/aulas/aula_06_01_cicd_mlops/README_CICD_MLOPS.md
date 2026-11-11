# Aula 6 - CI/CD para MLOps

## Material oficial da Alura

https://github.com/alura-cursos/6123-alura-ml-databricks

Arquivos de referencia:
- .github/workflows/deploy.yml
- databricks.yml
- aula_6/pipeline/

## Estrutura criada

databricks.yml
resources/jobs.yml
notebooks/
VALIDAR_IAC_LOCAL.py
validar_promocao.py
exemplos/deploy_remoto_desativado.yml

Workflow na raiz do projeto:
.github/workflows/alura_mlops_ci.yml

## Ambientes

Branch develop -> target dev -> catalogo dev
Branch stage -> target staging -> catalogo stag
Branch main -> target prod -> catalogo prod

Esses catalogos nao foram criados no Databricks.
A definicao representa ambientes futuros.

## Regras de promocao

develop -> stage: permitido
stage -> main: permitido
develop -> main: bloqueado
feature -> main: bloqueado

A politica de branches foi simulada localmente.

Para protecao real, configurar regras de
branch e aprovacoes no GitHub.

## GitHub Actions

O workflow CI valida:
- Bundle YAML e notebooks
- Ordem das cinco tasks
- Dependencias do workflow
- Politica de promocao por PR

Nao executa deploy remoto.

Para executar no GitHub, os arquivos precisam
estar publicados no mesmo repositorio com o
workflow na pasta .github/workflows da raiz.

## Deploy futuro

O exemplo de deploy remoto esta fora da
pasta ativa de workflows.

Nao copiar o exemplo para .github/workflows
sem antes configurar o Databricks, credenciais,
permissoes e aprovacao de producao.

Credenciais devem ficar em GitHub Secrets.
Nunca salvar token no codigo.

## Etapas futuras da carreira

O repositorio oficial inclui sete scripts:
01_ingestao_dados.py
02_pre_processamento.py
03_treinamento_modelo.py
04_gerando_dados_produtivos.py
05_monitoramento_drift.py
06_re_treino.py
07_deploy_modelo.py

Esses sete scripts ainda nao foram integrados
ao pacote local nesta aula introdutoria.

## Pendencias

- Publicacao no GitHub: nao realizada.
- GitHub Actions na nuvem: nao executado.
- Workspace Databricks: nao conectado.
- Catalogos dev/stag/prod: nao criados.
- Deploy real: nao realizado.
- Jobs remotos: nao executados.