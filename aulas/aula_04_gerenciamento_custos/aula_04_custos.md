# Aula 04 - Custos e boas praticas

## Pontos principais

- AWS trabalha com cobranca por uso.
- Free Tier e creditos possuem regras e limites.
- Glue pode cobrar por DPU e tempo de execucao.
- Athena pode cobrar pela quantidade de dados consultados.
- SageMaker pode gerar custos de computacao e armazenamento.
- S3 pode cobrar armazenamento, requisicoes e transferencia.
- Alertas de orcamento nao impedem toda cobranca.
- Precos dependem de regiao, servico e configuracao.

## Nossa regra

Orcamento de uso real na AWS: R$ 0.

## Alternativas locais

- S3: Moto
- Glue: Python e PySpark
- Athena: DuckDB
- SageMaker: Scikit-learn e Jupyter

## Exercicio

Calcular dois cenarios hipoteticos de custo:
1. Glue com 2 DPUs por 30 minutos.
2. Athena consultando 0.01 TB.

Os valores sao ilustrativos e nao incluem todos
os componentes de cobranca.

Nenhum recurso real da AWS sera criado.
