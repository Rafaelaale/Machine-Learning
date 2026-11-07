# Aula 21 - Decorando classes

## 1. Objetivo

Aplicar decorators diretamente a classes,
acrescentando comportamentos sem modificar
sua implementacao original.

Exemplos:
- Singleton com decorator.
- Registry com decorator parametrizado.

## 2. Singleton com decorator

```python
from functools import wraps

def singleton(cls):
    instancia = None

    @wraps(cls)
    def wrapper(*args, **kwargs):
        nonlocal instancia

        if instancia is None:
            instancia = cls(*args, **kwargs)

        return instancia

    return wrapper
```

## 3. Aplicacao

```python
@singleton
class Configuracao:
    def __init__(self):
        print("Carregando configurações...")
        self.valor = 42

config1 = Configuracao()
config2 = Configuracao()

print(config1 is config2)
```

Resultado: True.

## 4. Closure e nonlocal

A variavel instancia permanece acessivel
ao wrapper apos o retorno de singleton.

nonlocal permite atualizar instancia
dentro da funcao interna.

## 5. Metadados

wraps(cls) preserva metadados da classe,
como o nome e o acesso via __wrapped__.

Entretanto, a variavel Configuracao
passa a referenciar uma funcao wrapper.

A instancia continua sendo um objeto
da classe original.

## 6. Registry por decorator

```python
registry = {}

def registrar(nome):
    def decorator(cls):
        registry[nome] = cls
        return cls

    return decorator
```

## 7. Registro automatico

```python
@registrar("pix")
class PagamentoPix:
    pass

@registrar("cartao")
class PagamentoCartao:
    pass
```

O decorator executa no momento da
definicao da classe.

As classes ficam disponiveis em:

registry["pix"]
registry["cartao"]

## 8. Diferenca entre os decorators

singleton retorna uma funcao wrapper
no lugar da classe decorada.

registrar retorna a propria classe
que recebeu, preservando sua identidade.

## 9. Limitacoes

O singleton desta transcricao nao usa
threading.Lock ou outra sincronizacao.

Por isso, nao oferece garantia
de criacao unica em ambientes concorrentes.

O registry permite sobrescrever
chaves duplicadas sem emitir erro.

Essas limitacoes foram mantidas
para reproduzir o material da Alura.

## 10. Relação com as aulas anteriores

Aula 07:
Singleton thread-safe com Lock.

Aula 16:
Registry com metodo registrar().

Aula 20:
functools.wraps e metadados.

Aula 21:
combinacao desses conceitos
por meio de decorators de classes.

## 11. Proxima aula

A transcricao anuncia exemplos de
decorators em Python e frameworks.

## 12. Arquivos

src/aula21_decorando_classes.py
aulas/aula21_decorando_classes.py
tests/test_aula21_decorando_classes.py
anotacoes/aula21_decorando_classes.md
resultados/aula21_decorando_classes.json

## 13. Testes

16 testes novos.
Meta acumulada: 336.
