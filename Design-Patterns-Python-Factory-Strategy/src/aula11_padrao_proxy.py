"""Aula 11 - Padrao Proxy em Python.

Implementacoes:
- Config: objeto real, leitura imediata
- ConfigProxy: virtual proxy com lazy loading
- ConfigProxyLazyLoading: proxy com logs
- DataProxy: interceptacao de chaves
- property e functools.partial
"""

import json
from functools import partial
from pathlib import Path


DIRETORIO_DADOS = (
    Path(__file__).resolve().parent.parent
    / "dados_aula11"
)


def resolver_arquivo(arquivo):
    caminho = Path(arquivo)

    if not caminho.is_absolute():
        caminho = DIRETORIO_DADOS / caminho

    return caminho


class Config:
    """Objeto real: carrega o JSON na inicializacao."""

    def __init__(self, arquivo="config.json"):
        self.arquivo = resolver_arquivo(arquivo)
        self.leituras = 0

        print("Lendo arquivo de configuração...")

        with self.arquivo.open(
            "r", encoding="utf-8"
        ) as arquivo_json:
            self.data = json.load(arquivo_json)

        self.leituras += 1


class ConfigProxy:
    """Substituto com a mesma propriedade data."""

    def __init__(self, arquivo="config.json"):
        self.arquivo = arquivo
        self._config = None

    def _carregar_config(self):
        if self._config is None:
            self._config = Config(self.arquivo)

    @property
    def data(self):
        self._carregar_config()
        return self._config.data


class ConfigProxyLazyLoading(ConfigProxy):
    """Proxy com mensagens para observar os acessos."""

    def _carregar_config(self):
        if self._config is None:
            print("Carregando configuração...")
            super()._carregar_config()

    @property
    def data(self):
        print("Acessando configuração...")
        return super().data


class DataProxy:
    """Proxy que intercepta leitura por chave."""

    def __init__(self, config_proxy):
        self._config_proxy = config_proxy
        self.chaves_acessadas = []

    def __getitem__(self, chave):
        print(
            f"Acessando configuração para a chave: {chave}"
        )

        self.chaves_acessadas.append(chave)

        # Como na transcricao, uma chave ausente
        # retorna None em vez de gerar KeyError.
        return self._config_proxy.data.get(chave, None)


class ExemploProperty:
    @property
    def x(self):
        return 10


def soma(a, b):
    return a + b


def demonstrar_partial():
    plus_10 = partial(soma, 10)
    plus_5 = partial(soma, b=5)

    return {
        "plus_10_com_5": plus_10(5),
        "plus_5_com_10": plus_5(10),
        "objeto_callable": callable(plus_10),
    }


def demonstrar_proxy():
    proxy = ConfigProxyLazyLoading()

    antes = proxy._config is None

    dados = DataProxy(proxy)

    tema = dados["theme"]
    idioma = dados["language"]
    ausente = dados["inexistente"]

    return {
        "objeto_real_ausente_antes": antes,
        "objeto_real_criado_depois": (
            proxy._config is not None
        ),
        "tema": tema,
        "idioma": idioma,
        "chave_inexistente": ausente,
        "leituras": proxy._config.leituras,
        "chaves_acessadas": list(
            dados.chaves_acessadas
        ),
        "property_x": ExemploProperty().x,
        "partial": demonstrar_partial(),
    }
