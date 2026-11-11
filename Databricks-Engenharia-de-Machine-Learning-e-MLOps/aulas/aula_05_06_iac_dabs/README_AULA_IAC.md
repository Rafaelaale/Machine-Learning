# Aula - IaC e Databricks Asset Bundles

## Objetivo

Transformar em YAML o workflow desenvolvido
nas aulas anteriores.

## Fonte oficial

https://github.com/alura-cursos/6123-alura-ml-databricks

## Databricks

https://docs.databricks.com/aws/en/dev-tools/bundles/

## Arquivos

databricks.yml
resources/jobs.yml
notebooks/
VALIDAR_IAC_LOCAL.py
AUDITORIA_IAC.txt

## Workflow

1. carga_prod
2. monitoramento_drift
3. verificar_drift
4. condicao_drift
5. re_treino

O re_treino so deve executar quando
total_drift for maior que zero.

## Parametros

data_inicio: 20260501
data_fim: 20260601 (exclusiva)
features: renda_mensal_k,tempo_medio_clique_segundos
target: comprou_eletronico
gravar: true
catalogo: workspace
esquema: default

## Ambientes

dev: desenvolvimento
staging: homologacao
prod: producao

Estes targets definem configuracoes de Bundle.
Nao foram criados workspaces separados.

## Ajustes em relacao ao exemplo original

- Data final exclusiva.
- Particao dia_prtc.
- Feature renda_mensal_k.
- Tabelas aprimoradas.
- Logs filtrados pelo periodo da execucao.
- Retreino condicionado a drift do periodo.
- Parametros compartilhados no nivel do Job.
- Notebooks como caminhos relativos ao Bundle.

## Validacao

A verificacao local confirma:
- Presenca dos arquivos.
- Estrutura JSON dos notebooks.
- Sintaxe Python dos novos notebooks.
- Sequencia esperada das tarefas.
- Referencias dos caminhos.

Se PyYAML estiver instalado, a estrutura YAML
tambem sera analisada formalmente.

A validacao oficial do Bundle pelo Databricks CLI
ainda requer autenticacao em um workspace.

## Limitacoes importantes

Este pacote foi construido a partir do projeto local.
Nao foi exportado de um Job remoto existente.

Nao houve deploy.
Nao houve execucao Spark ou MLflow remota.
Nao houve criacao de recursos na nuvem.
Nao houve commit, push ou pull request.

A configuracao ainda precisa de validacao oficial
e teste de integracao antes de um deploy real.