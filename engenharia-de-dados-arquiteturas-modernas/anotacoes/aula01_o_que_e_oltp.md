# Aula 01 - O que e OLTP?

## Definicao

OLTP significa Online Transaction Processing.

Sistemas OLTP registram operacoes do dia a dia:
- compras;
- pagamentos;
- alteracoes de estoque;
- cadastro de clientes;
- atualizacoes de dados.

## Caracteristicas fundamentais

### Alta concorrencia

O sistema precisa controlar transacoes de varios
usuarios sem comprometer a integridade dos dados.

### Baixa latencia

Operacoes pontuais devem responder rapidamente.

### Dados normalizados

Clientes, produtos, pedidos, itens, inventario e
pagamentos ficam em tabelas com responsabilidades
separadas.

### ACID

A - Atomicidade:
Tudo e confirmado ou tudo e desfeito.

C - Consistencia:
As restricoes do banco precisam ser respeitadas.

I - Isolamento:
Transacoes concorrentes nao devem produzir
resultados incorretos.

D - Durabilidade:
Alteracoes confirmadas permanecem persistidas.

## Exemplo da Minishop

1. Validar cliente.
2. Criar pedido.
3. Registrar itens.
4. Verificar e baixar estoque.
5. Registrar pagamento aprovado.
6. Confirmar pedido.

Se houver falha, executar rollback.

## OLTP versus OLAP

OLTP:
Registrar uma compra especifica.

OLAP:
Analisar o faturamento de milhares de compras
ao longo de um ano.

## Decisoes tecnicas do laboratorio

- SQLite para persistencia.
- Chaves primarias e estrangeiras.
- BEGIN IMMEDIATE para controlar escrita.
- CHECK para evitar estoque negativo.
- Valores monetarios em centavos.
- COMMIT ao concluir a compra.
- ROLLBACK se houver falha.
- Testes automatizados.

## Limites da demonstracao

O pagamento e simulado. Nao ha gateway real.

A concorrencia nao foi submetida a teste de carga.
SQLite possui caracteristicas de escrita diferentes
das de um SGBD corporativo.

Uma transacao que envolve servicos externos exige
cuidados adicionais, como idempotencia e conciliacao.

## Proxima aula

Entender sistemas analiticos e por que cargas OLAP
costumam ser separadas das operacoes OLTP.
