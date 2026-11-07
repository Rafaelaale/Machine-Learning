# Aula 18 - Arquitetura do Data Lake

## Objetivo

Estudar a organizacao do Data Lake e a
coexistencia entre Data Lake e Data Warehouse.

## Arquitetura classica

OLTP -> ETL -> Data Warehouse

As fontes alimentam processos de
transformacao e estruturas analiticas.

## Arquitetura com Data Lake

As fontes podem ser ingeridas primeiro
em um repositorio central de dados brutos.

Depois, diferentes consumidores podem
interpretar e transformar os dados.

## Tecnologias mencionadas na aula

Amazon S3.
Azure Data Lake Storage.
Google Cloud Storage.

Formatos:
CSV.
JSON.
Parquet.
ORC.

O laboratorio utiliza arquivos locais.
Nao implementa armazenamento em nuvem.

Os servicos de armazenamento de objetos
citados sao alternativas de infraestrutura;
nao dependem obrigatoriamente do Hadoop.

## Bronze - Raw

Objetivo:
Preservar dados brutos.

Implementacao:
Reutiliza os snapshots da Aula 17.

Arquivos:
oltp.sqlite
clientes.csv
pedidos.jsonl
manifest.json

A integridade e conferida por SHA-256.

## Silver - Staged

Objetivo:
Validar e padronizar os dados para consumo.

Transformacoes realizadas:
Verificacao de campos obrigatorios.
Validacao de tipos.
Verificacao de datas.
Verificacao de quantidades.
Conferencia de valor da venda.
Deteccao de duplicidades.

Saidas:
vendas_padronizadas.jsonl
vendas_padronizadas.csv
manifest.json

A Silver nao altera a Bronze.

## Gold - Curated

Objetivo:
Criar informacoes analiticas.

Saidas:
resumo.json
faturamento_diario.csv
faturamento_produtos.csv
manifest.json

Indicadores:
Quantidade de linhas.
Unidades vendidas.
Faturamento.
Dias com vendas.
Produtos distintos.

A Gold le somente a Silver.

## Schema on Read

A estrutura do dado bruto e interpretada
quando a Bronze e consumida.

Diferentes fontes podem exigir
interpretacoes e validacoes especificas.

## Schema on Write

A Silver e a Gold sao produzidas com
campos e tipos definidos previamente.

Os resultados tratados usam
esquemas de saida conhecidos.

## Preservacao e reprocessamento

Cada snapshot de origem recebe um
identificador de conteudo.

Uma nova versao nao substitui a anterior.

A Silver e a Gold sao organizadas
por snapshot_id.

Assim, podemos comparar resultados
gerados de diferentes capturas.

## Data Lake e Data Warehouse

O Data Lake pode alimentar o DW.

O DW continua importante para:
Modelagem dimensional.
Indicadores empresariais.
Business Intelligence.
Relatorios.

O Data Lake pode apoiar:
Exploracao de dados.
Ciencia de Dados.
Machine Learning.
Inteligencia Artificial.

## Limites do laboratorio

Implementacao local e didatica.

Nao utiliza:
S3, ADLS ou GCS.
Apache Spark.
Parquet ou ORC.
Catalogo corporativo.
Governanca automatizada.
Controle de acesso distribuido.

Os arquivos Gold representam
indicadores analiticos simples,
nao substituindo o DW da Aula 16.

O hash detecta alteracoes acidentais,
mas nao implementa armazenamento WORM.

## Proxima aula

Consultas, ingestao e transformacoes
com Data Lake na arquitetura.
