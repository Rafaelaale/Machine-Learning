"""Aula 04 - Singleton Pythonico com __new__.

A propria classe controla sua instancia unica.

Implementacao didatica sem protecao para threads,
conforme o conteudo desta aula da Alura.
"""

import json
from pathlib import Path


class Singleton:

    NOME_DO_ARQUIVO = (
        Path(__file__).resolve().parent.parent
        / "config.json"
    )

    _instancia = None
    _leituras = 0

    def __new__(cls):
        if cls._instancia is None:
            print("Criando a instância única")

            # Chama object.__new__ atraves de super().
            # Usar Singleton() aqui provocaria recursao.
            instancia = super().__new__(cls)

            # A instancia so entra no cache apos o
            # carregamento bem-sucedido do arquivo.
            with open(
                cls.NOME_DO_ARQUIVO,
                "r",
                encoding="utf-8",
            ) as arquivo:
                instancia.dados = json.load(arquivo)

            cls._leituras += 1
            cls._instancia = instancia

        return cls._instancia

    @classmethod
    def quantidade_leituras(cls):
        """Instrumentacao didatica do laboratorio."""
        return cls._leituras
