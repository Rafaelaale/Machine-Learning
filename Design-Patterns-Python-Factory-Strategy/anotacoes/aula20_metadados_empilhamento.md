# Aula 20 - Preservando metadados e empilhando decoradores

## 1. Objetivo

Estudar a preservacao de metadados e
a combinacao de varios decoradores.

## 2. Problema dos metadados

Sem functools.wraps:

```python
def adicionar_log(func):
    def wrapper(a, b):
        return func(a, b)
    return wrapper
```

Ao decorar uma funcao chamada somar,
somar.__name__ passa a ser wrapper.

Isso ocorre porque a variavel somar
passa a referenciar a funcao wrapper.

## 3. Solucao: functools.wraps

```python
import functools

def adicionar_log(func):
    @functools.wraps(func)
    def wrapper(a, b):
        resultado = func(a, b)
        print(
            f"Executando {func.__name__}"
            f"({a}, {b}) = {resultado}"
        )
        return resultado

    return wrapper
```

wraps preserva varios metadados,
como __name__, __doc__ e __wrapped__.

## 4. Aplicacao do decorator

```python
@adicionar_log
def somar(a, b):
    return a + b
```

Agora:

somar.__name__ retorna "somar".

## 5. Empilhamento de decoradores

```python
@repetir(3)
@adicionar_log
def somar(a, b):
    return a + b
```

A aplicacao ocorre de baixo para cima.

Primeiro:
adicionar_log(somar)

Depois:
repetir(3)(resultado_anterior)

## 6. Execucao

Ao chamar somar(2, 3):

[1]: Executando somar(2, 3) = 5
[2]: Executando somar(2, 3) = 5
[3]: Executando somar(2, 3) = 5

## 7. Ordem importa

Se invertermos os decoradores:

```python
@adicionar_log
@repetir(3)
def somar(a, b):
    return a + b
```

O decorator de log envolve o de repeticao.

Nesse caso, repetimos a funcao tres vezes,
mas registramos apenas um log externo.

## 8. Comportamento do retorno

Na implementacao da transcricao,
repetir(vezes) nao retorna o valor
produzido pela funcao original.

Por isso a funcao empilhada retorna None.

## 9. Nem todos os metadados ficam preservados

Nesta aula, adicionar_log utiliza
functools.wraps.

Mas repetir ainda nao utiliza wraps.

Portanto, o decorator externo pode
substituir novamente o nome da funcao
por "wrapper".

## 10. Proxima aula

A transcricao anuncia decoradores
implementados com classes.

Nao antecipamos essa implementacao.

## 11. Arquivos

src/aula20_metadados_empilhamento.py
aulas/aula20_metadados_empilhamento.py
tests/test_aula20_metadados_empilhamento.py
anotacoes/aula20_metadados_empilhamento.md
resultados/aula20_metadados_empilhamento.json

## 12. Testes

16 testes novos.
Meta acumulada: 320.
