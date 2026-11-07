# Aula 26 - Aproveitando funcoes de primeira classe e lambdas

## Objetivo

Implementar o padrao Strategy utilizando
funcoes tradicionais e expressoes lambda.

A Aula 25 usava classes abstratas e classes
concretas. A Aula 26 utiliza callables.

## 1. Funcoes de primeira classe

Em Python, funcoes podem:
- ser passadas como argumentos;
- ser armazenadas em variaveis;
- ser guardadas em listas e dicionarios;
- ser retornadas por outras funcoes;
- ser substituidas em tempo de execucao.

## 2. Estrategias tradicionais

```python
def desconto_vip(total):
    return total * 0.8

def desconto_novo(total):
    return total * 0.9

def desconto_funcionario(total):
    return total * 0.7

def sem_desconto(total):
    return total
```

## 3. Contexto Strategy

```python
def calcular_preco(total, estrategia):
    return estrategia(total)
```

A funcao calcular_preco nao precisa
conhecer os detalhes do desconto.

## 4. Expressoes lambda

```python
soma = lambda a, b: a + b

desconto_estudante = lambda total: total * 0.85

black_friday = (
    lambda total: total * 0.5
    if total <= 500
    else total * 0.9
)

parceria_empresa_x = lambda total: total * 0.85 - 10
parceria_empresa_y = lambda total: total * 0.85 - 5
```

Essas lambdas sao exemplos da transcricao.

Para funcoes nomeadas, em geral prefere-se
def em vez de atribuir lambda a variaveis.

## 5. Lambda diretamente como argumento

```python
print(
    calcular_preco(
        300,
        lambda total: total * 0.75,
    )
)
```

Resultado: 225.

## 6. Divergencia na transcricao

A formula literal para Black Friday:

total * 0.5 if total <= 500 else total * 0.9

Para total igual a 600, o resultado e 540.

A transcricao informa 270, mas esse
resultado nao corresponde a formula escrita.

Na Aula 24, a formula para total > 500
aplicava dois descontos sucessivos:

600 * 0.5 * 0.9 = 270.

Nesta Aula 26, a formula original foi
preservada sem correcao silenciosa.

## 7. Resultados segundo as formulas

VIP, 200: 160.
Novo, 200: 180.
Funcionario, 200: 140.
Sem desconto, 200: 200.
Estudante, 200: 170.
Black Friday, 600: 540.
Empresa X, 200: 160.
Empresa Y, 200: 165.
Lambda direta, 300: 225.

## 8. Colecoes de estrategias

Funcoes podem ser armazenadas em
listas ou dicionarios.

O exemplo ESTRATEGIAS demonstra
selecao por chave, sem precisar
criar classes concretas.

## 9. Closure como fabrica de estrategia

criar_estrategia_percentual(fator)
retorna uma funcao que conserva
o fator recebido.

Esse e um exemplo complementar
de funcao retornando outra funcao.

## 10. Relacao com aulas anteriores

Aula 24: regras em if/elif/else.
Aula 25: Strategy com classes.
Aula 26: Strategy com funcoes.

## 11. Proxima aula

A transcricao apresenta um proximo
cenario com algoritmo comum e
apenas algumas etapas variaveis.

Nao implementamos Template Method aqui.

## 12. Arquivos

src/aula26_funcoes_lambdas.py
aulas/aula26_funcoes_lambdas.py
tests/test_aula26_funcoes_lambdas.py
anotacoes/aula26_funcoes_lambdas.md
resultados/aula26_funcoes_lambdas.json

## 13. Testes

16 testes novos.
Meta acumulada: 416.
