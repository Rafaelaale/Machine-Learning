# Aula 12 - Testes automatizados em projetos de dados

## Objetivo

Garantir o comportamento das funcoes do pacote
pre_processamento criado na Aula 10.

## Pytest

Framework para executar testes automatizados
em Python.

## Convencoes

Arquivos: test_*.py
Funcoes: test_*

## Fixture

@pytest.fixture permite reutilizar preparacoes
de dados e objetos entre testes.

## tmp_path

Cria um diretorio temporario independente
para cada teste.

## assert

Compara os resultados com o comportamento esperado.

## pytest.raises

Confirma que entradas invalidas geram excecoes.

## pytest.mark.parametrize

Permite verificar varias entradas com a
mesma funcao de teste.

## pytest-cov

Calcula a cobertura das linhas executaveis.

Cobertura de 100% nao garante a ausencia de bugs.

## Testes implementados

- Leitura do CSV.
- Arquivos inexistentes.
- Colunas obrigatorias.
- Conversao de datas.
- Datas invalidas.
- Valores ausentes.
- Imputacao pela mediana.
- Codificacao de churn.
- Rotulos desconhecidos.
- Calculo de fidelidade.
- Calculo de score de gasto.
- Rejeicao de valores negativos.
- One-hot encoding.
- Integracao do pipeline.
- Preservacao do arquivo de entrada.
- Reprodutibilidade da execucao.

## Meta do laboratorio

Cobertura minima de 85% do modulo core.py.

Esse valor e uma meta didatica de cobertura,
nao uma garantia de qualidade de producao.

## Cuidados futuros

Validar o modelo de ML com metricas adequadas.

Evitar vazamento de dados no pre-processamento.

Garantir esquema de atributos consistente
entre treinamento e inferencia.

Acompanhar qualidade de dados e alteracoes
de distribuicao ao longo do tempo.
