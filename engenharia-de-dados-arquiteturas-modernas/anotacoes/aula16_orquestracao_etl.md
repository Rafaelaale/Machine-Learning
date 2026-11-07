# Aula 16 - Continuando a criacao do ETL do Minishop

## Parametros globais

Data_Inicial
Data_Final

Todas as consultas de fatos respeitam esse intervalo.

Tambem existe uma funcao para calcular
os ultimos 30 dias, incluindo a data de referencia.

## Abordagem

Python + SQLite, com um orquestrador unico.

Ordem:
1. Extrair fonte
2. Validar dados
3. Iniciar transacao no DW
4. Carregar dimensoes
5. Resolver surrogate keys
6. Apagar fatos do periodo
7. Recarregar fatos do periodo
8. Registrar auditoria
9. Confirmar transacao

Em caso de falha:
ROLLBACK.

## Dimensao Produto

Produto e Categoria sao extraidos por JOIN.

Categoria e carregada antes do Produto.

Ambos usam SCD Tipo 1.

## Dimensao Cliente

SCD Tipo 2.

Lookup de fatos considera:
codigo natural + data da venda.

O OLTP existente nao possui endereco,
cidade, estado nem nascimento.

Nao criar versoes historicas geograficas
sem fonte e data efetiva confiaveis.

## Dimensao Acesso

A transcricao propoe DISTINCT(canal_venda).

O OLTP implementado nao possui essa coluna.

A dimensao permanece sem registros.

## Dimensao Promocao

Dois valores constantes:
TRUE e FALSE.

Nao classificar pedidos sem coluna de promocao.

## Dimensao Aging

Faixas:
0-15 dias
16-30 dias
31-60 dias
61+ dias

Situacoes:
a_vencer
vencido

## Dimensao Tempo

Todos os dias de Data_Inicial a Data_Final.

Surrogate Key deterministica: AAAAMMDD.

O laboratorio nao inventa feriados locais.

## Fato Vendas

Grao:
um produto de um pedido.

Origem:
pedidos + itens + pagamentos.

Somente vendas confirmadas e pagas.

Lookups:
cliente SCD2
produto SCD1
tempo SCD1

Promocao e Acesso ficam NULL
porque nao existem na origem.

## Fato Inventario

Origem:
movimentos_estoque associados aos pedidos.

O OLTP didatico nao armazena data especifica
do movimento. Usamos a data do pedido.

Isso e uma aproximacao e deve ser corrigido
se o modelo operacional ganhar essa coluna.

## Fato Financeiro

Estrutura preparada.

Nao carregar valores ficticios.

Necessita:
data de vencimento
saldo em aberto
situacao de cobranca
data de referencia da analise

Sem essas informacoes, a tabela permanece vazia.

## Politica de carga

Reprocessamento por periodo completo.

Os dados de vendas e inventario do periodo
sao apagados e inseridos novamente.

Permite:
inclusoes
alteracoes
exclusoes

A fonte precisa entregar uma fotografia completa
para o intervalo informado.

## Auditoria

etl_execucoes registra:
datas do intervalo
momento da execucao
quantidade de vendas
quantidade de movimentos
faturamento carregado

## Agendamento

A transcricao sugere 01:00 diariamente.

Este laboratorio nao cria uma tarefa agendada.

Primeiro validamos o ETL.
Depois podemos configurar o Agendador
de Tarefas do Windows separadamente.

## Proxima aula

Introducao ao Data Lake.
