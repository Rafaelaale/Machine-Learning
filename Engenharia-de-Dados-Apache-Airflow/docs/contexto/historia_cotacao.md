# História da Sprint — DAG de Cotação USD-BRL

**Sprint:** 2025-S03
**Story ID:** DATA-127
**Reporter:** Rafael Souza (Produto)
**Assignee:** Time de Dados
**Prioridade:** Média

---

## Título
Histórico diário de cotação USD-BRL para área financeira

## Descrição

Como **analista financeiro**,
quero **ter acesso ao histórico de cotação do dólar dos últimos 7 dias atualizado diariamente**,
para que eu possa **calcular o impacto cambial nas compras internacionais sem precisar buscar manualmente em sites de câmbio**.

## Contexto

A área financeira hoje consulta manualmente o site do Banco Central toda manhã para registrar a cotação do dólar do dia. Esse dado é usado para:

- Ajuste de preços de produtos importados
- Cálculo de custo de mercadorias compradas em dólar
- Relatório semanal de exposição cambial

O processo manual gera problemas:

- Esquecimento em dias atribulados
- Inconsistência no horário de captura (cotação varia ao longo do dia)
- Falta de histórico organizado

## Critérios de aceitação

- O sistema deve buscar a cotação USD-BRL automaticamente uma vez por dia
- A cotação bruta deve ser armazenada para auditoria futura
- Um arquivo consolidado deve conter sempre os últimos 7 dias de cotação
- O arquivo consolidado deve ter: data, cotação de abertura, máxima, mínima, fechamento
- Se a API estiver indisponível, o time deve ser notificado

## Fonte de dados sugerida

AwesomeAPI — `https://economia.awesomeapi.com.br/last/USD-BRL`

API pública, gratuita, sem necessidade de autenticação no plano básico.

## Não faz parte desta história

- Interface visual para consulta (a área usa o CSV direto)
- Histórico maior que 7 dias (pode ser feito em sprint futura)
- Alertas de variação cambial brusca (escopo da DATA-141)
