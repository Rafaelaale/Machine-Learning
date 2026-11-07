"""Aula 17 - Entendendo o que sao decoradores.

O decorator adiciona logs sem modificar
as funcoes originais.
"""


def somar(a, b):
    return a + b


def dividir(a, b):
    return a / b


# Solucoes manuais: repeticao de codigo.

def somar_com_log(a, b):
    resultado = a + b
    print(f"Somando {a} + {b} = {resultado}")
    return resultado


def somar_com_log_2(a, b):
    resultado = somar(a, b)
    print(f"Somando {a} + {b} = {resultado}")
    return resultado


def dividir_com_log(a, b):
    resultado = dividir(a, b)
    print(f"Dividindo {a} / {b} = {resultado}")
    return resultado


# Solucao reutilizavel: Decorator.

def adicionar_log(func):
    def wrapper(a, b):
        resultado = func(a, b)
        print(
            f"Executando {func.__name__}"
            f"({a}, {b}) = {resultado}"
        )
        return resultado

    return wrapper


# Aplicacao explicita, conforme a aula.

soma_com_log2 = adicionar_log(somar)
dividir_com_log2 = adicionar_log(dividir)


def analisar_decorator():
    return {
        "aula": 17,
        "padrao": "Decorator",
        "funcoes_originais": ["somar", "dividir"],
        "decorator": "adicionar_log",
        "wrapper": "wrapper",
        "adiciona_log": True,
        "preserva_resultado": True,
        "modifica_funcoes_originais": False,
        "sintaxe_arroba": False,
        "functools_wraps": False,
    }
