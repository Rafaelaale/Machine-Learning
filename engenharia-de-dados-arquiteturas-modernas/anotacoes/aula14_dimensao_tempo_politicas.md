# Aula 14 - Dimensao Tempo e politicas de carga

## Dimensao Tempo

Cada dia possui chave numerica AAAAMMDD.

Exemplo:
2025-02-01 -> 20250201

A chave e deterministica e inteira.

A dimensao fornece:
- Dia
- Mes
- Ano
- Trimestre
- Semestre
- Dia da semana
- Indicador de fim de semana

Feriados nao sao inferidos sem calendario
regional confiavel.

## Politica de preenchimento

Tres abordagens discutidas:

1. Gerar intervalo muito amplo.
2. Gerar somente dias com fatos.
3. Gerar intervalo continuo entre os limites.

Implementada:
Terceira abordagem.

Dias sem movimento aparecem nos relatorios
com valor zero.

## Politicas de fatos

Alternativas:

1. Incremental por chave natural.
2. Incremental pela combinacao das SKs.
3. Reprocessamento de periodo completo.

Implementada:
Terceira abordagem.

## Reprocessamento

Selecionar periodo.

Receber fotografia integral do periodo.

Validar dados e chaves.

Iniciar transacao.

Remover fatos anteriores daquele periodo.

Recarregar todos os fatos recebidos.

Sincronizar a dimensao Tempo.

Confirmar a transacao.

Em caso de erro, executar rollback.

## Exemplo didatico

Fevereiro anterior:
FEV-1 = R$ 10
FEV-2 = R$ 8

Fevereiro reprocessado:
FEV-1 = R$ 15
FEV-3 = R$ 14

FEV-2 foi removido.

Novo total:
R$ 29.

Janeiro permanece inalterado.

## Restricao obrigatoria

A entrada precisa ser um snapshot completo.

Passar somente as linhas alteradas
e apagar todo o mes provocaria perda de dados.

Um snapshot vazio, quando autenticamente
completo, representa zero movimentos no mes.

## Integridade

O processo protege:
- IDs duplicados
- Clientes inexistentes
- Valores invalidos
- Datas fora do periodo
- Reutilizacao de IDs entre meses
- Falhas no meio da transacao

## OLTP da Minishop

O laboratorio tambem permite extrair
vendas pagas e confirmadas da Aula 05.

A fonte e aberta em modo somente leitura.

O DW didatico fica separado do DW que
recebe os dados reais do laboratorio.

## Limites

O exemplo nao implementa captura CDC.

O reprocessamento requer que a extracao
seja consistente e realmente completa.

Mudancas de versao SCD2 precisam de lookup
pela data do evento, visto na Aula 13.

Indicadores financeiros ainda precisam
de dados de vencimento e saldo em aberto.

## Proxima etapa

Projeto do ETL da Minishop e suas cargas.
