# Aula 02 - Principios da Engenharia de Software: 1 ao 3

## Referencia apresentada pela Alura

Livro: Engenharia de Software: Uma Abordagem Profissional

Autores citados no curso:
Roger Pressman e Bruce Maxine.

A aula atribui os sete principios fundamentais
a David Hooker.

Nesta aula sao estudados os tres primeiros.

## 1. Razao de existir

Toda solucao deve ter um proposito.

Perguntas importantes:

- Por que estamos desenvolvendo este sistema?
- Qual problema ele resolve?
- Que valor entrega ao usuario?
- Que beneficio entrega a organizacao?
- Uma nova funcionalidade realmente ajuda?

### Exemplo: churn

Uma empresa de e-commerce deseja identificar
clientes com risco de abandono para apoiar
estrategias de retencao.

Precisamos entender o objetivo antes de
escolher modelos, parametros ou variaveis.

## 2. KISS - Keep It Simple, Stupid

Manter a solucao simples sem perder robustez.

Boas praticas:

- Evitar duplicacao de codigo.
- Criar funcoes reutilizaveis.
- Centralizar a leitura de dados.
- Evitar varios notebooks desorganizados.
- Diminuir complexidade desnecessaria.
- Facilitar testes e manutencao.

Simplificar nao significa eliminar validacoes.

## 3. Manter a visao

Preservar o conceito e a arquitetura do projeto.

Antes de alterar um sistema, entender:

- Quais dados sao utilizados?
- Qual e a origem desses dados?
- Como os dados sao tratados?
- Quais sao as transformacoes?
- Quando os processos executam?
- Qual problema de negocio e resolvido?

Novas funcionalidades devem respeitar
os objetivos e a arquitetura do sistema.

## Laboratorio complementar

Construimos uma analise ficticia de clientes.

Arquitetura:

- dados: arquivo CSV de clientes.
- src: funcoes reutilizaveis.
- aulas: programa principal.
- tests: testes automatizados.
- resultados: relatorio JSON.

A classificacao foi criada com regras simples,
para demonstrar os principios de engenharia.

Ela nao equivale a um modelo preditivo
de churn e nao utiliza dados reais.

## Aprendizados principais

1. Desenvolver sistemas com proposito.
2. Evitar complexidade desnecessaria.
3. Preservar a visao e a arquitetura.

## Proxima aula

Continuar os principios apresentados
no curso da Alura.

Nao utilizar Git ou GitHub durante as aulas.