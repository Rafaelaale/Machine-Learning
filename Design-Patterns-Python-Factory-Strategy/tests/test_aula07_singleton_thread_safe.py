"""16 testes da Aula 07 - Singleton thread-safe."""

import contextlib
import io
import sys
import threading
import unittest
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from src.aula07_singleton_thread_safe import (
    Singleton,
    _lock,
    executar_concorrencia,
    reiniciar_para_testes,
)


class TestSingletonThreadSafe(unittest.TestCase):

    def setUp(self):
        reiniciar_para_testes()

    def tearDown(self):
        reiniciar_para_testes()

    def criar(self):
        with contextlib.redirect_stdout(io.StringIO()):
            return Singleton()

    def concorrencia(self, quantidade):
        with contextlib.redirect_stdout(io.StringIO()):
            return executar_concorrencia(quantidade)

    def test_01_instancia_inicial_nula(self):
        self.assertIsNone(Singleton._instance)

    def test_02_criacao_direta(self):
        objeto = self.criar()
        self.assertIsInstance(objeto, Singleton)

    def test_03_reutiliza_mesmo_objeto(self):
        a = self.criar()
        b = Singleton()
        self.assertIs(a, b)

    def test_04_ids_iguais(self):
        a = self.criar()
        b = Singleton()
        self.assertEqual(id(a), id(b))

    def test_05_criacao_unica(self):
        self.criar()
        Singleton()
        self.assertEqual(
            Singleton.quantidade_criacoes(),
            1,
        )

    def test_06_mensagem_uma_vez(self):
        saida = io.StringIO()

        with contextlib.redirect_stdout(saida):
            Singleton()
            Singleton()
            Singleton()

        self.assertEqual(
            saida.getvalue().count(
                "Criando a instância única"
            ),
            1,
        )

    def test_07_chamada_direta_new(self):
        a = self.criar()
        b = Singleton.__new__(Singleton)
        self.assertIs(a, b)

    def test_08_aceita_argumentos_em_new(self):
        with contextlib.redirect_stdout(io.StringIO()):
            objeto = Singleton.__new__(
                Singleton,
                10,
                exemplo="teste",
            )

        self.assertIsInstance(objeto, Singleton)

    def test_09_lock_existe(self):
        self.assertTrue(
            hasattr(_lock, "acquire")
        )
        self.assertTrue(
            hasattr(_lock, "release")
        )

    def test_10_duas_threads(self):
        resultado = self.concorrencia(2)

        self.assertTrue(resultado["mesma_instancia"])
        self.assertEqual(resultado["criacoes"], 1)

    def test_11_dez_threads(self):
        resultado = self.concorrencia(10)

        self.assertEqual(
            resultado["instancias_distintas"],
            1,
        )

    def test_12_cem_threads(self):
        resultado = self.concorrencia(100)

        self.assertEqual(resultado["threads"], 100)
        self.assertEqual(
            resultado["instancias_distintas"],
            1,
        )

    def test_13_cem_threads_criacao_unica(self):
        resultado = self.concorrencia(100)

        self.assertEqual(resultado["criacoes"], 1)
        self.assertEqual(
            len(resultado["referencias"]),
            100,
        )

    def test_14_todas_referencias_iguais(self):
        resultado = self.concorrencia(50)
        primeiro = resultado["referencias"][0]

        self.assertTrue(all(
            objeto is primeiro
            for objeto in resultado["referencias"]
        ))

    def test_15_reinicializacao_do_laboratorio(self):
        primeiro = self.criar()

        reiniciar_para_testes()

        segundo = self.criar()

        self.assertIsNot(primeiro, segundo)
        self.assertEqual(
            Singleton.quantidade_criacoes(),
            1,
        )

    def test_16_cinco_rodadas_cem_threads(self):
        for _ in range(5):
            reiniciar_para_testes()
            resultado = self.concorrencia(100)

            self.assertEqual(
                resultado["instancias_distintas"],
                1,
            )
            self.assertEqual(
                resultado["criacoes"],
                1,
            )


if __name__ == "__main__":
    unittest.main()
