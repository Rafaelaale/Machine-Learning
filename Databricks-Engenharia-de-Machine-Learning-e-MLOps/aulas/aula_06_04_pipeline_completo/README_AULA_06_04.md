# Aula 6.4 - Construindo o Pipeline Final

## Origem
Os sete codigos vieram da Aula 6.3 e foram copiados
para notebooks/. Os originais permanecem inalterados.

## Workflow
ingestao_dados
pre_processamento
treinamento
dados_prod
monitoramento_drift
check_re_treino
re_treino_modelo (somente com drift)
deploy_modelo (com ou sem drift)

## Targets
dev, stage e prod.

## Correcoes realizadas
1. Catalogos dinamicos no JOIN da ingestao.
2. taskKey dados_prod no monitoramento.
3. predict_proba para score da classe positiva.

## Pendencias para Databricks real
- Os CSVs ainda sao lidos de
  /Volumes/workspace/bronze/raw/
- Os notebooks exigem Spark, dbutils,
  Feature Store, MLflow e bibliotecas.
- A UDF de previsao precisa de teste
  no ambiente remoto.
- Bundle validate oficial nao executado.
- Jobs remotos nao criados nem executados.
- GitHub Actions remoto nao executado.
- Deploy remoto nao realizado.

A auditoria verifica YAML, codigo e
o encadeamento logico. Nao executa
os sete notebooks produtivos.

## Fonte oficial
https://github.com/alura-cursos/6123-alura-ml-databricks