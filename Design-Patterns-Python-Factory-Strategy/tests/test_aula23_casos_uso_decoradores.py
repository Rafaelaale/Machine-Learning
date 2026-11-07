"""16 testes da Aula 23 - Casos de uso de decoradores."""

import contextlib
import io
import sys
import unittest
from dataclasses import fields, is_dataclass
from datetime import datetime
from pathlib import Path


RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from src.aula23_casos_uso_decoradores import (
    app,
    listar,
    Usuario,
    Pessoa,
    Math,
    multiplicar,
    demonstrar_fastapi,
    demonstrar_nativos,
    demonstrar_cache,
    analisar_aula23,
)


class TestCasosUsoDecoradores(unittest.TestCase):

    def test_01_fastapi_e_aplicacao(self):
        from fastapi import FastAPI
        self.assertIsInstance(app, FastAPI)

    def test_02_rota_get_users_registrada(self):
        rotas = [
            rota for rota in app.routes
            if getattr(rota, "path", None) == "/users"
            and "GET" in getattr(rota, "methods", set())
        ]
        self.assertEqual(len(rotas), 1)

    def test_03_endpoint_retorna_usuario(self):
        self.assertEqual(
            listar(),
            [{"id": 1, "nome": "Maria"}],
        )

    def test_04_rota_aponta_para_endpoint(self):
        rota = demonstrar_fastapi()
        self.assertEqual(rota["endpoint"], "listar")
        self.assertEqual(rota["metodo"], "GET")

    def test_05_usuario_e_dataclass(self):
        self.assertTrue(is_dataclass(Usuario))
        self.assertEqual(
            [campo.name for campo in fields(Usuario)],
            ["nome", "idade"],
        )

    def test_06_dataclass_cria_instancia(self):
        usuario = Usuario("Maria", 30)
        self.assertEqual(usuario.nome, "Maria")
        self.assertEqual(usuario.idade, 30)

    def test_07_dataclass_compara_valores(self):
        self.assertEqual(
            Usuario("Maria", 30),
            Usuario("Maria", 30),
        )
        self.assertNotEqual(
            Usuario("Maria", 30),
            Usuario("Ana", 30),
        )

    def test_08_property_ano_nascimento(self):
        pessoa = Pessoa("Ana", 25)
        self.assertEqual(
            pessoa.ano_nascimento,
            datetime.now().year - 25,
        )

    def test_09_property_sem_parenteses(self):
        pessoa = Pessoa("Ana", 25)
        self.assertIsInstance(pessoa.ano_nascimento, int)
        self.assertIsInstance(
            Pessoa.__dict__["ano_nascimento"],
            property,
        )

    def test_10_staticmethod_dobro(self):
        self.assertEqual(Math.dobro(5), 10)
        self.assertEqual(Math.dobro(-3), -6)

    def test_11_classmethod_cria_instancia(self):
        objeto = Math.criar()
        self.assertIsInstance(objeto, Math)

    def test_12_cache_reutiliza_resultado(self):
        multiplicar.cache_clear()
        saida = io.StringIO()
        with contextlib.redirect_stdout(saida):
            primeiro = multiplicar(2, 3)
            segundo = multiplicar(2, 3)
        self.assertEqual((primeiro, segundo), (6, 6))
        self.assertEqual(
            saida.getvalue().count("Calculando"),
            1,
        )

    def test_13_cache_registra_hits_e_misses(self):
        multiplicar.cache_clear()
        with contextlib.redirect_stdout(io.StringIO()):
            multiplicar(2, 3)
            multiplicar(2, 3)
            multiplicar(4, 5)
        info = multiplicar.cache_info()
        self.assertEqual(info.hits, 1)
        self.assertEqual(info.misses, 2)

    def test_14_cache_limite_32(self):
        multiplicar.cache_clear()
        with contextlib.redirect_stdout(io.StringIO()):
            for numero in range(40):
                multiplicar(numero, 2)
        info = multiplicar.cache_info()
        self.assertEqual(info.maxsize, 32)
        self.assertEqual(info.currsize, 32)

    def test_15_exemplos_frameworks_validos(self):
        arquivos = [
            "aula23_flask.py",
            "aula23_click.py",
            "aula23_django.py",
            "aula23_celery.py",
        ]
        for nome in arquivos:
            caminho = RAIZ / "exemplos" / nome
            self.assertTrue(caminho.is_file())
            codigo = caminho.read_text(encoding="utf-8")
            compile(codigo, str(caminho), "exec")

    def test_16_laboratorio_e_analise(self):
        nativos = demonstrar_nativos()
        saida = io.StringIO()
        with contextlib.redirect_stdout(saida):
            cache = demonstrar_cache()
        analise = analisar_aula23()

        self.assertEqual(nativos["dataclass"]["nome"], "Maria")
        self.assertEqual(
            nativos["staticmethod"]["dobro_de_5"],
            10,
        )
        self.assertEqual(cache["resultados"], [6, 6, 20, 20, 20])
        self.assertEqual(cache["hits"], 3)
        self.assertEqual(cache["misses"], 2)
        self.assertEqual(analise["aula"], 23)
        self.assertEqual(analise["cache_maxsize"], 32)


if __name__ == "__main__":
    unittest.main()
