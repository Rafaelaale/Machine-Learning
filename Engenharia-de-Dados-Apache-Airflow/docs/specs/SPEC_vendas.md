# SPEC — Pipeline de Vendas Diárias

**Origem:** `docs/contexto/email_vendas.md`
**Status:** Aprovado
**Última atualização:** 2025-01-14

---

## Objetivo

Automatizar a geração do relatório diário de vendas por categoria, eliminando o processo manual realizado pelo time de Operações Comerciais.

## Resultado esperado

Resumo diário disponível até as 8h da manhã com:
- Categoria
- Total de pedidos
- Valor total em reais
- Ticket médio

---

## Inputs

| Item | Detalhe |
|---|---|
| Arquivo de entrada | `vendas_YYYY-MM-DD.csv` |
| Localização | `data/input/` |
| Janela de chegada | Entre 5h e 7h30 da manhã |
| Colunas esperadas | `data`, `pedido_id`, `produto`, `categoria`, `quantidade`, `valor_unitario` |
| Encoding | UTF-8 |
| Separador | Vírgula |

## Outputs

| Item | Detalhe |
|---|---|
| Arquivo de saída | `resumo_categoria_YYYY-MM-DD.csv` |
| Localização | `data/output/` |
| Colunas | `categoria`, `total_pedidos`, `valor_total_brl`, `ticket_medio_brl` |
| Encoding | UTF-8 |

---

## Fluxo de execução

```
[FileSensor: aguardar arquivo] 
        ↓
[Extrair: ler CSV e validar estrutura]
        ↓
[Transformar: agrupar por categoria e calcular métricas]
        ↓
[Carregar: salvar CSV consolidado em data/output/]
```

## Tasks

### 1. aguardar_arquivo_vendas
- Tipo: FileSensor
- Aguarda o arquivo `vendas_YYYY-MM-DD.csv` aparecer em `data/input/`
- Timeout: 3 horas (das 5h às 8h)
- Poke interval: 60 segundos

### 2. extrair_vendas
- Lê o CSV e valida que as colunas esperadas estão presentes
- Valida que o arquivo não está vazio
- Retorna via XCom: caminho do arquivo lido e contagem de linhas

### 3. transformar_vendas
- Recebe via XCom o caminho do arquivo
- Agrupa por categoria
- Calcula: total de pedidos, valor total (quantidade × valor_unitario), ticket médio
- Retorna via XCom: caminho do arquivo transformado

### 4. carregar_resumo
- Recebe via XCom o caminho do arquivo transformado
- Salva o resumo em `data/output/resumo_categoria_YYYY-MM-DD.csv`
- Sobrescreve arquivo existente da mesma data

---

## Agendamento

- Frequência: diária
- Horário de execução: 5h da manhã
- Cron: `0 5 * * *`
- Catchup: desativado

## Tratamento de falhas

| Cenário | Comportamento |
|---|---|
| Arquivo não chega até 8h | FileSensor falha por timeout → notificação por e-mail |
| Arquivo corrompido ou vazio | Task de extração falha → notificação por e-mail |
| Colunas faltando no CSV | Task de extração falha com mensagem específica |
| Falha de rede ou disco | Retry automático (3 tentativas, 5 min de intervalo) |

## Notificações

- Destinatário: `dados@vendemais.com.br`
- Disparo: qualquer falha após esgotadas as tentativas de retry
- Conteúdo: nome da DAG, task que falhou, mensagem de erro, link para os logs

---

## Casos de borda considerados

- **Arquivo chega antes da DAG iniciar:** FileSensor detecta imediatamente e segue
- **Múltiplas execuções no mesmo dia (reprocessamento):** o arquivo de saída é sobrescrito
- **Categoria nova nunca vista:** aparece no resumo normalmente, sem tratamento especial
- **Quantidade ou valor negativo:** registrado como está (regra de negócio do time comercial)

## Casos de borda fora do escopo desta versão

- Validação de duplicidade de pedido_id
- Reconciliação com sistema de origem
- Geração de histórico consolidado de múltiplos dias
