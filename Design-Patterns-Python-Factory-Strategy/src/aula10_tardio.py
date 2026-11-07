"""Aula 10 - Inicializacao tardia usando @property."""

import json
from pathlib import Path


ARQUIVO_CONFIG = (
    Path(__file__).resolve().parent.parent
    / "dados_aula10"
    / "config.json"
)


class Config:
    def __init__(self, arquivo=ARQUIVO_CONFIG):
        self.arquivo = Path(arquivo)
        self._data = None
        self.leituras = 0

    @property
    def data(self):
        if self._data is None:
            print("Lendo arquivo de configuração...")

            with self.arquivo.open(
                "r",
                encoding="utf-8",
            ) as arquivo_json:
                self._data = json.load(arquivo_json)

            self.leituras += 1

        return self._data


# Criar o objeto nao executa a leitura.
config = Config()
