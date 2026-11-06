# Aula 06 - Entendendo codigo limpo

## Curso

Engenharia de Software para Dados: principios basicos.

## Conceito de codigo limpo

Codigo limpo e compreensivel, organizado,
eficiente, com proposito e facil manutencao.

Facilita a colaboracao e a evolucao do projeto.

## PEP 8

Guia de estilo da linguagem Python.

Recomendacoes:

- Indentacao de quatro espacos por nivel.
- Nao misturar tabs e espacos.
- Linhas com ate 79 caracteres como referencia.
- Variaveis em snake_case.
- Funcoes em snake_case.
- Classes em PascalCase.
- Imports organizados no inicio dos arquivos.
- Comentarios e docstrings com proposito.

## Codigo ruim apresentado na aula

A funcao pp apresentava:

- Nome pouco informativo.
- Colunas A, B, C, D e E.
- Tratamentos misturados na mesma funcao.
- Ano 2025 fixo no codigo.
- Normalizacao sem tratar divisao por zero.
- Retorno de variavel nao definida.

Isso dificulta compreensao e manutencao.

## Funcoes melhoradas

### preencher_valores_ausentes

Trata quantidade ausente e categoria vazia.

### calcular_tempo_do_pedido

Calcula o tempo decorrido utilizando
ano_referencia como parametro.

### normalizar_valor_da_compra

Aplica normalizacao min-max ao valor de compra.

### preprocessar_pedidos

Orquestra as etapas anteriores.

O codigo passa a expressar as etapas
do processamento de forma clara.

## Docstrings

Descrevem a responsabilidade de uma funcao,
seus parametros e seu retorno.

## Type hints

Exemplo:

def calcular_tempo_do_pedido(
    df: pd.DataFrame,
    ano_referencia: int,
) -> pd.DataFrame:

Indicacoes de tipo ajudam a compreender
o contrato da funcao.

## Principio KISS

Keep It Simple, Stupid.

Evitar complexidade desnecessaria,
sem tornar o sistema fragil.

## Laboratorio complementar

Aplicamos o exemplo do curso a pedidos ficticios.

Criamos:

- Funcoes Python reutilizaveis.
- Tratamento de valores ausentes.
- Calculo da idade dos pedidos.
- Normalizacao min-max.
- Pipeline completo.
- Testes automatizados.
- Relatorios CSV e JSON.

## Cuidados adicionais

O DataFrame original e preservado.

Valores de compra constantes sao tratados
sem divisao por zero.

Em projetos reais de ML, a normalizacao
deve ser ajustada no conjunto de treino
e aplicada no teste, evitando vazamento
de informacoes entre os conjuntos.

## Principal aprendizado

Codigo limpo torna o software mais facil
de compreender, testar, reutilizar e manter.

A clareza deve ser priorizada em cada etapa
do desenvolvimento de projetos de dados.