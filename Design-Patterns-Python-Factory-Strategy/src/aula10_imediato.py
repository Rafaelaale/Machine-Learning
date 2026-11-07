"""Aula 10 - Carregamento imediato de configuracao."""

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
        self.leituras = 0

        print("Lendo arquivo de configuração...")

        with self.arquivo.open(
            "r",
            encoding="utf-8",
        ) as arquivo_json:
            self.data = json.load(arquivo_json)

        self.leituras += 1


# Este objeto e criado durante o import do modulo.
# Portanto, o JSON tambem e lido nesse momento.
config = Config()
