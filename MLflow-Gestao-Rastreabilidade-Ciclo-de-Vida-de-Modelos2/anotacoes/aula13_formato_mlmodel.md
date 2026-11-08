# Aula 13 - Formato MLmodel

## Objetivo

Inspecionar o pacote MLflow registrado
e compreender seu contrato de inferencia.

## Modelo

risco_credito_classifier

Alias: production

## Componentes do pacote

MLmodel: metadados YAML.
Arquivo serializado: model.skops.
requirements.txt: dependencias.
conda.yaml: ambiente Conda.
python_env.yaml: ambiente Python.
Input example: exemplo de entrada.

A lista exata deve ser conferida no inventario.

## Flavors

sklearn:
Permite predict e predict_proba.

python_function:
Fornece interface generica predict.

## Signature

Descreve nomes, tipos e estrutura
dos dados esperados.

## Validacao

1. Entrada valida com tres linhas.
2. Coluna obrigatoria ausente.
3. Coluna extra.
4. Consistencia entre flavors.

## Limites

A signature nao substitui regras de negocio,
validacao de valores ou controle de limiares.

## Proxima etapa

Criar PyFunc personalizado com saida
mais explicita para inferencia.

## Seguranca

Utilizar apenas modelos confiaveis.
Dados sinteticos para estudo.
Nenhuma decisao real de credito.
