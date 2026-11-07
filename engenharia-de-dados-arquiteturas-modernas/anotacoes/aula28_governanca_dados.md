# Aula 28 - Governanca dos dados

## Objetivo

Organizar, documentar e controlar o uso
dos dados analiticos da Minishop.

A governanca e transversal a:
OLTP, Data Lake, Lakehouse, DW e consumo.

## Pilar 1 - Catalogo de dados

O catalogo e o inventario da plataforma.

No laboratorio documentamos:

- Tabelas do DW.
- Colunas e respectivos tipos.
- Chaves primarias.
- Chaves estrangeiras.
- Quantidade de registros.
- Tabelas Parquet da Gold.
- Metricas e dimensoes oficiais.
- Localizacao dos datasets.

O responsavel pelos datasets foi deixado
como nao definido. A aula nao fornece
uma pessoa ou equipe real responsavel.

## Pilar 2 - Linhagem

A linhagem documenta a origem,
as transformacoes e o destino.

Caminhos principais:

OLTP -> Bronze -> Silver -> Gold -> Lakehouse.
Silver -> ETL -> Data Warehouse.
Lakehouse e DW -> Camada semantica -> BI.

A linhagem do laboratorio e declarativa:
representa os fluxos implementados nas aulas.

Nao estamos usando ferramenta automatica
de descoberta ou captura de linhagem.

## Pilar 3 - Qualidade dos dados

Validacoes implementadas:

- Campos obrigatorios.
- Pedidos e produtos identificados.
- Duplicidades de pedido/produto.
- Quantidade positiva.
- Valores financeiros nao negativos.
- Datas validas.
- Integridade referencial SQLite.
- Conciliacao de indicadores Gold e DW.
- Consistencia das metricas semanticas.

## Politica de rejeicao

A funcao de validacao retorna erros,
sem gravar os registros incorretos.

Os testes injetam dados invalidos
somente em memoria.

Este laboratorio nao implementa
quarentena persistente de registros.

## Ferramentas citadas na transcricao

DataHub.
Amundsen.
Atlan.
Alation.

O laboratorio utiliza Python,
SQLite, DuckDB e manifestos existentes.

Nao instalamos ferramentas externas
de catalogacao.

## Resultado de negocio

A governanca melhora:

Descoberta dos dados.
Documentacao.
Rastreabilidade.
Confiabilidade.
Consistencia entre dashboards.

## Limitacoes

Nao implementa controle de permissao
por usuario ou classificacao de sigilo.

Nao implementa alertas automaticos
nem verificacoes agendadas.

Nao valida historico completo de todas
as versoes dos datasets; verifica
o snapshot selecionado.

## Proxima aula

Continuar os mecanismos de governanca
e produtividade da arquitetura moderna.
