"""16 testes da Aula 22 - Decoradores com classes."""

import contextlib
import io
import sys
import unittest
from pathlib import Path


RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from src.aula22_decoradores_com_classes import (
    ComLog,
    Repetir,
    somar,
    imprime,
    somar_original,
    imprime_original,
    demonstrar_aplicacao_manual,
    analisar_aula22,
)


class TestDecoradoresComClasses(unittest.TestCase):

    def capturar(self, funcao, *args, **kwargs):
        saida = io.StringIO()

        with contextlib.redirect_stdout(saida):
            resultado = funcao(*args, **kwargs)

        return resultado, saida.getvalue().splitlines()

    def test_01_comlog_e_classe(self):
        self.assertTrue(isinstance(ComLog, type))

    def test_02_comlog_guarda_funcao_original(self):
        self.assertIsInstance(somar, ComLog)
        self.assertEqual(somar.func.__name__, "somar")

    def test_03_comlog_e_callable(self):
        self.assertTrue(callable(somar))

    def test_04_comlog_retorna_soma(self):
        resultado, _ = self.capturar(somar, 3, 5)
        self.assertEqual(resultado, 8)

    def test_05_comlog_imprime_log_inicial(self):
        _, linhas = self.capturar(somar, 3, 5)

        self.assertEqual(
            linhas[0],
            "Executando somar (3, 5)",
        )

    def test_06_comlog_imprime_resultado(self):
        _, linhas = self.capturar(somar, 3, 5)

        self.assertEqual(
            linhas[1],
            "Resultado: 8",
        )

    def test_07_comlog_aceita_outra_funcao(self):
        def multiplicar(a, b):
            return a * b

        decorada = ComLog(multiplicar)

        resultado, linhas = self.capturar(
            decorada, 4, 6
        )

        self.assertEqual(resultado, 24)
        self.assertEqual(
            linhas,
            [
                "Executando multiplicar (4, 6)",
                "Resultado: 24",
            ],
        )

    def test_08_comlog_manual_equivale_arroba(self):
        manual = ComLog(somar_original)

        resultado, linhas = self.capturar(
            manual, 3, 5
        )

        self.assertEqual(resultado, 8)
        self.assertEqual(
            linhas,
            [
                "Executando somar_original (3, 5)",
                "Resultado: 8",
            ],
        )

    def test_09_repetir_armazena_quantidade(self):
        decorador = Repetir(5)

        self.assertEqual(decorador.vezes, 5)

    def test_10_repetir_e_callable(self):
        decorador = Repetir(3)

        self.assertTrue(callable(decorador))

    def test_11_repetir_retorna_wrapper(self):
        wrapper = Repetir(3)(imprime_original)

        self.assertTrue(callable(wrapper))
        self.assertEqual(wrapper.__name__, "wrapper")

    def test_12_repetir_executa_cinco_vezes(self):
        resultado, linhas = self.capturar(imprime)

        self.assertIsNone(resultado)
        self.assertEqual(
            linhas,
            [
                f"[{i}] Executando função..."
                for i in range(1, 6)
            ],
        )

    def test_13_repetir_aceita_args_e_kwargs(self):
        chamadas = []

        def funcao(a, *, b):
            chamadas.append((a, b))
            print(a + b)

        decorada = Repetir(3)(funcao)

        resultado, linhas = self.capturar(
            decorada, 2, b=4
        )

        self.assertIsNone(resultado)
        self.assertEqual(
            chamadas,
            [(2, 4), (2, 4), (2, 4)],
        )
        self.assertEqual(
            linhas,
            ["[1] 6", "[2] 6", "[3] 6"],
        )

    def test_14_repetir_zero_vezes(self):
        chamadas = []

        def funcao():
            chamadas.append("executou")

        decorada = Repetir(0)(funcao)

        resultado, linhas = self.capturar(decorada)

        self.assertIsNone(resultado)
        self.assertEqual(chamadas, [])
        self.assertEqual(linhas, [])

    def test_15_comparacao_aplicacao_manual(self):
        exemplos = demonstrar_aplicacao_manual()

        self.assertIsInstance(
            exemplos["soma_manual"],
            ComLog,
        )

        self.assertIsInstance(
            exemplos["repetidor"],
            Repetir,
        )

        resultado, linhas = self.capturar(
            exemplos["imprime_manual"]
        )

        self.assertIsNone(resultado)
        self.assertEqual(len(linhas), 3)

    def test_16_analise_e_preservacao_original(self):
        analise = analisar_aula22()

        self.assertEqual(analise["aula"], 22)
        self.assertEqual(
            analise["metodo_especial"],
            "__call__",
        )

        self.assertTrue(
            analise["comlog_retorna_resultado"]
        )

        self.assertTrue(
            analise["repetir_retorna_wrapper"]
        )

        self.assertFalse(
            analise["repetir_preserva_retorno"]
        )

        self.assertFalse(
            analise["functools_wraps"]
        )

        self.assertEqual(somar_original(2, 3), 5)

        self.assertEqual(
            somar_original.__name__,
            "somar_original",
        )


if __name__ == "__main__":
    unittest.main()
