"""Aula 05 - Singleton e condicoes de corrida.

Compara:
1. Singleton original da Aula 04 com 100 threads.
2. Versao didatica com janela de corrida controlada.

Aula 05 NAO implementa Lock para proteger o Singleton.
"""

import json
import threading

from src.aula04_singleton_pythonico import Singleton


N_THREADS = 100


def executar_threads(
    quantidade,
    criador,
    timeout=10,
):
    """Inicia threads juntas e preserva referencias aos objetos."""
    if quantidade < 2:
        raise ValueError("Use pelo menos duas threads")

    inicio = threading.Barrier(quantidade)
    referencias = []
    erros = []
    coleta = threading.Lock()

    def tarefa():
        try:
            inicio.wait(timeout=timeout)
            instancia = criador()

            with coleta:
                referencias.append(instancia)

        except Exception as erro:
            with coleta:
                erros.append(
                    f"{type(erro).__name__}: {erro}"
                )

    threads = [
        threading.Thread(
            target=tarefa,
            daemon=True,
        )
        for _ in range(quantidade)
    ]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join(timeout=timeout + 2)

    pendentes = sum(
        thread.is_alive() for thread in threads
    )

    if pendentes:
        raise RuntimeError(
            f"{pendentes} threads nao terminaram"
        )

    if erros:
        raise RuntimeError(
            "Erros nas threads: " + "; ".join(erros)
        )

    if len(referencias) != quantidade:
        raise RuntimeError(
            "Nem todas as instancias foram registradas"
        )

    return {
        "threads": quantidade,
        "instancias_distintas": len({
            id(objeto) for objeto in referencias
        }),
        "ids": sorted({
            id(objeto) for objeto in referencias
        }),
        "objetos": referencias,
    }


def testar_singleton_original(quantidade=N_THREADS):
    """Teste real: pode ou nao observar a corrida."""
    instancia_anterior = Singleton._instancia
    leituras_anteriores = Singleton._leituras

    try:
        Singleton._instancia = None
        Singleton._leituras = 0

        resultado = executar_threads(
            quantidade,
            Singleton,
        )

        resultado["leituras"] = (
            Singleton.quantidade_leituras()
        )

        return resultado

    finally:
        Singleton._instancia = instancia_anterior
        Singleton._leituras = leituras_anteriores


class SingletonComCorridaControlada:
    """Reproduz a verificacao vulneravel de __new__.

    Duas threads entram no bloco antes que qualquer
    uma publique a instancia compartilhada.
    """

    NOME_DO_ARQUIVO = Singleton.NOME_DO_ARQUIVO
    _instancia = None
    _leituras = 0
    _barreira_critica = None

    def __new__(cls):
        if cls._instancia is None:
            barreira = cls._barreira_critica

            if barreira is not None:
                barreira.wait(timeout=10)

            instancia = object.__new__(cls)

            with open(
                cls.NOME_DO_ARQUIVO,
                "r",
                encoding="utf-8",
            ) as arquivo:
                instancia.dados = json.load(arquivo)

            cls._leituras += 1
            cls._instancia = instancia

        return cls._instancia


def demonstrar_corrida_controlada():
    """Forca a intercalacao e revela duas instancias.

    Esta classe e um instrumento de estudo, nao
    uma alteracao no Singleton original.
    """
    classe = SingletonComCorridaControlada

    classe._instancia = None
    classe._leituras = 0
    classe._barreira_critica = threading.Barrier(2)

    try:
        resultado = executar_threads(
            quantidade=2,
            criador=classe,
        )

        resultado["leituras"] = classe._leituras

        return resultado

    finally:
        classe._barreira_critica = None
        classe._instancia = None
        classe._leituras = 0


def resumo(resultado):
    """Remove referencias de objetos para serializar em JSON."""
    return {
        "threads": resultado["threads"],
        "instancias_distintas": (
            resultado["instancias_distintas"]
        ),
        "leituras": resultado["leituras"],
        "ids": resultado["ids"],
    }


def executar(quantidade=N_THREADS):
    real = testar_singleton_original(quantidade)
    controlado = demonstrar_corrida_controlada()

    return {
        "aula": 5,
        "padrao": "Singleton",
        "tema": "Condicao de corrida em threads",
        "experimento_real": resumo(real),
        "experimento_controlado": resumo(controlado),
        "corrida_demonstrada": (
            controlado["instancias_distintas"] == 2
            and controlado["leituras"] == 2
        ),
        "singleton_original_modificado": False,
        "thread_safe_implementado": False,
    }
