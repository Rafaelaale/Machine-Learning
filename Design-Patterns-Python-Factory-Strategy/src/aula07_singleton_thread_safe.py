"""Aula 07 - Singleton thread-safe com Lock e dupla verificacao."""

import threading


_lock = threading.Lock()


class Singleton:
    _instance = None
    _criacao_contador = 0

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with _lock:
                # Uma thread pode ter criado a instancia
                # enquanto outra aguardava pelo Lock.
                if cls._instance is None:
                    print("Criando a instância única")
                    cls._instance = super().__new__(cls)
                    cls._criacao_contador += 1

        return cls._instance

    @classmethod
    def quantidade_criacoes(cls):
        """Contador didatico para verificar as criacoes."""
        return cls._criacao_contador


def executar_concorrencia(n_threads=100):
    """Executa um teste concorrente limitado e verificavel."""
    if n_threads < 2:
        raise ValueError("Use pelo menos duas threads")

    barreira = threading.Barrier(n_threads)
    referencias = [None] * n_threads
    erros = []
    lock_erros = threading.Lock()

    def tarefa(indice):
        try:
            barreira.wait(timeout=15)
            referencias[indice] = Singleton()
        except Exception as erro:
            with lock_erros:
                erros.append(
                    f"{type(erro).__name__}: {erro}"
                )

    threads = [
        threading.Thread(
            target=tarefa,
            args=(indice,),
            daemon=True,
        )
        for indice in range(n_threads)
    ]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join(timeout=20)

    if any(thread.is_alive() for thread in threads):
        raise RuntimeError(
            "Uma ou mais threads nao finalizaram"
        )

    if erros:
        raise RuntimeError("; ".join(erros))

    if any(objeto is None for objeto in referencias):
        raise RuntimeError(
            "Uma thread nao retornou a instancia"
        )

    ids = {id(objeto) for objeto in referencias}

    return {
        "threads": n_threads,
        "instancias_distintas": len(ids),
        "criacoes": Singleton.quantidade_criacoes(),
        "mesma_instancia": len(ids) == 1,
        "referencias": referencias,
    }


def reiniciar_para_testes():
    """Usar apenas sem threads em execucao."""
    with _lock:
        Singleton._instance = None
        Singleton._criacao_contador = 0
