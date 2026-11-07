"""Aula 19 - Decoradores com parametros, closures e nonlocal.

Implementacao fiel aos exemplos da aula:
- repetir(vezes): fabrica de decoradores;
- limite(maximo): controla chamadas com nonlocal;
- wrappers com *args e **kwargs.

A preservacao de metadados sera estudada depois.
"""


def repetir(vezes):
    """Retorna um decorator que repete uma funcao."""

    def decorator(func):

        def wrapper(*args, **kwargs):
            for i in range(vezes):
                print(f"[{i + 1}]: ", end="")
                func(*args, **kwargs)

        return wrapper

    return decorator


@repetir(5)
def imprime():
    print("Executando função...")


# Decorator criado e armazenado para reutilizacao.

decorador_tres_vezes = repetir(3)


def diz_ola_original():
    print("Olá!")


# Aplicacao manual, conforme a transcricao.

diz_ola_repetida = decorador_tres_vezes(
    diz_ola_original
)


@decorador_tres_vezes
def say_hello():
    print("Hello!")


def limite(maximo):
    """Limita quantas vezes a funcao pode executar."""

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


def criar_ola_limitado(maximo=3):
    """Cria uma nova funcao decorada para cada demonstracao."""

    @limite(maximo)
    def diz_ola():
        print("Olá!")

    return diz_ola


def criar_contador(maximo):
    """Exemplo adicional de closure com nonlocal."""

    def consultar():
        return maximo

    def decrementar():
        nonlocal maximo
        maximo = maximo - 1
        return maximo

    return consultar, decrementar


def analisar_aula19():
    return {
        "aula": 19,
        "titulo": "Decoradores com parametros, closures e nonlocal",
        "decoradores": ["repetir", "limite"],
        "fabrica_de_decoradores": True,
        "utiliza_closure": True,
        "utiliza_nonlocal": True,
        "utiliza_args_kwargs": True,
        "repetir_retorna_resultados": False,
        "limite_preserva_retorno": True,
        "metadados_preservados_por_wraps": False,
    }
