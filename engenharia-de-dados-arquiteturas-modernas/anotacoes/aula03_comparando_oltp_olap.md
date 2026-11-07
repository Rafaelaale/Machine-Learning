# Aula 03 - Comparando OLTP e OLAP

## OLTP: sistema operacional

Responde a perguntas pontuais:

- Qual e o pedido de determinado cliente?
- O pagamento foi aprovado?
- Qual e o estoque de um produto?

Caracteristicas:

- Muitas operacoes pequenas.
- Insercoes, atualizacoes e validacoes.
- Baixa latencia.
- Integridade transacional.
- Modelagem normalmente normalizada.

## OLAP: sistema analitico

Responde a perguntas agregadas:

- Quanto a empresa faturou?
- Qual foi o ticket medio?
- Quais produtos venderam mais?
- Como as vendas evoluiram no tempo?

Caracteristicas:

- Consultas complexas.
- Grandes volumes historicos.
- Agregacoes e agrupamentos.
- Predominio de leituras.
- Modelagem multidimensional.

## Usuarios

OLTP:
Clientes, operadores e sistemas operacionais.

OLAP:
Analistas, gestores e cientistas de dados.

## Caso Minishop

OLTP:
clientes, produtos, inventario,
pedidos, itens_pedido e pagamentos.

OLAP:
fato_vendas, dim_clientes,
dim_produtos e dim_tempo.

## Reconciliacao

Os valores agregados da origem devem
ser comparados com a carga analitica.

Uma nova venda no OLTP nao aparece
automaticamente na fotografia OLAP.

E necessario executar nova carga.

## Limites da demonstracao

A medicao de tempo de duas consultas locais
nao demonstra superioridade de desempenho
de nenhuma arquitetura.

O banco do exemplo e pequeno.

Nao ha informacoes suficientes para analisar
faturamento por categoria, lucro ou regiao.

## Proximo assunto

Projetar formalmente a camada OLTP
da empresa Minishop.
