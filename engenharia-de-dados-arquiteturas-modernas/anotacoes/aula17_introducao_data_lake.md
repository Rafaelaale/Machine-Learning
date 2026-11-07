# Aula 17 - Introducao ao Data Lake

## Arquitetura classica

OLTP -> ETL -> Data Warehouse -> BI

O OLTP registra operacoes.

O ETL transforma dados operacionais
em estruturas analiticas.

O Data Warehouse organiza fatos e
dimensoes para consultas de negocio.

## Limitacoes discutidas

Crescimento do volume de dados.

Diversidade de fontes e formatos.

Complexidade crescente do ETL.

Dependencia da disponibilidade do OLTP.

Dificuldade de recuperar historicos
quando os dados brutos foram eliminados.

## Data Lake

Repositorio de dados brutos, antes das
transformacoes analiticas.

Pode armazenar:
- Dados estruturados
- Dados semiestruturados
- Dados nao estruturados

Formatos comuns:
SQLite, CSV, JSON, logs, imagens e outros.

## Schema on Write

Esquema definido e aplicado antes da
carga na estrutura analitica.

Conceito associado ao Data Warehouse.

## Schema on Read

Armazenar os dados e interpretar
seu formato posteriormente.

Neste laboratorio, JSONL e SQLite
sao interpretados na leitura.

## Camada Raw

Local:
dados/lake/raw/minishop

Cada snapshot possui:
oltp.sqlite
clientes.csv
pedidos.jsonl
manifest.json

O SQLite representa uma fotografia
consistente do OLTP.

CSV e JSONL representam informacoes
extraidas sem aplicar regras analiticas.

O manifest registra hashes SHA-256,
identificador e contagens de tabelas.

## Camada Curated

Local:
dados/lake/curated/minishop

Armazena:
resumo_vendas.json
vendas_tratadas.csv

Os dados sao derivados do snapshot bruto.

O resultado nao substitui nem altera a Raw.

## Preservacao historica

Cada estado logico do OLTP recebe um
identificador baseado em seu conteudo.

Se nao houve mudanca:
reutilizamos o snapshot existente.

Se os dados mudaram:
criamos um novo snapshot.

Snapshots anteriores permanecem disponiveis.

## Papel do Data Warehouse

O Data Lake nao precisa substituir o DW.

O Data Lake pode preservar fontes brutas.

O DW pode continuar fornecendo modelos
dimensionais e indicadores para BI.

## Limites do laboratorio

Este e um Data Lake local didatico.

Nao implementa armazenamento de objetos
como S3, Azure Data Lake ou Google Cloud.

Nao implementa controle de acesso,
criptografia, catalogo corporativo,
retencao automatica nem distribuicao.

A preservacao e feita por convencao,
com verificacao por hashes. Nao e WORM
nem protecao contra adulteracao maliciosa.

A captura do SQLite e consistente,
mas representa o estado atual disponivel.

Nao recria automaticamente historicos
que ja foram apagados antes da ingestao.

## Proxima aula

Aprofundar organizacao e tecnologias
utilizadas em Data Lakes.
