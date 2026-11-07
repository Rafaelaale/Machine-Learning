"""16 testes automatizados para Singleton por modulo."""

import contextlib
import importlib
import io
import json
import subprocess
import sys
import unittest

from pathlib import Path


BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))


class TestSingletonModulos(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.modulo = importlib.import_module("singleton1_4")

    def test_01_modulo_importado(self):
        self.assertIn("singleton1_4", sys.modules)

    def test_02_modulo_reutilizado(self):
        outro = importlib.import_module("singleton1_4")
        self.assertIs(self.modulo, outro)

    def test_03_mesmo_singleton(self):
        outro = importlib.import_module("singleton1_4")
        self.assertIs(self.modulo.singleton, outro.singleton)

    def test_04_instancia_da_classe(self):
        self.assertIsInstance(
            self.modulo.singleton,
            self.modulo.Singleton
        )

    def test_05_nome_da_instancia(self):
        self.assertEqual(
            self.modulo.singleton.nome,
            "Instancia compartilhada"
        )

    def test_06_dados_sao_dicionario(self):
        self.assertIsInstance(self.modulo.dados, dict)

    def test_07_nome_da_aplicacao(self):
        self.assertEqual(
            self.modulo.dados["aplicacao"],
            "Design Patterns em Python"
        )

    def test_08_ambiente(self):
        self.assertEqual(
            self.modulo.dados["ambiente"],
            "desenvolvimento"
        )

    def test_09_versao(self):
        self.assertEqual(self.modulo.dados["versao"], "1.0")

    def test_10_recurso_singleton_ativo(self):
        self.assertTrue(
            self.modulo.dados["recursos"]["singleton"]
        )

    def test_11_arquivo_configuracao_existe(self):
        self.assertTrue(
            self.modulo.NOME_ARQUIVO.is_file()
        )

    def test_12_json_corresponde_ao_modulo(self):
        with open(
            self.modulo.NOME_ARQUIVO,
            "r",
            encoding="utf-8",
        ) as arquivo:
            esperado = json.load(arquivo)

        self.assertEqual(self.modulo.dados, esperado)

    def test_13_importacao_repetida_silenciosa(self):
        saida = io.StringIO()

        with contextlib.redirect_stdout(saida):
            importlib.import_module("singleton1_4")
            importlib.import_module("singleton1_4")

        self.assertEqual(saida.getvalue(), "")

    def test_14_mesmas_configuracoes_importadas(self):
        from singleton1_4 import dados
        from singleton1_4 import dados as dados_novamente

        self.assertIs(dados, dados_novamente)

    def test_15_uma_criacao_em_processo_novo(self):
        comando = (
            "import singleton1_4; "
            "import singleton1_4; "
            "from singleton1_4 import singleton"
        )

        processo = subprocess.run(
            [sys.executable, "-c", comando],
            cwd=str(BASE),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="strict",
            env={
                **__import__("os").environ,
                "PYTHONIOENCODING": "utf-8",
                "PYTHONUTF8": "1",
            },
            check=True,
        )

        self.assertEqual(
            processo.stdout.count("Criando a instância única"),
            1
        )

    def test_16_estado_compartilhado(self):
        primeira = self.modulo.singleton
        segunda = importlib.import_module(
            "singleton1_4"
        ).singleton

        contador_original = primeira.contador

        try:
            primeira.incrementar()

            self.assertEqual(
                segunda.contador,
                contador_original + 1
            )
        finally:
            primeira.contador = contador_original


if __name__ == "__main__":
    unittest.main()
