"""16 testes da Aula 03 - Singleton com get_instance."""

import contextlib
import io
import json
import sys
import tempfile
import unittest

from pathlib import Path


BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from src.aula03_explorando_singleton import Config


class TestSingletonGetInstance(unittest.TestCase):

    def setUp(self):
        # Isola o estado compartilhado entre os testes.
        Config._instancia = None
        Config._leituras = 0

    def tearDown(self):
        Config._instancia = None
        Config._leituras = 0

    def primeira(self):
        with contextlib.redirect_stdout(io.StringIO()):
            return Config.get_instance()

    def test_01_instancia_inicial_nula(self):
        self.assertIsNone(Config._instancia)

    def test_02_primeira_criacao(self):
        instancia = self.primeira()
        self.assertIsInstance(instancia, Config)

    def test_03_reutiliza_instancia(self):
        a = self.primeira()
        b = Config.get_instance()
        self.assertIs(a, b)

    def test_04_mesmo_id(self):
        a = self.primeira()
        b = Config.get_instance()
        self.assertEqual(id(a), id(b))

    def test_05_apenas_uma_leitura(self):
        self.primeira()
        Config.get_instance()
        Config.get_instance()

        self.assertEqual(Config.quantidade_leituras(), 1)

    def test_06_mensagem_primeira_criacao(self):
        saida = io.StringIO()

        with contextlib.redirect_stdout(saida):
            Config.get_instance()

        self.assertEqual(
            saida.getvalue().count("Criando a instância única"),
            1,
        )

    def test_07_sem_mensagem_repetida(self):
        self.primeira()
        saida = io.StringIO()

        with contextlib.redirect_stdout(saida):
            Config.get_instance()

        self.assertEqual(saida.getvalue(), "")

    def test_08_configuracao_dicionario(self):
        instancia = self.primeira()
        self.assertIsInstance(instancia.dados, dict)

    def test_09_arquivo_existe(self):
        self.assertTrue(Config.NOME_DO_ARQUIVO.is_file())

    def test_10_json_foi_carregado(self):
        instancia = self.primeira()

        with open(
            Config.NOME_DO_ARQUIVO,
            encoding="utf-8",
        ) as arquivo:
            original = json.load(arquivo)

        self.assertEqual(instancia.dados, original)

    def test_11_instanciacao_direta_e_diferente(self):
        a = self.primeira()
        b = Config()

        self.assertIsNot(a, b)

    def test_12_instanciacao_direta_rele_arquivo(self):
        self.primeira()
        Config()

        self.assertEqual(Config.quantidade_leituras(), 2)

    def test_13_direta_nao_substitui_instancia(self):
        a = self.primeira()
        Config()

        self.assertIs(Config.get_instance(), a)

    def test_14_atributo_classe_compartilhado(self):
        self.primeira()
        self.assertIs(
            Config._instancia,
            Config.get_instance(),
        )

    def test_15_arquivo_inexistente_falha(self):
        with tempfile.TemporaryDirectory() as pasta:
            class ConfigTemporaria(Config):
                NOME_DO_ARQUIVO = (
                    Path(pasta) / "inexistente.json"
                )
                _instancia = None
                _leituras = 0

            with self.assertRaises(FileNotFoundError):
                ConfigTemporaria.get_instance()

            self.assertIsNone(ConfigTemporaria._instancia)

    def test_16_instancia_retorna_dados_compartilhados(self):
        a = self.primeira()
        b = Config.get_instance()

        self.assertIs(a.dados, b.dados)
        self.assertEqual(Config.quantidade_leituras(), 1)


if __name__ == "__main__":
    unittest.main()
