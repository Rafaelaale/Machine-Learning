"""Aula 21 - Decorando classes.

Exemplos da transcricao:
1. Singleton usando decorator, closure e nonlocal.
2. Registry preenchido por decorators de classes.

O singleton apresentado e didatico e nao
implementa sincronizacao entre threads.
"""

from functools import wraps


def singleton(cls):
    """Decorator que transforma uma classe em singleton."""
    instancia = None

    @wraps(cls)
    def wrapper(*args, **kwargs):
        nonlocal instancia

        if instancia is None:
            instancia = cls(*args, **kwargs)

        return instancia

    return wrapper


@singleton
class Configuracao:
    """Configuracao compartilhada da aplicacao."""

    def __init__(self):
        print("Carregando configurações...")
        self.valor = 42


# REGISTRY COM DECORATORS

registry = {}


def registrar(nome):
    """Cria um decorator que registra uma classe."""

    def decorator(cls):
        registry[nome] = cls
        return cls

    return decorator


@registrar("pix")
class PagamentoPix:
    pass


@registrar("cartao")
class PagamentoCartao:
    pass


def demonstrar_singleton():
    """Verifica tres referencias ao mesmo objeto."""

    config1 = Configuracao()
    config2 = Configuracao()
    config3 = Configuracao()

    return {
        "valor": config1.valor,
        "mesma_instancia": config1 is config2 is config3,
        "nome_decorado": Configuracao.__name__,
        "wrapper_eh_funcao": callable(Configuracao),
        "wrapper_eh_classe": isinstance(Configuracao, type),
        "classe_original": Configuracao.__wrapped__.__name__,
        "tipo_da_instancia": type(config1).__name__,
    }


def demonstrar_registry():
    """Consulta as classes registradas por decorator."""

    pix = registry["pix"]
    cartao = registry["cartao"]

    return {
        "chaves": sorted(registry.keys()),
        "pix": pix.__name__,
        "cartao": cartao.__name__,
        "pix_preserva_classe": pix is PagamentoPix,
        "cartao_preserva_classe": cartao is PagamentoCartao,
        "instancia_pix": type(pix()).__name__,
        "instancia_cartao": type(cartao()).__name__,
    }


def analisar_aula21():
    return {
        "aula": 21,
        "titulo": "Decorando classes",
        "singleton_com_decorator": True,
        "singleton_com_closure": True,
        "singleton_com_nonlocal": True,
        "singleton_com_wraps": True,
        "registry_com_decorator": True,
        "registry_com_parametro": True,
        "registro_automatico_na_definicao": True,
        "chave_duplicada_sobrescreve": True,
        "singleton_thread_safe": False,
    }
