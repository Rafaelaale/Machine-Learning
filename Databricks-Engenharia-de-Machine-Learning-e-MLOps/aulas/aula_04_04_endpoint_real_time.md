# Aula 4.4 - Endpoint e Deploy Real Time

## Material original

aula_4/aula_4_4_deploy_real_time.ipynb

## Objetivos

- Verificar modelo registrado no Unity Catalog.
- Selecionar a versao do modelo.
- Validar as 16 features pela Signature.
- Verificar endpoint existente com Databricks SDK.
- Confirmar estado READY.
- Confirmar a versao servida pelo endpoint.
- Criar 5 clientes sinteticos.
- Consultar endpoint com dataframe_records.
- Medir tempo de resposta de cada requisicao.

## Modelo

workspace.gold.propensao_compra_modelo

## Endpoint sugerido

modelo_propensao

O nome pode ser alterado pelo widget do notebook.

## Seguranca

Nenhum token sera armazenado.

Nenhum endpoint sera criado automaticamente.

Nenhuma requisicao sera enviada por padrao.

O alias Champion nao sera alterado.

Para enviar os testes, habilitar o widget e confirmar:
ENVIAR 5 TESTES

## Dependencias

Aula 4.2 executada na nuvem.
Modelo registrado no Unity Catalog.
Endpoint criado e pronto no Model Serving.
Permissao para consultar o endpoint.

## Importante

Alterar Champion nao atualiza automaticamente
a versao implantada em um endpoint existente.

A disponibilidade do Model Serving pode ser
limitada no Databricks Free Edition.

Esta aula prepara o teste.
A execucao real depende do workspace Databricks.