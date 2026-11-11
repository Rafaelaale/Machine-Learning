# Aula 3.2 - Treinamento de Modelos no Databricks

## Fonte original

aula_3/aula_3_2_treinamento_modelos.ipynb

## Preparacao

- Dataset Iris: 150 registros.
- Feature Store: iris_features_table.
- FeatureLookup para quatro atributos.
- Training Set com species como target.
- Divisao estratificada: 80% treino e 20% teste.
- Quatro classificadores sklearn.
- Rastreamento com MLflow.
- Registro opcional no Unity Catalog.
- Demonstracao de AutoML com Bike Sharing.

## Correcoes do codigo do professor

1. Nao recriar id_flor com ordenacao aleatoria.
2. Reconstruir o target a partir dos atributos originais.
3. Validar a correspondencia de 150 registros.
4. Utilizar drop(columns=...) quando necessario.
5. Incluir assinatura para registro no Unity Catalog.
6. Encapsular escalonamento no Pipeline sklearn.
7. Nao sobrescrever tabelas Bike Sharing existentes.
8. Nao instalar pacotes sem necessidade.
9. Nao presumir que AutoML esta habilitado na Free Edition.

## Proxima execucao

Importar os notebooks preparados no Databricks.

Dependencias:
- workspace.default.iris_dataset
- workspace.default.iris_features_table
- Databricks Feature Engineering
- Permissoes de MLflow e Unity Catalog

A preparacao local nao confirma as tabelas na nuvem.

## Seguranca

Nenhum token armazenado.
Nenhum deploy automatico.
Nenhum arquivo original alterado.
Nenhuma publicacao realizada.