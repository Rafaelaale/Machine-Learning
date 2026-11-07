"""Aula 06 - Casos de uso do Singleton em Python."""

import logging
import sys
import threading

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


def verificar_none():
    a = None
    b = None
    c = None

    return {
        "none_is_none": None is None,
        "a_is_b": a is b,
        "a_is_c": a is c,
    }


def verificar_booleanos():
    a = True
    b = True
    c = False
    d = False

    return {
        "true_unico": a is b,
        "false_unico": c is d,
        "true_diferente_false": a is not c,
    }


def verificar_fluxos():
    entrada = sys.stdin
    saida = sys.stdout
    erro = sys.stderr

    return {
        "stdin_reutilizado": entrada is sys.stdin,
        "stdout_reutilizado": saida is sys.stdout,
        "stderr_reutilizado": erro is sys.stderr,
        "fluxos_disponiveis": all(
            fluxo is not None
            for fluxo in (entrada, saida, erro)
        ),
    }


def verificar_logger(nome="design_patterns.aula06"):
    primeiro = logging.getLogger(nome)
    segundo = logging.getLogger(nome)

    return {
        "nome": nome,
        "mesmo_objeto": primeiro is segundo,
        "mesmo_id": id(primeiro) == id(segundo),
        "tipo": type(primeiro).__name__,
    }


def verificar_sqlalchemy():
    """Demonstra uma sessao por escopo de thread."""
    engine = create_engine("sqlite:///:memory:")

    Session = scoped_session(
        sessionmaker(bind=engine)
    )

    try:
        primeira = Session()
        segunda = Session()

        mesma_thread = primeira is segunda
        resultado_thread = {}
        erros = []

        def trabalhar():
            try:
                outra = Session()
                resultado_thread["mesma_sessao"] = (
                    outra is primeira
                )
            except Exception as erro:
                erros.append(str(erro))
            finally:
                Session.remove()

        thread = threading.Thread(target=trabalhar)
        thread.start()
        thread.join(timeout=10)

        if thread.is_alive():
            raise RuntimeError("Thread nao finalizou")

        if erros:
            raise RuntimeError("; ".join(erros))

        if "mesma_sessao" not in resultado_thread:
            raise RuntimeError("Resultado da thread ausente")

        Session.remove()

        terceira = Session()

        return {
            "mesma_thread_mesma_sessao": mesma_thread,
            "outra_thread_mesma_sessao":
                resultado_thread["mesma_sessao"],
            "remove_cria_nova_sessao":
                terceira is not primeira,
            "escopo": "thread-local",
            "banco": "SQLite em memoria",
        }

    finally:
        Session.remove()
        engine.dispose()


def executar():
    return {
        "aula": 6,
        "titulo": "Casos de uso do Singleton",
        "none": verificar_none(),
        "booleanos": verificar_booleanos(),
        "fluxos": verificar_fluxos(),
        "logging": verificar_logger(),
        "sqlalchemy": verificar_sqlalchemy(),
    }
