# Aula 24 - Exemplo das diferentes camadas

## Dados da aula

FAT001:
CLI10, R$ 1.000,00
Vencimento: 10/01/2026
Pagamento: 09/01/2026
Paga em dia.

FAT002:
CLI20, R$ 800,00
Vencimento: 15/01/2026
Sem pagamento.

FAT003:
CLI10, R$ 500,00
Vencimento: 20/01/2026
Pagamento: 28/01/2026
Paga com 8 dias de atraso.

Clientes:
CLI10: Mercado Alpha, Belo Horizonte/MG.
CLI20: Loja Beta, Campinas/SP.

Os dados sao exemplos didaticos, nao dados
operacionais reais da Minishop.

## OLTP

Banco SQLite com clientes e faturas.
Responsavel pelo registro transacional.

## Bronze

Faturas em Parquet real.
Clientes em JSON.
Dados preservados antes da classificacao.

## Silver

Join entre clientes e faturas.
Extracao de cidade e estado.
Status de pagamento.
Dias de atraso.
Saldo aberto.

## Gold

Faixas de aging.
Indicador de inadimplencia atual.
Indicador historico de pagamento atrasado.

Data de referencia: 31/01/2026.

FAT002 vence em 15/01 e possui 16 dias
de atraso em 31/01.

Na tabela didatica da transcricao,
ABERTO aparecia com atraso 0 e inadimplencia
False sem uma data de corte definida.

Neste laboratorio, usamos uma data de corte
explicita para calcular aging atual.

FAT003 foi paga com 8 dias de atraso.
Isso e historico de pagamento atrasado,
nao saldo atualmente inadimplente.

## Indicadores

Total emitido: R$ 2.300,00.
Total recebido: R$ 1.500,00.
Saldo aberto vencido: R$ 800,00.

Inadimplencia atual sobre valor emitido:
800 / 2300 = 34,78%.

Esse percentual e um indicador definido
para o exercicio, nao uma regra universal.

## Lakehouse

DuckDB consulta Parquet diretamente.
Catalogo JSON registra localizacoes.

Nao implementa Iceberg, Delta nem Hudi.

## Data Warehouse

Dimensoes:
Cliente.
Tempo.
Aging.

Fato:
Contas a receber.

Os dados do DW sao carregados a partir
da Gold, sem retornar ao OLTP.

## Proxima aula

Projetar o Lakehouse da Minishop
segundo a sequencia da Alura.
