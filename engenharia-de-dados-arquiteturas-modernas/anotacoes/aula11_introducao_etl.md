# Aula 11 - Introducao ao Processo de ETL

## Objetivo

Entender como o Data Warehouse recebe dados
do OLTP atraves das etapas E, T e L.

## Extract

Extrair informacoes de fontes operacionais.

Fontes possiveis:
- Bancos de dados
- Arquivos
- Planilhas
- APIs
- Web Services

Laboratorio:
Leitura do OLTP da Minishop em modo read-only.

## Transform

Validar e padronizar dados.

Exemplos:
- Validar campos obrigatorios
- Padronizar nomes
- Converter datas
- Verificar quantidades e valores
- Aplicar regras de negocio
- Localizar chaves substitutas

## Load

Carregar dimensoes e fatos.

Neste laboratorio:
- Dimensao cliente
- Dimensao produto
- Dimensao tempo
- Fato vendas

O banco ETL e independente dos anteriores.

## Lookup de dimensao

Verifica se o codigo natural ja existe.

Se nao existe:
cria um novo membro e sua surrogate key.

Se existe e nao mudou:
reutiliza a surrogate key.

Se mudou um atributo acompanhado por SCD2:
cria uma nova versao da dimensao.

## Lookup de fato

Localiza chaves substitutas das dimensoes
antes de inserir o fato.

O fato guarda essas SKs como chaves
estrangeiras.

## Slowly Changing Dimension Tipo 2

Preserva versoes anteriores.

Exemplo:
Cliente 1 - Ana - versao 1 - inativa
Cliente 1 - Ana Atualizada - versao 2 - ativa

Cada versao possui uma SK diferente.

As vendas antigas continuam apontando
para a SK da versao anterior.

## Carga inicial

Primeira alimentacao do DW.

Carrega o historico disponivel na fonte.

## Carga incremental

Adiciona fatos ainda nao carregados.

No laboratorio, a extracao relê a fonte
completa e compara as chaves no destino.

Portanto, nao implementa CDC.

## Auditoria

A tabela etl_cargas registra:
- Tipo da carga
- Data e hora
- Linhas extraidas
- Novos fatos
- Novas versoes das dimensoes

## Transacoes

A carga utiliza BEGIN IMMEDIATE,
COMMIT e ROLLBACK.

Um erro no processamento desfaz as
alteracoes daquela carga.

## Limitacoes

Correcoes em fatos historicos exigem
politica de reprocessamento.

Alteracoes em dimensoes sao detectadas
pela comparacao com o estado atual.

SCD2 utiliza horario de carga, nao
a data efetiva da mudanca operacional.

Exclusoes, cancelamentos retroativos,
CDC e integracao com fontes externas
ainda nao foram implementados.

A seguranca de concorrencia e o tratamento
de falhas de plataformas corporativas
exigem recursos adicionais.

## Proxima etapa

Aprofundar os mecanismos de transformacao
e processamento ETL na proxima aula.
