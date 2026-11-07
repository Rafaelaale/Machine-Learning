# Aula 19 - Decoradores com parametros, closures e nonlocal

## 1. Objetivo

Aprender a criar decoradores parametrizados,
compreender closures e utilizar nonlocal.

## 2. Fabrica de decoradores

A funcao repetir(vezes) retorna
um decorator.

O decorator recebe a funcao original,
cria um wrapper e retorna esse wrapper.

```python
def repetir(vezes):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for i in range(vezes):
                print(f"[{i + 1}]: ", end="")
                func(*args, **kwargs)

        return wrapper

    return decorator
```

## 3. Acucar sintatico

```python
@repetir(5)
def imprime():
    print("Executando função...")
```

A expressao @repetir(5) cria o decorator
que sera aplicado a imprime.

## 4. Aplicacao manual

```python
def diz_ola():
    print("Olá!")

decorador = repetir(3)
diz_ola = decorador(diz_ola)
diz_ola()
```

A mesma fabrica de decoradores pode
ser reutilizada em varias funcoes.

## 5. Closure

Uma closure permite que uma funcao
interna continue acessando variaveis
do seu escopo externo.

Em repetir, o wrapper lembra do
valor de vezes mesmo depois que
repetir terminou sua execucao.

## 6. Palavra-chave nonlocal

nonlocal permite alterar uma variavel
encontrada em um escopo externo
nao global.

```python
def limite(maximo):
    def decorator(func):
        def wrapper(*args, **kwargs):
            nonlocal maximo

            if maximo == 0:
                print("Limite de chamadas atingido.")
                return None

            maximo = maximo - 1
            return func(*args, **kwargs)

        return wrapper

    return decorator
```

O contador diminui a cada chamada.

Quando atinge zero, o wrapper
nao executa mais a funcao original.

## 7. Diferenca entre ler e alterar

Para ler vezes, nao e necessario nonlocal.

Para atribuir um novo valor a maximo
no wrapper, precisamos de nonlocal.

## 8. args e kwargs

*args aceita argumentos posicionais.

**kwargs aceita argumentos nomeados.

O wrapper pode encaminhar ambos
para a funcao decorada.

## 9. Retornos

O decorator repetir da transcricao
nao retorna os resultados das
execucoes da funcao original.

O decorator limite retorna
o resultado da funcao original
enquanto houver chamadas disponiveis.

## 10. Limitacoes

O exemplo nao implementa
validacao de numeros negativos.

O decorator limite compartilha
o contador entre as chamadas
da mesma funcao decorada.

A implementacao nao adiciona
sincronizacao para uso concorrente.

## 11. Proxima aula

A transcricao indica o estudo
da preservacao de metadados.

Por enquanto, o nome das funcoes
decoradas pode aparecer como wrapper.

Ainda nao implementamos functools.wraps.

## 12. Arquivos

src/aula19_closures_nonlocal.py
aulas/aula19_closures_nonlocal.py
tests/test_aula19_closures_nonlocal.py
anotacoes/aula19_closures_nonlocal.md
resultados/aula19_closures_nonlocal.json

## 13. Testes

16 testes novos.
Meta acumulada: 304.
