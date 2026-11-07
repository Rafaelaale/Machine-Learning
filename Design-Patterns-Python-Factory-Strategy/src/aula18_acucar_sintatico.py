"""Aula 18 - Uma pitada de acucar sintatico.

Demonstra a equivalencia entre:

    funcao = adicionar_log(funcao)

e:

    @adicionar_log
    def funcao(...):
        ...

Reutiliza o decorator implementado na Aula 17.
"""

from src.aula17_entendendo_decoradores import adicionar_log


# FORMA 1: APLICACAO EXPLICITA

def somar_original(a, b):
    return a + b


def dividir_original(a, b):
    return a / b


somar_explicita = adicionar_log(somar_original)
dividir_explicita = adicionar_log(dividir_original)


# FORMA 2: ACUCAR SINTATICO COM @

@adicionar_log
def somar(a, b):
    return a + b


@adicionar_log
def dividir(a, b):
    return a / b


def demonstrar_equivalencia():
    """Cria funcoes com o mesmo nome e comportamento.

    A forma explicita e a forma com @ devem
    produzir o mesmo resultado e o mesmo log.
    """

    def operacao(a, b):
        return a + b

    versao_explicita = adicionar_log(operacao)

    @adicionar_log
    def operacao(a, b):
        return a + b

    versao_arroba = operacao

    return versao_explicita, versao_arroba


def comparar_proxy_decorator():
    """Diferencas conceituais apresentadas na aula."""
    return {
        "proxy": {
            "objetivo": "Controlar acesso a um objeto",
            "exemplos": [
                "Lazy Loading",
                "Controle de acesso",
                "Ocultacao de detalhes",
            ],
        },
        "decorator": {
            "objetivo": "Adicionar funcionalidades",
            "exemplos": [
                "Logs",
                "Comportamento adicional",
            ],
        },
    }


def analisar_aula18():
    return {
        "aula": 18,
        "titulo": "Uma pitada de acucar sintatico",
        "padrao": "Decorator",
        "sintaxe_explicita": True,
        "sintaxe_arroba": True,
        "equivalencia": True,
        "decorator_reutilizado_da_aula17": True,
        "funcao_original_preservada": True,
        "functools_wraps_implementado": False,
        "args_kwargs_implementado": False,
    }
