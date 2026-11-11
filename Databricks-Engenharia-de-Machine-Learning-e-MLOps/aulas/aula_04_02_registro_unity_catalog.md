# Aula 4.2 - Modelo de ML no Unity Catalog

## Fonte original
aula_4/aula_4_2_salvando_modelo_final.ipynb

## Objetivos
- Encoding de genero e regiao no PySpark.
- Preservacao das features temporais.
- Criacao de Feature Table codificada.
- FeatureLookup com chave temporal.
- Treinamento LightGBM.
- Optuna para hiperparametros.
- MLflow Tracking.
- Signature de entrada e saida.
- Registro opcional no Unity Catalog.

## Tabelas utilizadas

Origem:
workspace.gold.base_features_modelo_aula34

Observacoes:
workspace.gold.base_propensao_compra_observacao_aula34

Nova Feature Table:
workspace.gold.base_features_modelo_encoded_aula42

Modelo Unity Catalog:
workspace.gold.propensao_compra_modelo

O catalogo pode ser alterado pelo widget no Databricks.

## Validacoes

Treino: janeiro-abril de 2025.
Validacao: maio-junho de 2025.
Teste: julho-dezembro de 2025.

## Importante

Aula 3.4 precisa ser executada no Databricks
antes de executar este notebook.

A Signature e criada com as mesmas features
e os mesmos tipos utilizados pelo LightGBM.

O modelo e registrado no Unity Catalog somente
quando registrar_no_unity = sim.

O registro direto com mlflow.lightgbm.log_model
nao adiciona automaticamente a linhagem de features
necessaria para FeatureEngineeringClient.score_batch.

Para essa funcionalidade, precisaremos revisar
o registro com fe.log_model em uma aula posterior.

Nenhum endpoint, alias ou deploy automatico.
Nenhuma tabela anterior sera sobrescrita.