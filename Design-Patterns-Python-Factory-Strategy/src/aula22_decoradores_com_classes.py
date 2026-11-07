"""Aula 22 - Implementando decoradores com classes.

Exemplos da transcricao:
- ComLog: decorator sem parametros.
- Repetir: decorator com parametros.
- __call__: torna objetos invocaveis.

Esta aula nao usa functools.wraps.
"""


class ComLog:
    """Decorator baseado em classe."""

    def __init__(self, func):
        self.func = func

    def __call__(self, a, b):
        print(
            f"Executando {self.func.__name__} ({a}, {b})"
        )

        resultado = self.func(a, b)

        print(f"Resultado: {resultado}")

        return resultado


@ComLog
def somar(a, b):
    return a + b


class Repetir:
    """Decorator parametrizado baseado em classe."""

    def __init__(self, vezes):
        self.vezes = vezes

    def __call__(self, func):

        def wrapper(*args, **kwargs):
            for i in range(self.vezes):
                print(f"[{i + 1}]", end=" ")
                func(*args, **kwargs)

        return wrapper


@Repetir(5)
def imprime():
    print("Executando função...")


def somar_original(a, b):
    return a + b


def imprime_original():
    print("Executando função...")


def demonstrar_aplicacao_manual():
    """Mostra a equivalencia da sintaxe com @."""

    soma_manual = ComLog(somar_original)

    repetidor = Repetir(3)
    imprime_manual = repetidor(imprime_original)

    return {
        "soma_manual": soma_manual,
        "imprime_manual": imprime_manual,
        "repetidor": repetidor,
    }


def analisar_aula22():
    return {
        "aula": 22,
        "titulo": "Implementando decoradores com classes",
        "decoradores": ["ComLog", "Repetir"],
        "metodo_especial": "__call__",
        "comlog_recebe_funcao_no_init": True,
        "comlog_retorna_resultado": True,
        "repetir_recebe_vezes_no_init": True,
        "repetir_recebe_funcao_no_call": True,
        "repetir_retorna_wrapper": True,
        "repetir_preserva_retorno": False,
        "functools_wraps": False,
    }
