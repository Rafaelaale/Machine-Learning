# Aula 23 - Casos de uso de decoradores

## Objetivo

Encerrar o estudo do padrão Decorator
identificando aplicações reais em Python
e em frameworks.

## FastAPI

@app.get("/users") registra uma função como
endpoint de uma rota HTTP GET.

O registro combina Decorator e Registry.

Arquivo executável:
src/aula23_casos_uso_decoradores.py

## Flask

@app.route("/home") registra uma rota web.

Exemplo salvo:
exemplos/aula23_flask.py

## Click

@click.group() cria um grupo de comandos.

@cli.command() registra um comando de terminal.

Exemplo salvo:
exemplos/aula23_click.py

## Django

@receiver(post_save, sender=User) conecta uma
função a um sinal de pós-salvamento.

Em um projeto real, o sender deve ser
um modelo Django válido, e o framework
deve estar configurado.

Exemplo salvo:
exemplos/aula23_django.py

## Celery

@shared_task registra uma tarefa que
pode ser executada pelo Celery.

Uma execução real exige configuração
do aplicativo e da infraestrutura.

Exemplo salvo:
exemplos/aula23_celery.py

## dataclass

@dataclass cria automaticamente métodos
úteis para classes de dados.

Exemplos: __init__, __repr__ e __eq__.

## property

@property permite acessar o resultado
de um método como atributo.

Exemplo: pessoa.ano_nascimento.

O cálculo apresentado na aula usa
ano atual menos idade, portanto é
uma estimativa do ano de nascimento.

## staticmethod

@staticmethod define um método que
não recebe self nem cls automaticamente.

## classmethod

@classmethod recebe a classe pelo
primeiro parâmetro, tradicionalmente cls.

## lru_cache

@lru_cache(maxsize=32) armazena
até 32 resultados de combinações
de argumentos.

Chamadas repetidas podem ser
atendidas pela cache.

Hits representam reutilizações.

Misses representam chamadas que
precisaram calcular um resultado.

LRU significa Least Recently Used:
quando é preciso remover uma entrada,
a cache elimina a menos recentemente usada.

Não significa necessariamente manter
os resultados mais frequentemente acessados.

## Bibliotecas opcionais

Os exemplos de Flask, Click, Django
e Celery são arquivos independentes.

A sintaxe desses arquivos é validada,
mas sua execução exige as dependências
e configurações correspondentes.

Os testes obrigatórios utilizam
FastAPI e recursos nativos de Python.

## Arquivos

src/aula23_casos_uso_decoradores.py
aulas/aula23_casos_uso_decoradores.py
tests/test_aula23_casos_uso_decoradores.py
anotacoes/aula23_casos_uso_decoradores.md

exemplos/aula23_flask.py
exemplos/aula23_click.py
exemplos/aula23_django.py
exemplos/aula23_celery.py

resultados/aula23_casos_uso_decoradores.json

## Validação

16 novos testes.
Meta acumulada: 368.
