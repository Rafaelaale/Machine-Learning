# Aula 27 - Consumo analitico pela camada semantica

## Problema central

Dois analistas podem chamar indicadores diferentes
pelo mesmo nome: "faturamento".

Comercial:
Valor dos pedidos ou vendas.

Financeiro:
Valor efetivamente recebido.

Ambos podem estar corretos em seus contextos,
mas essas duas grandezas nao sao equivalentes.

## Solucao

Centralizar:
- Nome do indicador.
- Definicao do negocio.
- Fonte autorizada.
- Regra de calculo.
- Unidade de medida.
- Dimensoes permitidas.

## Minishop

A metrica oficial de faturamento permanece
a mesma definida na Aula 26:

Soma dos valores das vendas.

Fontes possiveis:
- Lakehouse
- Data Warehouse

Os consumidores nao precisam escrever SQL.

## Demonstracao financeira independente

Usa exclusivamente os dados didaticos
de contas a receber da Aula 24.

Valor das faturas emitidas:
R$ 2.300,00.

Valor recebido:
R$ 1.500,00.

Saldo aberto:
R$ 800,00.

Esses valores NAO representam os
recebimentos reais do e-commerce Minishop.

## Beneficio da camada semantica

A area comercial solicita:
minishop.faturamento

A area financeira solicita:
minishop.faturamento

Ambas recebem a mesma definicao oficial,
mesmo utilizando fontes fisicas diferentes.

Quando desejam analisar caixa,
devem solicitar explicitamente uma
metrica de recebimentos disponivel
no dominio financeiro apropriado.

## Ferramentas citadas na transcricao

Power BI.
Cube.
PostgreSQL.

Este laboratorio nao instala Power BI
nem Cube; demonstra o conceito por Python,
SQLite e DuckDB.

## Auditoria

20 comparacoes da Aula 26 entre DW e Lakehouse.
Consistencia entre comercial e financeiro.
Conciliacao das contas a receber didaticas.

## Limitacoes

Nao ha endpoint externo de BI.
Nao ha autenticacao nem permissao por usuario.
Nao ha dados operacionais suficientes para
afirmar o caixa real da Minishop.

## Proxima aula

Governanca:
Catalogo, linhagem e qualidade dos dados.
