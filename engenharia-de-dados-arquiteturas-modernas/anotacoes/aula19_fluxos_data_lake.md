# Aula 19 - Fluxos de Dados com Data Lake

## Objetivo

Entender a mudanca do fluxo de dados quando
introduzimos o Data Lake na arquitetura.

## Arquitetura classica

OLTP -> ETL -> Data Warehouse

ETL significa:
Extract
Transform
Load

A transformacao acontece antes da carga
no ambiente analitico.

## Arquitetura com Data Lake

Primeiro fluxo:
Extract -> Load

Segundo fluxo:
Extract -> Transform -> Load

O primeiro fluxo preserva os dados brutos.

O segundo fluxo consome os dados
ja armazenados no Data Lake.

## Fluxo EL

Fonte:
OLTP da Minishop.

Destino:
Data Lake Bronze.

Operacoes:
Captura do banco SQLite.
Preservacao dos dados.
Registro de manifesto.
Verificacao de hashes SHA-256.

Nao prepara indicadores para BI.

A copia utiliza a rotina de ingestao
implementada na Aula 17.

## Fluxo ETL

Fonte:
Snapshot SQLite preservado na Bronze.

Operacoes:
Validar integridade.
Ler dados do snapshot.
Produzir Silver.
Produzir Gold.
Carregar dimensoes e fatos no DW.
Registrar auditoria do ETL.

Destino:
Data Warehouse separado.

O ETL utiliza o orquestrador da Aula 16.

## Vantagem central

A fonte original nao precisa estar
disponivel para reprocessar um snapshot
ja preservado no Data Lake.

O laboratorio inclui um teste que move
o arquivo OLTP original e reconstrói
o DW exclusivamente da Bronze.

## Camadas

Bronze:
Dados brutos preservados.

Silver:
Dados validados e padronizados.

Gold:
Indicadores preparados para consumo.

O Data Warehouse continua separado.

## Multiplos consumidores

Os dados da Bronze e Silver podem
alimentar diferentes projetos.

Exemplos da transcricao:
Business Intelligence.
Ciencia de Dados.
Machine Learning.
Inteligencia Artificial.

Nesta aula, implementamos o consumidor DW.

## Reconciliacao

Compara:
Faturamento Gold x DW.
Unidades Gold x DW.

A comparacao direta pressupoe um DW novo,
com o mesmo escopo do snapshot carregado.

Se o DW acumular outros periodos,
a reconciliacao precisa ser filtrada.

## Politica de reprocessamento

Os fatos do intervalo informado sao
substituidos pela carga do snapshot.

O processamento precisa receber os
dados completos daquele intervalo.

Novas ingestoes geram novos snapshots
quando o conteudo da origem muda.

## Limites

A implementacao continua local.

Nao ha armazenamento distribuido.

Nao foi criado um orquestrador externo
ou agendamento automatico.

A Silver e a Gold sao materializadas
a partir da Bronze.

O DW e carregado a partir do SQLite
preservado na Bronze.

Portanto, o fluxo nao exige retornar
ao OLTP original, mas tambem nao
exige que o DW leia diretamente
os arquivos CSV/JSONL da Silver.

O Data Lake pode ser consultado por
diferentes ferramentas em arquiteturas reais.

## Proxima aula

Modelar o Data Lake do e-commerce Minishop.
