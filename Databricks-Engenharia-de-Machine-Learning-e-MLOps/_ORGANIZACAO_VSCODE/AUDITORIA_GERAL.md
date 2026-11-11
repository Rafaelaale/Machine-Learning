# Auditoria Geral - Databricks MLOps

Data: 2026-11-11 02:01:50

- Arquivos inventariados: 196
- Grupos de copias identicas: 11
- Backups/temporarios: 5
- Arquivos grandes (10 MB ou mais): 1

## Verificacoes

| Verificacao | Resultado | Detalhe |
|---|---|---|
| 05.02 - Drift | OK | aulas/aula_05_02_drift_aprimorado |
| 05.03 - Jobs | OK | aulas/aula_05_03_jobs |
| 05.04 - Alertas | OK | aulas/aula_05_04_alertas_locais |
| 05.05 - Retreino | OK | aulas/aula_05_05_retreino_local |
| 05.06 - DABs | OK | aulas/aula_05_06_iac_dabs |
| 06.01 - CI/CD | OK | aulas/aula_06_01_cicd_mlops |
| 06.02 - GitHub Actions | OK | aulas/aula_06_02_github_actions |
| 06.03 - Codigos produtivos | OK | aulas/aula_06_03_pipeline_final |
| 06.04 - Pipeline completo | OK | aulas/aula_06_04_pipeline_completo |
| 06.05 - Unity Catalog | OK | aulas/aula_06_05_unity_catalog_acessos |
| Sete notebooks da Aula 6.4 | OK | Encontrados: 7 |
| Bundle e oito tarefas | OK | 8 tarefas |
| Auditoria anterior da Aula 6.4 | OK | 8 tarefas, 7 notebooks e 6 cenarios |
| Aula 6.5 - Acessos | OK | Oito testes de permissoes |
| Aula 6.2 - Tres ambientes | OK | DEV, STAGE e PROD |

## Pontos de atencao

- Nenhum problema nas verificacoes realizadas.

## Backups e temporarios identificados

- `aulas/aula_05_06_iac_dabs/VALIDAR_IAC_LOCAL.py.backup_20261111_005516`
- `aulas/aula_06_01_cicd_mlops/VALIDAR_IAC_LOCAL.py.backup_20261111_010807`
- `aulas/aula_06_04_pipeline_completo/notebooks/01_ingestao_dados.py.antes_ajuste_20261111_014612.bak`
- `aulas/aula_06_04_pipeline_completo/notebooks/05_monitoramento_drift.py.antes_ajuste_20261111_014612.bak`
- `aulas/aula_06_04_pipeline_completo/notebooks/07_deploy_modelo.py.antes_ajuste_20261111_014612.bak`

## Arquivos grandes

- `material-alura/6123-alura-ml-databricks/aula_2/aula_2_3_projeto_features.ipynb` - 10.6 MB

## Organizacao aplicada

- Workspace focado nas aulas criado.
- Workspace de visao geral criado.
- Indice e inventario gerados.
- Caches ocultos somente no Explorador.
- Arquivos anteriores preservados.
- Configuracoes globais do VS Code preservadas.
- Nenhum deploy remoto realizado.

## Limitacoes

- Esta auditoria nao executa Spark nem MLflow.
- Nao verifica Jobs remotos do Databricks.
- Copias identicas podem ser intencionais.
- Nenhum arquivo foi removido automaticamente.
