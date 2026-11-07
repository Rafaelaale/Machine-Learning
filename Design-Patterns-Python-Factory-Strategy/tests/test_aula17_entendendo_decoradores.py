"""16 testes da Aula 17 - Decorator."""

import contextlib
import io
import sys
import unittest
from pathlib import Path


RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from src.aula17_entendendo_decoradores import (
    somar,
    dividir,
    somar_com_log,
    somar_com_log_2,
    dividir_com_log,
    adicionar_log,
    soma_com_log2,
    dividir_com_log2,
    analisar_decorator,
)


class TestDecorator(unittest.TestCase):

    def executar(self, funcao, *args):
        saida = io.StringIO()

        with contextlib.redirect_stdout(saida):
            resultado = funcao(*args)

        return resultado, saida.getvalue().strip()

    def test_01_soma_original(self):
        self.assertEqual(somar(3, 5), 8)

    def test_02_divisao_original(self):
        self.assertEqual(dividir(10, 2), 5.0)

    def test_03_soma_original_sem_log(self):
        resultado, log = self.executar(somar, 3, 5)
        self.assertEqual(resultado, 8)
        self.assertEqual(log, "")

    def test_04_divisao_original_sem_log(self):
        resultado, log = self.executar(dividir, 10, 2)
        self.assertEqual(resultado, 5.0)
        self.assertEqual(log, "")

    def test_05_soma_log_manual(self):
        resultado, log = self.executar(somar_com_log, 3, 5)
        self.assertEqual(resultado, 8)
        self.assertEqual(log, "Somando 3 + 5 = 8")

    def test_06_soma_log_manual_2(self):
        resultado, log = self.executar(somar_com_log_2, 3, 5)
        self.assertEqual(resultado, 8)
        self.assertEqual(log, "Somando 3 + 5 = 8")

    def test_07_divisao_log_manual(self):
        resultado, log = self.executar(dividir_com_log, 10, 2)
        self.assertEqual(resultado, 5.0)
        self.assertEqual(log, "Dividindo 10 / 2 = 5.0")

    def test_08_decorator_retorna_funcao(self):
        funcao = adicionar_log(somar)
        self.assertTrue(callable(funcao))

    def test_09_soma_decorada(self):
        resultado, log = self.executar(soma_com_log2, 3, 5)
        self.assertEqual(resultado, 8)
        self.assertEqual(log, "Executando somar(3, 5) = 8")

    def test_10_divisao_decorada(self):
        resultado, log = self.executar(dividir_com_log2, 10, 2)
        self.assertEqual(resultado, 5.0)
        self.assertEqual(log, "Executando dividir(10, 2) = 5.0")

    def test_11_decorator_dinamico(self):
        funcao = adicionar_log(somar)
        resultado, log = self.executar(funcao, 7, 8)
        self.assertEqual(resultado, 15)
        self.assertEqual(log, "Executando somar(7, 8) = 15")

    def test_12_decorator_com_outra_funcao(self):
        def multiplicar(a, b):
            return a * b

        funcao = adicionar_log(multiplicar)
        resultado, log = self.executar(funcao, 4, 6)

        self.assertEqual(resultado, 24)
        self.assertEqual(
            log,
            "Executando multiplicar(4, 6) = 24",
        )

    def test_13_funcoes_decoradas_independentes(self):
        soma, log_soma = self.executar(soma_com_log2, 2, 3)
        divisao, log_divisao = self.executar(
            dividir_com_log2, 8, 2
        )

        self.assertEqual(soma, 5)
        self.assertEqual(divisao, 4.0)
        self.assertIn("somar", log_soma)
        self.assertIn("dividir", log_divisao)

    def test_14_excecao_propagada(self):
        funcao = adicionar_log(dividir)

        with self.assertRaises(ZeroDivisionError):
            funcao(10, 0)

    def test_15_nome_do_wrapper(self):
        self.assertEqual(soma_com_log2.__name__, "wrapper")
        self.assertEqual(dividir_com_log2.__name__, "wrapper")
        self.assertEqual(somar.__name__, "somar")

    def test_16_analise(self):
        analise = analisar_decorator()

        self.assertEqual(analise["aula"], 17)
        self.assertEqual(analise["padrao"], "Decorator")
        self.assertTrue(analise["adiciona_log"])
        self.assertTrue(analise["preserva_resultado"])
        self.assertFalse(analise["modifica_funcoes_originais"])
        self.assertFalse(analise["sintaxe_arroba"])
        self.assertFalse(analise["functools_wraps"])


if __name__ == "__main__":
    unittest.main()
