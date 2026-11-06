# Dicionario de dados

## Origem

Repositorio de materiais da Alura:
alura-cursos/projeto-CHURN

Arquivo de trabalho:
data/raw/dados_corretos2.csv

Amostra analisada nas aulas: 10.000 registros.

## Variaveis utilizadas nas aulas

| Campo | Interpretacao didatica |
|---|---|
| customer_id | Identificador do cliente |
| signup_date | Data de cadastro |
| last_purchase_date | Data da ultima compra |
| product_category | Categoria do produto |
| total_spent | Total gasto |
| num_orders | Quantidade de pedidos |
| cancel_date | Data de cancelamento |
| data_ingestion | Data de ingestao |
| city | Cidade |
| payment_method | Meio de pagamento |
| product_id | Identificador do produto |
| churn | Rotulo de abandono |
| days_since_last_purchase | Dias desde a ultima compra |

As regras completas de origem, unidades e semantica
devem ser confirmadas com os responsaveis pelos dados.

## Transformacoes da Aula 10

- Datas convertidas com pandas.to_datetime.
- Cidade ausente preenchida como Desconhecido.
- Pagamento ausente preenchido como outro.
- Categoria ausente preenchida como outro.
- Dias ausentes preenchidos pela mediana disponivel.
- Churn conhecido convertido para 0 ou 1.
- Rotulos desconhecidos de churn preservados como ausentes.
- Categorias convertidas em colunas indicadoras.

## Atributos derivados

fidelidade = num_orders / (days_since_last_purchase + 1)

score_gasto = total_spent * num_orders

Esses atributos sao exemplos didaticos e precisam
de avaliacao de significado e utilidade preditiva.

## Cuidados

Nao assumir que valores ausentes significam zero.

Ajustar transformacoes usando somente dados de treino
quando houver treinamento e avaliacao de modelo.

Nao tratar colunas criadas por one-hot encoding como
estaveis entre bases sem um esquema definido.
