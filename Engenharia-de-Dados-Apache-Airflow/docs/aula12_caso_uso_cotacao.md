# Aula 12 — Caso de uso da cotacao USD/BRL

## Objetivo

Consultar diariamente a cotacao do dolar em reais e manter
um historico consolidado dos ultimos sete dias.

## Fonte

AwesomeAPI
Metodo: GET
Formato: JSON
Autenticacao: nao exigida no exemplo da aula.

## Fluxo

1. Buscar cotacao na API.
2. Salvar JSON bruto.
3. Consolidar historico dos ultimos sete dias.

## Helper existente

Arquivo: helpers/cotacao.py

Funcoes apresentadas:
- buscar_cotacao(url)
- salvar_json_bruto(cotacao, pasta_destino)
- consolidar_historico(pasta_raw, caminho_consolidado)

## Validacoes

O JSON deve conter USDBRL.

Campos obrigatorios:
- bid
- ask
- high
- low
- create_date

Ausencia de campos deve produzir erro explicito.

## Saidas

Arquivo bruto:
cotacao_YYYY-MM-DD.json

Arquivo consolidado:
CSV com as colunas:
- data
- abertura
- maxima
- minima
- fechamento

Historico: ultimos 7 dias.

Na primeira execucao, consolidar somente os dados disponiveis.

## Agendamento previsto

Diariamente, as 09:00.

O fuso horario ainda precisa ser definido na implementacao.

## Tratamento de falhas

- 3 retries
- Intervalo de 5 minutos
- Notificacao por e-mail em etapa futura

## Escopo desta aula

Compreender a especificacao e o helper existente.

A DAG sera construida na proxima aula.
XCom sera abordado posteriormente.

## Observacao tecnica

O helper apresentado utiliza datetime.now() para nomear arquivos
e selecionar os ultimos sete dias.

Na implementacao da DAG, verificar como isso se relaciona
com a data logica das execucoes e o fuso horario.
