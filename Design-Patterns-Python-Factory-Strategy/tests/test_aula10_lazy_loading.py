"""16 testes da Aula 10 - Lazy Loading."""

import contextlib
import importlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path


BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from src.aula10_sqlalchemy_lazy import (
    Author,
    Book,
    demonstrar_sqlalchemy,
)


class TestLazyLoading(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.imediato = importlib.import_module(
            "src.aula10_imediato"
        )

        cls.tardio = importlib.import_module(
            "src.aula10_tardio"
        )

        cls.sql = demonstrar_sqlalchemy()

    def test_01_config_json_existe(self):
        self.assertTrue(
            self.imediato.ARQUIVO_CONFIG.is_file()
        )

    def test_02_json_tema_dark(self):
        with self.imediato.ARQUIVO_CONFIG.open(
            encoding="utf-8"
        ) as arquivo:
            dados = json.load(arquivo)

        self.assertEqual(dados["theme"], "dark")

    def test_03_imediato_carrega_no_import(self):
        saida = io.StringIO()

        with contextlib.redirect_stdout(saida):
            mod = importlib.reload(self.imediato)

        self.assertEqual(
            mod.config.leituras,
            1,
        )
        self.assertIn(
            "Lendo arquivo",
            saida.getvalue(),
        )

    def test_04_imediato_tem_dados_prontos(self):
        config = self.imediato.Config()

        self.assertEqual(config.data["theme"], "dark")
        self.assertEqual(config.leituras, 1)

    def test_05_lazy_nao_carrega_ao_criar(self):
        config = self.tardio.Config()

        self.assertIsNone(config._data)
        self.assertEqual(config.leituras, 0)

    def test_06_lazy_property_primeiro_acesso(self):
        config = self.tardio.Config()

        with contextlib.redirect_stdout(io.StringIO()):
            dados = config.data

        self.assertEqual(dados["theme"], "dark")
        self.assertEqual(config.leituras, 1)

    def test_07_lazy_reutiliza_cache(self):
        config = self.tardio.Config()

        with contextlib.redirect_stdout(io.StringIO()):
            primeiro = config.data
            segundo = config.data

        self.assertIs(primeiro, segundo)
        self.assertEqual(config.leituras, 1)

    def test_08_lazy_imprime_uma_vez(self):
        config = self.tardio.Config()
        saida = io.StringIO()

        with contextlib.redirect_stdout(saida):
            config.data
            config.data
            config.data

        self.assertEqual(
            saida.getvalue().count(
                "Lendo arquivo de configuração"
            ),
            1,
        )

    def test_09_lazy_nao_le_arquivo_ausente_ao_criar(self):
        with tempfile.TemporaryDirectory() as pasta:
            ausente = Path(pasta) / "ausente.json"

            config = self.tardio.Config(ausente)

            self.assertEqual(config.leituras, 0)

            with self.assertRaises(FileNotFoundError):
                _ = config.data

            self.assertIsNone(config._data)

    def test_10_lazy_instancias_tem_cache_proprio(self):
        a = self.tardio.Config()
        b = self.tardio.Config()

        with contextlib.redirect_stdout(io.StringIO()):
            _ = a.data

        self.assertEqual(a.leituras, 1)
        self.assertEqual(b.leituras, 0)

    def test_11_sqlalchemy_autor_correto(self):
        self.assertEqual(
            self.sql["autor"],
            "Machado de Assis",
        )

    def test_12_sqlalchemy_dois_livros(self):
        self.assertEqual(
            self.sql["quantidade_livros"],
            2,
        )

        self.assertEqual(
            self.sql["livros"],
            ["Dom Casmurro", "Memórias Póstumas"],
        )

    def test_13_books_ausentes_antes(self):
        self.assertTrue(
            self.sql["books_nao_carregados_antes"]
        )

        self.assertFalse(
            self.sql["books_no_dict_antes"]
        )

    def test_14_books_presentes_depois(self):
        self.assertTrue(
            self.sql["books_carregados_depois"]
        )

        self.assertTrue(
            self.sql["books_no_dict_depois"]
        )

    def test_15_consulta_sql_adicional(self):
        self.assertEqual(
            self.sql["consulta_extra_ao_acessar_books"],
            1,
        )

        self.assertEqual(
            self.sql["consultas_depois_acesso"],
            self.sql["consultas_antes_acesso"] + 1,
        )

    def test_16_segundo_acesso_sem_nova_consulta(self):
        self.assertTrue(
            self.sql["mesma_colecao_reutilizada"]
        )

        self.assertEqual(
            self.sql["consultas_apos_repeticao"],
            self.sql["consultas_depois_acesso"],
        )


if __name__ == "__main__":
    unittest.main()
