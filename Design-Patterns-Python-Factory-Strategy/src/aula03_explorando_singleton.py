"""Aula 03 - Explorando o Singleton com get_instance.

Implementacao didatica conforme a transcricao da Alura.

Limitacoes intencionais:
- Config() pode criar outras instancias.
- get_instance() nao e seguro contra concorrencia.
"""

import json
from pathlib import Path


class Config:
    NOME_DO_ARQUIVO = (
        Path(__file__).resolve().parent.parent / "config.json"
    )

    _instancia = None
    _leituras = 0

    def __init__(self):
        with open(
            self.NOME_DO_ARQUIVO,
            "r",
            encoding="utf-8",
        ) as arquivo:
            self.dados = json.load(arquivo)

        type(self)._leituras += 1

    @classmethod
    def get_instance(cls):
        if cls._instancia is None:
            print("Criando a instância única")
            cls._instancia = cls()

        return cls._instancia

    @classmethod
    def quantidade_leituras(cls):
        """Instrumentacao didatica para os testes."""
        return cls._leituras
