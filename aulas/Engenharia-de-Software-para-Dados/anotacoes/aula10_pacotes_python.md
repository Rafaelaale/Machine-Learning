# Aula 10 - Convertendo notebooks em pacotes Python

## Objetivo

Transformar codigo experimental de notebooks em
um pacote Python instalavel e reutilizavel.

## Paradigmas

Programacao Orientada a Objetos:
classe PreProcessamento, atributos e metodos.

Programacao Funcional:
etapas pequenas, previsiveis e testaveis.

## Estrutura

src/tratamentos/setup.py

src/tratamentos/pre_processamento/__init__.py

src/tratamentos/pre_processamento/core.py

## Instalacao editavel

python -m pip install -e CAMINHO_DO_PACOTE

A opcao -e permite alterar o codigo local
sem reinstalar a cada mudanca.

## Metodos

- carregar_dados
- tratar_datas
- preencher_nulos
- codificar_churn
- criar_colunas_derivadas
- codificar_categoricas
- salvar_dados
- executar_pipeline

## Novas colunas

fidelidade = num_orders / (days_since_last_purchase + 1)

score_gasto = total_spent * num_orders

## Tratamento da variavel alvo

yes ou sim = 1
no ou nao = 0
desconhecido = ausente

Nao devemos transformar um rotulo desconhecido
em zero sem justificativa.

## Cuidados para producao

- Validar fontes e tipos de dados.
- Ajustar imputacao apenas nos dados de treino.
- Reutilizar mapeamentos de categorias.
- Verificar se ha vazamento de dados.
- Registrar parametros e transformacoes.
- Versionar artefatos e esquemas em ambiente adequado.

## Testes

A aula inclui testes de:
- leitura e esquema;
- datas invalidas;
- valores ausentes;
- codificacao de churn;
- colunas derivadas;
- valores negativos;
- one-hot encoding;
- reproducibilidade;
- integridade da fonte.

## Aprendizado principal

Um notebook experimental pode se transformar
em um componente Python que outros sistemas
conseguem importar, executar e testar.
