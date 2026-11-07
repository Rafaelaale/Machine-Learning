"""16 testes da Aula 11 - Padrao Proxy."""

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from src.aula11_padrao_proxy import (
    DIRETORIO_DADOS,
    Config,
    ConfigProxy,
    ConfigProxyLazyLoading,
    DataProxy,
    ExemploProperty,
    soma,
    demonstrar_partial,
    demonstrar_proxy,
)


class TestPadraoProxy(unittest.TestCase):

    def capturar(self, funcao):
        saida = io.StringIO()

        with contextlib.redirect_stdout(saida):
            resultado = funcao()

        return resultado, saida.getvalue()

    def test_01_json_exclusivo(self):
        caminho = DIRETORIO_DADOS / "config.json"
        self.assertTrue(caminho.is_file())

    def test_02_config_real_le_imediatamente(self):
        config, saida = self.capturar(Config)

        self.assertEqual(config.leituras, 1)
        self.assertIn("Lendo arquivo", saida)

    def test_03_config_real_tema_idioma(self):
        config, _ = self.capturar(Config)

        self.assertEqual(config.data["theme"], "ARC")
        self.assertEqual(
            config.data["language"], "PT-BR"
        )

    def test_04_proxy_nao_carrega_ao_criar(self):
        proxy = ConfigProxy()
        self.assertIsNone(proxy._config)

    def test_05_proxy_carrega_primeiro_acesso(self):
        proxy = ConfigProxy()

        tema, _ = self.capturar(
            lambda: proxy.data["theme"]
        )

        self.assertEqual(tema, "ARC")
        self.assertIsInstance(proxy._config, Config)

    def test_06_proxy_reutiliza_config(self):
        proxy = ConfigProxy()

        with contextlib.redirect_stdout(io.StringIO()):
            primeiro = proxy.data
            segundo = proxy.data

        self.assertIs(primeiro, segundo)
        self.assertEqual(proxy._config.leituras, 1)

    def test_07_proxy_primeira_leitura_unica(self):
        proxy = ConfigProxy()

        def acessar():
            proxy.data["theme"]
            proxy.data["language"]
            proxy.data["theme"]

        _, saida = self.capturar(acessar)

        self.assertEqual(
            saida.count("Lendo arquivo"),
            1,
        )

    def test_08_proxy_erro_somente_ao_acessar(self):
        with tempfile.TemporaryDirectory() as pasta:
            ausente = Path(pasta) / "ausente.json"

            proxy = ConfigProxy(ausente)
            self.assertIsNone(proxy._config)

            with self.assertRaises(FileNotFoundError):
                _ = proxy.data

            self.assertIsNone(proxy._config)

    def test_09_proxy_logging_primeiro_carregamento(self):
        proxy = ConfigProxyLazyLoading()

        _, saida = self.capturar(
            lambda: proxy.data["theme"]
        )

        self.assertIn("Carregando configuração", saida)
        self.assertIn("Acessando configuração", saida)

    def test_10_proxy_logging_acessos_repetidos(self):
        proxy = ConfigProxyLazyLoading()

        def acessar():
            proxy.data["theme"]
            proxy.data["language"]

        _, saida = self.capturar(acessar)

        self.assertEqual(
            saida.count("Carregando configuração"),
            1,
        )

        self.assertEqual(
            saida.count("Acessando configuração"),
            2,
        )

    def test_11_dataproxy_tema(self):
        proxy = ConfigProxyLazyLoading()
        dados = DataProxy(proxy)

        tema, saida = self.capturar(
            lambda: dados["theme"]
        )

        self.assertEqual(tema, "ARC")
        self.assertIn("chave: theme", saida)

    def test_12_dataproxy_idioma(self):
        dados = DataProxy(ConfigProxyLazyLoading())

        idioma, saida = self.capturar(
            lambda: dados["language"]
        )

        self.assertEqual(idioma, "PT-BR")
        self.assertIn("chave: language", saida)

    def test_13_dataproxy_chave_ausente(self):
        dados = DataProxy(ConfigProxyLazyLoading())

        valor, _ = self.capturar(
            lambda: dados["inexistente"]
        )

        self.assertIsNone(valor)

    def test_14_dataproxy_registra_chaves(self):
        dados = DataProxy(ConfigProxyLazyLoading())

        with contextlib.redirect_stdout(io.StringIO()):
            _ = dados["theme"]
            _ = dados["language"]

        self.assertEqual(
            dados.chaves_acessadas,
            ["theme", "language"],
        )

    def test_15_property_e_partial(self):
        self.assertEqual(ExemploProperty().x, 10)
        self.assertEqual(soma(10, 5), 15)

        resultado = demonstrar_partial()

        self.assertEqual(
            resultado["plus_10_com_5"], 15
        )
        self.assertEqual(
            resultado["plus_5_com_10"], 15
        )
        self.assertTrue(resultado["objeto_callable"])

    def test_16_demonstracao_completa(self):
        resultado, _ = self.capturar(
            demonstrar_proxy
        )

        self.assertTrue(
            resultado["objeto_real_ausente_antes"]
        )

        self.assertTrue(
            resultado["objeto_real_criado_depois"]
        )

        self.assertEqual(resultado["tema"], "ARC")
        self.assertEqual(resultado["idioma"], "PT-BR")
        self.assertEqual(resultado["leituras"], 1)

        self.assertEqual(
            resultado["chaves_acessadas"],
            ["theme", "language", "inexistente"],
        )


if __name__ == "__main__":
    unittest.main()
