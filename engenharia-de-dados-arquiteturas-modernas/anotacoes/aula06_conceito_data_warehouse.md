# Aula 06 - Conceito de Data Warehouse

## Definicao

Um Data Warehouse e um ambiente orientado
a analise estrategica e historica de dados.

A definicao classica apresentada por
Bill Inmon possui quatro caracteristicas.

## 1. Orientado por temas

Organiza informacoes por assuntos
como vendas, clientes ou produtos.

## 2. Integrado

Consolida informacoes de diferentes
sistemas em uma visao consistente.

Nosso laboratorio ainda possui somente
uma fonte: o OLTP da Aula 05.

A integracao real com fontes adicionais
sera estudada posteriormente.

## 3. Nao volatil

O Data Warehouse preserva informacoes
historicas para consulta.

No laboratorio, cada lote registra
uma fotografia das vendas.

A carga de um novo lote nao apaga
as fotografias anteriores.

Isso nao significa que todo DW real
proiba correcoes, retificacoes ou expurgos.

## 4. Variavel no tempo

Os dados sao organizados para permitir
comparacoes entre periodos.

A dimensao tempo registra:
data, ano, mes e dia.

## Modelo dimensional

Tabela de fatos:
fato_vendas

Dimensoes:
dim_clientes
dim_produtos
dim_tempo

Grao:
Uma linha por produto de um pedido
confirmado e pago, para cada lote.

## Indicadores

Faturamento total.
Ticket medio.
Unidades vendidas.
Faturamento por categoria.
Faturamento mensal.

## Historico de cargas

A tabela lotes_carga registra
as fotografias disponiveis.

Consultas comuns usam o lote mais recente.

Consultas historicas podem selecionar
um lote anterior.

A assinatura dos dados evita criar
outro lote se o conteudo nao mudou.

## Limites

Este e um prototipo em SQLite.

Nao implementa ainda uma plataforma
corporativa de Data Warehouse.

Uma fotografia historica de carga nao
substitui o historico de todas as
mudancas operacionais entre cargas.

Nao existem dados suficientes para
analisar tres anos de faturamento.

Nao ha integracao real com gateway
de pagamento, marketing ou planilhas.

## Proxima aula

Arquitetura interna do Data Warehouse
e organizacao em camadas.
