# Aula 17 - Entendendo o que sao decoradores

## Objetivo

Adicionar funcionalidades a funcoes
sem modificar suas implementacoes originais.

## Funcoes originais

```python
def somar(a, b):
    return a + b

def dividir(a, b):
    return a / b
```

## Problema

Para adicionar logs manualmente, precisamos
repetir codigo em varias funcoes.

## Solucao: Decorator

```python
def adicionar_log(func):
    def wrapper(a, b):
        resultado = func(a, b)
        print(
            f"Executando {func.__name__}"
            f"({a}, {b}) = {resultado}"
        )
        return resultado

    return wrapper
```

## Utilizacao

```python
soma_com_log2 = adicionar_log(somar)
dividir_com_log2 = adicionar_log(dividir)

soma_com_log2(3, 5)
dividir_com_log2(10, 2)
```

## Conceitos

- Funcoes sao objetos de primeira classe.
- Uma funcao pode receber outra funcao.
- Uma funcao pode retornar outra funcao.
- Wrapper adiciona comportamento.
- Closure preserva acesso a func.
- As funcoes originais continuam inalteradas.

## Limites desta aula

O wrapper recebe apenas dois argumentos.

Ainda nao utilizamos:
- @decorator;
- functools.wraps;
- *args e **kwargs.

A sintaxe avancada sera estudada depois.

## Arquivos

- src/aula17_entendendo_decoradores.py
- aulas/aula17_entendendo_decoradores.py
- tests/test_aula17_entendendo_decoradores.py
- anotacoes/aula17_entendendo_decoradores.md
- resultados/aula17_entendendo_decoradores.json

## Testes

16 novos testes.
Meta acumulada: 272.
