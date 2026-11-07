"""Aula 20 - Preservando metadados e empilhando decoradores.

Conteudo:
- Problema do nome wrapper.
- functools.wraps(func).
- Preservacao de metadados.
- Empilhamento de decoradores.
- Ordem de aplicacao de baixo para cima.
"""

import functools


# PRIMEIRO EXEMPLO: SEM PRESERVAR METADADOS

def adicionar_log_sem_wraps(func):

    def wrapper(a, b):
        resultado = func(a, b)
        print(
            f"Executando {func.__name__}"
            f"({a}, {b}) = {resultado}"
        )
        return resultado

    return wrapper


@adicionar_log_sem_wraps
def somar_sem_wraps(a, b):
    """Soma dois numeros sem preservar metadados."""
    return a + b


# SEGUNDO EXEMPLO: COM FUNCTOOLS.WRAPS

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


@adicionar_log
def somar(a, b):
    """Soma dois numeros."""
    return a + b


@adicionar_log
def dividir(a, b):
    """Divide dois numeros."""
    return a / b


# TERCEIRO EXEMPLO: EMPILHAMENTO

def repetir(vezes):
    """Fabrica de decorators, como na transcricao."""

    def decorator(func):

        def wrapper(*args, **kwargs):
            for i in range(vezes):
                print(f"[{i + 1}]: ", end="")
                func(*args, **kwargs)

        return wrapper

    return decorator


@repetir(3)
@adicionar_log
def somar_empilhada(a, b):
    """Soma utilizada no empilhamento."""
    return a + b


# Exemplo adicional: inverter a ordem
# para observar a diferenca do resultado.

@adicionar_log
@repetir(3)
def somar_ordem_invertida(a, b):
    return a + b


def somar_original(a, b):
    """Funcao nao decorada."""
    return a + b


def demonstrar_ordem_aplicacao():
    """Compara o empilhamento com a aplicacao manual."""

    def operacao(a, b):
        return a + b

    decorada_primeiro = adicionar_log(operacao)
    decorada_depois = repetir(3)(decorada_primeiro)

    return decorada_depois


def demonstrar_metadados():
    """Mostra os metadados das funcoes decoradas."""

    return {
        "sem_wraps": {
            "nome": somar_sem_wraps.__name__,
            "documentacao": somar_sem_wraps.__doc__,
            "possui_wrapped": hasattr(
                somar_sem_wraps, "__wrapped__"
            ),
        },
        "com_wraps": {
            "nome": somar.__name__,
            "documentacao": somar.__doc__,
            "possui_wrapped": hasattr(
                somar, "__wrapped__"
            ),
            "nome_original": somar.__wrapped__.__name__,
        },
        "empilhada": {
            "nome": somar_empilhada.__name__,
            "possui_wrapped": hasattr(
                somar_empilhada, "__wrapped__"
            ),
        },
    }


def analisar_aula20():
    return {
        "aula": 20,
        "titulo": "Preservando metadados e empilhando decoradores",
        "padrao": "Decorator",
        "functools_wraps": True,
        "empilhamento": True,
        "aplicacao_de_baixo_para_cima": True,
        "repetir_vezes": 3,
        "decorator_repetir_preserva_retorno": False,
        "decorator_repetir_usa_wraps": False,
        "decorators_com_classes": False,
    }
