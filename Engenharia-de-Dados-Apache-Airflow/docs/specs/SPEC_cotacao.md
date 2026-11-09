# SPEC — Pipeline de Cotação USD-BRL

**Origem:** `docs/contexto/historia_cotacao.md`
**Story ID:** DATA-127
**Status:** Aprovado
**Última atualização:** 2025-01-14

---

## Objetivo

Buscar diariamente a cotação USD-BRL e manter um arquivo consolidado com o histórico dos últimos 7 dias para uso da área financeira.

## Resultado esperado

Arquivo consolidado atualizado diariamente com a cotação dos últimos 7 dias.

---

## Inputs

| Item | Detalhe |
|---|---|
| Fonte | AwesomeAPI |
| Endpoint | `https://economia.awesomeapi.com.br/last/USD-BRL` |
| Autenticação | Não requer no plano básico |
| Formato de resposta | JSON |

## Outputs

| Item | Detalhe |
|---|---|
| Arquivo bruto | `cotacao_YYYY-MM-DD.json` em `data/cotacao/raw/` |
| Arquivo consolidado | `historico_7dias.csv` em `data/cotacao/consolidated/` |
| Colunas do consolidado | `data`, `abertura`, `maxima`, `minima`, `fechamento` |

---

## Fluxo de execução

```
[Buscar cotação na API]
        ↓
[Salvar JSON bruto]
        ↓
[Consolidar histórico dos últimos 7 dias]
```

## Tasks

### 1. buscar_cotacao
- Faz GET no endpoint da AwesomeAPI
- Valida que a resposta contém os campos esperados
- Retorna via XCom: caminho do arquivo JSON salvo

### 2. salvar_json_bruto
- Recebe via XCom o conteúdo da resposta
- Salva em `data/cotacao/raw/cotacao_YYYY-MM-DD.json`
- Retorna via XCom: caminho do arquivo salvo

### 3. consolidar_historico
- Lê os JSONs dos últimos 7 dias em `data/cotacao/raw/`
- Monta um CSV com as colunas: data, abertura, máxima, mínima, fechamento
- Sobrescreve `data/cotacao/consolidated/historico_7dias.csv`

---

## Agendamento

- Frequência: diária
- Horário de execução: 9h da manhã (após fechamento dos mercados do dia anterior)
- Cron: `0 9 * * *`
- Catchup: desativado

## Tratamento de falhas

| Cenário | Comportamento |
|---|---|
| API indisponível | Retry automático (3 tentativas, 5 min de intervalo) → notificação por e-mail se persistir |
| Resposta com campos faltando | Task falha com mensagem específica |
| Menos de 7 dias de histórico disponível | Consolida com os dias disponíveis, sem falhar |

## Notificações

- Destinatário: `dados@vendemais.com.br`
- Disparo: qualquer falha após esgotadas as tentativas de retry
- Conteúdo: nome da DAG, task que falhou, mensagem de erro, link para os logs

---

## Casos de borda considerados

- **API retorna cotação fora do horário comercial:** aceito normalmente
- **Reprocessamento no mesmo dia:** o JSON bruto e o consolidado são sobrescritos
- **Primeira execução (sem histórico):** consolida apenas com a cotação do dia

## Casos de borda fora do escopo desta versão

- Variação cambial brusca como alerta (DATA-141)
- Histórico maior que 7 dias
- Múltiplas moedas além de USD-BRL
