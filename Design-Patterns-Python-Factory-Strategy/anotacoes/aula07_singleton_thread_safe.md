# Aula 07 - Avancando no Singleton Thread Safe

## Problema identificado anteriormente

Na Aula 05, duas threads podiam executar:

if cls._instance is None:

antes que uma delas criasse a instancia.

Isso permitia a criacao de objetos diferentes.

## Solucao da Aula 07

Utilizar threading.Lock().

O Lock garante que apenas uma thread
execute o bloco critico por vez.

## Dupla verificacao

```python
import threading

_lock = threading.Lock()

class Singleton:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with _lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)

        return cls._instance
```

## Por que verificar duas vezes?

Primeiro IF:

Evita adquirir o Lock quando a instancia
ja existe.

WITH LOCK:

Impede que duas threads executem
simultaneamente a criacao.

Segundo IF:

Impede que a segunda thread crie
outro objeto depois de esperar
a primeira liberar o Lock.

## Exemplo

Thread A verifica None.
Thread B tambem verifica None.

Thread A adquire o Lock.
Thread B espera.

Thread A cria o objeto.
Thread A libera o Lock.

Thread B adquire o Lock.
Thread B verifica novamente.

Como a instancia ja existe,
Thread B reutiliza o objeto.

## Testes

Utilizamos 100 threads e
threading.Barrier para aproximar
o inicio simultaneo.

Executamos cinco rodadas adicionais.

Cada rodada verifica:

- Uma identidade de objeto.
- Uma criacao registrada.
- Cem referencias retornadas.

Nao utilizamos loop infinito.

## Observacoes tecnicas

A classe da aula nao usa __init__
para reinicializar a instancia em
chamadas posteriores.

O metodo reiniciar_para_testes()
serve exclusivamente ao laboratorio,
sem threads concorrentes em andamento.

O Lock protege a criacao da instancia,
mas nao torna automaticamente seguro
todo estado mutavel armazenado no objeto.

O controle e por processo Python.
Processos independentes possuem memoria
e instancias proprias.

## Proxima aula

Analisar a alternativa para Singleton
que sera apresentada pela Alura.
