# Aula 01 — Apresentando o problema

## Curso
MLflow: gestão e rastreabilidade do ciclo de vida de modelos.

## Problema principal

Durante experimentos de Machine Learning, é comum:

- alterar hiperparâmetros;
- transformar os dados;
- executar novos treinamentos;
- obter métricas diferentes;
- salvar várias versões de um modelo;
- perder a informação de qual configuração gerou cada resultado.

Sem rastreabilidade, torna-se difícil reproduzir experimentos.

## Solução proposta: MLflow

O MLflow permite acompanhar:

1. Experimentos realizados.
2. Parâmetros de cada execução.
3. Métricas obtidas.
4. Artefatos produzidos.
5. Modelos resultantes.
6. Registro e versões dos modelos.

O MLflow não substitui a modelagem ou todos os processos de MLOps.

## Projeto prático

Classificação de risco de crédito.

Objetivo: estimar categorias de risco a partir de características
disponíveis em uma base de dados.

Nesta aula ainda não existe base fornecida ou modelo treinado.

## Três critérios de sucesso

### 1. Desempenho técnico
Avaliar os resultados por métricas de classificação.

### 2. Reprodutibilidade
Entender quais dados, parâmetros e procedimentos
produziram cada resultado.

### 3. Operacionalização
Registrar, versionar, empacotar e servir o modelo.

## Evolução prevista na trilha

Aula 01: problema e conceitos fundamentais.
Aula 02: ambiente, dados e baseline.
Aulas 03 a 05: tracking, autolog, runs e modelo campeão.
Aulas 06 e 07: registro e empacotamento.
Aula 08: inferência por API.
Aula 09: execução reprodutível.
Aula 10: tracking remoto e arquitetura MLOps.

## Cuidados com risco de crédito

Métricas técnicas não bastam, por si sós, para validar decisões
financeiras reais. Em aplicações de crédito, é importante
avaliar qualidade dos dados, vieses, explicabilidade e
necessidades de governança.

## Estado desta aula

Conteúdo conceitual registrado.

Nenhum modelo treinado.
Nenhuma base de dados inventada.
Nenhuma execução MLflow criada antecipadamente.
