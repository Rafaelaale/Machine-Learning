# Aula 05 - Tipos de linhagem de dados

## Objetivo

Compreender as diferencas entre a linhagem
por tabela e a linhagem por coluna.

## 1. Linhagem por tabela

Identifica quais tabelas alimentam outras tabelas
ou visoes.

No exemplo apresentado pela Alura:

- Precos de imoveis por metro quadrado.
- Informacoes de cartorios.
- Analises anteriores.

Essas tres fontes alimentam uma base de avaliacao.

## 2. Linhagem por coluna

Identifica quais colunas de origem contribuem
para cada coluna de destino.

Tambem documenta as transformacoes especificas.

## 3. Exemplo: variacao percentual

O laboratorio complementar calcula:

variacao_pct = (atual - anterior) / anterior * 100

A coluna depende de:

- transacoes_cartorio.negocios_mes_atual
- analises_anteriores.negocios_mes_anterior

Se o valor anterior for zero, o resultado sera nulo.

## 4. Diferencas entre os niveis

Linhagem por tabela:
- Menor detalhamento.
- Identifica fontes gerais.
- Mais simples de manter.

Linhagem por coluna:
- Maior detalhamento.
- Identifica dependencias especificas.
- Documenta transformacoes por campo.
- Exige maior esforco de manutencao.

## 5. Quando utilizar cada uma

Conforme a aula, nao existe regra fixa.

Bases mais importantes para o negocio podem
justificar linhagem com maior detalhamento.

## 6. Laboratorio pratico

Tecnologias utilizadas:

- Python
- SQLite
- SQL
- JSON
- CSV

Foram criados registros de linhagem por tabela
e por coluna, utilizando dados ficticios.

## 7. Principal aprendizado

A linhagem por tabela identifica as bases envolvidas.

A linhagem por coluna detalha a origem de cada campo
e as transformacoes aplicadas aos dados.

A escolha depende da importancia dos ativos
e das necessidades da organizacao.