# Aula 01 - Modulos do Singleton

## O que aprendemos

Em Python, a importacao normal de um modulo
executa seu codigo na primeira carga e
reutiliza o modulo em importacoes posteriores.

O cache de modulos pode ser consultado
por meio de `sys.modules`.

## Exemplo da aula

```python
from singleton1_4 import singleton
from singleton1_4 import singleton
```

A segunda importacao nao cria outra instancia.

## Aplicacao pratica

Carregar `config.json` quando o modulo e
importado pela primeira vez.

As demais importacoes reutilizam o dicionario
`dados` existente.

## Estado compartilhado

```python
from singleton1_4 import singleton

singleton.incrementar()
print(singleton.contador)
```

Outras partes do programa que importarem
o mesmo objeto observarao o contador atualizado.

## Limites importantes

Esse comportamento vale normalmente dentro
do mesmo processo e interpretador Python.

Um novo processo pode criar outra instancia.

`importlib.reload()` executa o modulo novamente,
portanto pode recriar o objeto.

A classe do exemplo nao proibe novas
instanciacoes diretas: a unicidade vem da
maneira como o modulo compartilha a instancia.

## Quando utilizar

Configuracoes da aplicacao.
Objetos compartilhados dentro do processo.
Recursos que exigem instancia de uso comum.

Evite colocar estado global mutavel sem
necessidade, pois dificulta testes e isolamento.
