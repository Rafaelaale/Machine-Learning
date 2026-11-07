"""16 testes da Aula 04 - Singleton Pythonico."""

import contextlib
import io
import json
import sys
import tempfile
import unittest

from pathlib import Path


BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from src.aula04_singleton_pythonico import Singleton


class TestSingletonPythonico(unittest.TestCase):

    def setUp(self):
        # Evita que um teste compartilhe a
        # instancia criada por outro teste.
        Singleton._instancia = None
        Singleton._leituras = 0

    def tearDown(self):
        Singleton._instancia = None
        Singleton._leituras = 0

    def criar(self):
        with contextlib.redirect_stdout(io.StringIO()):
            return Singleton()

    def test_01_instancia_inicial_nula(self):
        self.assertIsNone(Singleton._instancia)

    def test_02_criacao_direta(self):
        instancia = self.criar()
        self.assertIsInstance(instancia, Singleton)

    def test_03_segunda_chamada_mesmo_objeto(self):
        a = self.criar()
        b = Singleton()
        self.assertIs(a, b)

    def test_04_identidades_iguais(self):
        a = self.criar()
        b = Singleton()
        self.assertEqual(id(a), id(b))

    def test_05_chamada_direta_new(self):
        a = self.criar()
        b = Singleton.__new__(Singleton)
        self.assertIs(a, b)

    def test_06_tres_referencias_mesma_instancia(self):
        a = self.criar()
        b = Singleton()
        c = Singleton.__new__(Singleton)

        self.assertIs(a, b)
        self.assertIs(b, c)

    def test_07_uma_leitura(self):
        self.criar()
        Singleton()
        Singleton.__new__(Singleton)

        self.assertEqual(
            Singleton.quantidade_leituras(),
            1,
        )

    def test_08_mensagem_unica(self):
        saida = io.StringIO()

        with contextlib.redirect_stdout(saida):
            Singleton()
            Singleton()
            Singleton.__new__(Singleton)

        self.assertEqual(
            saida.getvalue().count(
                "Criando a instância única"
            ),
            1,
        )

    def test_09_reutilizacao_silenciosa(self):
        self.criar()
        saida = io.StringIO()

        with contextlib.redirect_stdout(saida):
            Singleton()

        self.assertEqual(saida.getvalue(), "")

    def test_10_arquivo_config_existe(self):
        self.assertTrue(
            Singleton.NOME_DO_ARQUIVO.is_file()
        )

    def test_11_configuracao_dicionario(self):
        a = self.criar()
        self.assertIsInstance(a.dados, dict)

    def test_12_conteudo_json_correto(self):
        a = self.criar()

        with open(
            Singleton.NOME_DO_ARQUIVO,
            encoding="utf-8",
        ) as arquivo:
            esperado = json.load(arquivo)

        self.assertEqual(a.dados, esperado)

    def test_13_compartilhamento_dicionario(self):
        a = self.criar()
        b = Singleton()

        self.assertIs(a.dados, b.dados)

    def test_14_atributo_classe_armazena_instancia(self):
        a = self.criar()

        self.assertIs(
            Singleton._instancia,
            a,
        )

    def test_15_new_nao_recarrega_configuracao(self):
        a = self.criar()
        dados_originais = a.dados

        Singleton.__new__(Singleton)

        self.assertIs(a.dados, dados_originais)
        self.assertEqual(
            Singleton.quantidade_leituras(),
            1,
        )

    def test_16_erro_leitura_nao_armazenado(self):
        with tempfile.TemporaryDirectory() as pasta:

            class SingletonTemporario(Singleton):
                NOME_DO_ARQUIVO = (
                    Path(pasta) / "inexistente.json"
                )
                _instancia = None
                _leituras = 0

            with contextlib.redirect_stdout(io.StringIO()):
                with self.assertRaises(FileNotFoundError):
                    SingletonTemporario()

            self.assertIsNone(
                SingletonTemporario._instancia
            )

            self.assertEqual(
                SingletonTemporario.quantidade_leituras(),
                0,
            )


if __name__ == "__main__":
    unittest.main()
