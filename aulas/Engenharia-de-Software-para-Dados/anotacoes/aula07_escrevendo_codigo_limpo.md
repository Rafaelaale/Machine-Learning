# Aula 07 - Escrevendo codigo limpo

## Contexto da Alura

Revisar o modelo de churn de um e-commerce
cuja qualidade das previsoes comecou a cair.

## Material original

Pasta Churn-antes do projeto oficial da Alura.

Arquivo de dados identificado:
dados_corretos2.csv

Notebook legado:
Versao V1 final de retreinamento.

## Problemas encontrados no codigo original

- Importacoes distribuidas pelo notebook.
- Nomes genericos como df, m e p.
- Uma funcao com responsabilidades excessivas.
- Ausencia de documentacao adequada.
- Selecao de atributos por posicao.
- Divisao treino e teste sem semente explicita.
- Dificuldade de manutencao.

## Ferramentas da aula

Pycodestyle:
Verifica convencoes do PEP 8.

Flake8:
Verifica estilo e alguns problemas no codigo.

No Google Colab, a Alura utiliza uma extensao
para executar a verificacao nas celulas.

No VS Code, utilizamos o terminal PowerShell.

## Melhorias implementadas

- carregar_clientes
- preparar_dados
- separar_treino_teste
- treinar_regressao_logistica
- avaliar_modelo
- executar_pipeline

Cada funcao possui uma responsabilidade clara.

## Atributos do modelo

- total_spent
- num_orders
- days_since_last_purchase

Alvo:
churn

## Cuidados com treinamento

A separacao de dados utiliza random_state
para permitir a reproducibilidade.

A estratificacao conserva aproximadamente
a proporcao das classes.

Os resultados precisam ser avaliados antes
de qualquer decisao de producao.

## Codigo limpo e KISS

O objetivo e facilitar leitura, colaboracao,
testes e manutencao do codigo.

Codigo limpo nao significa apenas passar
em verificadores automaticos de estilo.

## Arquivos preservados

O dataset original da Alura nao e modificado.

Os arquivos das Aulas 01 a 06 sao mantidos.