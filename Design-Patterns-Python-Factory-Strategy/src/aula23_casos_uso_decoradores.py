"""Aula 23 - Casos de uso de decoradores.

FastAPI, dataclass, property, staticmethod,
classmethod e lru_cache.

Os demais frameworks possuem exemplos separados
na pasta exemplos, sem dependencias obrigatorias.
"""

from dataclasses import dataclass
from datetime import datetime
from functools import lru_cache
from fastapi import FastAPI


# 1. FASTAPI: DECORATOR E REGISTRY

app = FastAPI()


@app.get("/users")
def listar():
    return [{"id": 1, "nome": "Maria"}]


# 2. DATACLASS

@dataclass
class Usuario:
    nome: str
    idade: int


# 3. PROPERTY

class Pessoa:
    def __init__(self, nome, idade):
        self.nome = nome
        self.idade = idade

    @property
    def ano_nascimento(self):
        return datetime.now().year - self.idade


# 4. STATICMETHOD E CLASSMETHOD

class Math:
    @staticmethod
    def dobro(x):
        return x * 2

    @classmethod
    def criar(cls):
        return cls()


# 5. LRU_CACHE

@lru_cache(maxsize=32)
def multiplicar(a, b):
    print(f"Calculando {a} * {b}")
    return a * b


def demonstrar_fastapi():
    """Consulta o registro de rotas sem iniciar servidor."""

    rota = next(
        (
            rota
            for rota in app.routes
            if getattr(rota, "path", None) == "/users"
            and "GET" in getattr(rota, "methods", set())
        ),
        None,
    )

    if rota is None:
        raise RuntimeError("Rota GET /users nao registrada")

    return {
        "rota": rota.path,
        "metodo": "GET",
        "endpoint": rota.endpoint.__name__,
        "resposta": rota.endpoint(),
    }


def demonstrar_nativos():
    usuario = Usuario("Maria", 30)
    pessoa = Pessoa("Ana", 25)
    objeto_math = Math.criar()

    return {
        "dataclass": {
            "nome": usuario.nome,
            "idade": usuario.idade,
            "representacao": repr(usuario),
        },
        "property": {
            "nome": pessoa.nome,
            "idade": pessoa.idade,
            "ano_nascimento": pessoa.ano_nascimento,
        },
        "staticmethod": {
            "dobro_de_5": Math.dobro(5),
        },
        "classmethod": {
            "instancia_valida": isinstance(objeto_math, Math),
        },
    }


def demonstrar_cache():
    """Demonstra dois calculos e tres reutilizacoes."""

    multiplicar.cache_clear()

    primeiro = multiplicar(2, 3)
    segundo = multiplicar(2, 3)
    terceiro = multiplicar(4, 5)
    quarto = multiplicar(4, 5)
    quinto = multiplicar(4, 5)

    info = multiplicar.cache_info()

    return {
        "resultados": [
            primeiro,
            segundo,
            terceiro,
            quarto,
            quinto,
        ],
        "hits": info.hits,
        "misses": info.misses,
        "maxsize": info.maxsize,
        "currsize": info.currsize,
    }


def analisar_aula23():
    return {
        "aula": 23,
        "titulo": "Casos de uso de decoradores",
        "frameworks": [
            "FastAPI",
            "Flask",
            "Click",
            "Django",
            "Celery",
        ],
        "decoradores_nativos": [
            "dataclass",
            "property",
            "staticmethod",
            "classmethod",
            "lru_cache",
        ],
        "fastapi_registry": True,
        "cache_maxsize": 32,
        "frameworks_opcionais_em_arquivos_separados": True,
    }
