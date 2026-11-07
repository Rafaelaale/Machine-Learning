# Aula 22 - Implementando decoradores com classes

## Objetivo

Implementar decoradores usando classes
e o metodo especial __call__.

## 1. Objetos callable

Um objeto que implementa __call__
pode ser invocado como uma funcao.

Exemplo:

```python
class ComLog:
    def __init__(self, func):
        self.func = func

    def __call__(self, a, b):
        print(f"Executando {self.func.__name__} ({a}, {b})")
        resultado = self.func(a, b)
        print(f"Resultado: {resultado}")
        return resultado
```

## 2. Aplicando ComLog

```python
@ComLog
def somar(a, b):
    return a + b
```

Isso equivale a:

somar = ComLog(somar)

Depois da decoracao, somar
referencia uma instancia de ComLog.

O operador somar(3, 5) chama __call__.

## 3. Decoradores parametrizados

```python
class Repetir:
    def __init__(self, vezes):
        self.vezes = vezes

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            for i in range(self.vezes):
                print(f"[{i + 1}]", end=" ")
                func(*args, **kwargs)

        return wrapper
```

## 4. Utilizacao de Repetir

```python
@Repetir(5)
def imprime():
    print("Executando função...")
```

Aqui, Repetir(5) cria a instancia.

O objeto recebe a funcao em __call__
e devolve a funcao wrapper.

## 5. Diferenca entre as duas classes

ComLog:
- Recebe func no __init__.
- __call__ recebe os argumentos da funcao.
- A funcao decorada referencia uma instancia.
- Preserva o resultado da funcao original.

Repetir:
- Recebe vezes no __init__.
- __call__ recebe a funcao a decorar.
- Retorna um wrapper.
- Nao retorna os resultados das repeticoes.

## 6. args e kwargs

*args encaminha argumentos posicionais.

**kwargs encaminha argumentos nomeados.

Isso permite usar Repetir com funcoes
que recebem assinaturas diferentes.

## 7. Metadados

Nesta transcricao, ComLog e Repetir
nao utilizam functools.wraps.

Nao acrescentamos essa melhoria,
pois os exemplos seguem a aula.

## 8. Relacao com aulas anteriores

Aula 17:
Decorator utilizando funcoes.

Aula 19:
Decorator parametrizado usando closures.

Aula 20:
Preservacao de metadados e empilhamento.

Aula 21:
Aplicacao de decorators a classes.

Aula 22:
Implementacao de decorators como classes.

## 9. Arquivos criados

src/aula22_decoradores_com_classes.py
aulas/aula22_decoradores_com_classes.py
tests/test_aula22_decoradores_com_classes.py
anotacoes/aula22_decoradores_com_classes.md
resultados/aula22_decoradores_com_classes.json

## 10. Testes

16 novos testes.
Meta acumulada: 352.
