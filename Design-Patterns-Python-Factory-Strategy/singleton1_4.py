"""Aula 01 - Modulos como Singleton.

Importacoes normais reutilizam o modulo carregado
em sys.modules, dentro do mesmo interpretador Python.
"""

import json
from pathlib import Path


# Classe considerada "privada" por convencao de uso.
# O Python nao impede sua instanciacao manual.
class Singleton:

    def __init__(self):
        print("Criando a instância única")
        self.nome = "Instancia compartilhada"
        self.contador = 0

    def incrementar(self):
        self.contador += 1
        return self.contador


# Objeto criado quando o modulo e executado pela primeira vez.
singleton = Singleton()


# Caminho absoluto baseado na localizacao deste arquivo.
NOME_ARQUIVO = Path(__file__).resolve().parent / "config.json"


# Configuracoes carregadas uma vez durante a importacao normal.
dados = None

with open(NOME_ARQUIVO, "r", encoding="utf-8") as arquivo:
    dados = json.load(arquivo)
