"""16 testes da Aula 18 - Acucar sintatico."""

import contextlib
import io
import sys
import unittest
from pathlib import Path


RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from src.aula17_entendendo_decoradores import adicionar_log

from src.aula18_acucar_sintatico import (
    somar_original,
    dividir_original,
    somar_explicita,
    dividir_explicita,
    somar,
    dividir,
    demonstrar_equivalencia,
    comparar_proxy_decorator,
    analisar_aula18,
)


class TestAcucarSintatico(unittest.TestCase):

    def capturar(self, funcao, *args):
        saida = io.StringIO()

        with contextlib.redirect_stdout(saida):
            resultado = funcao(*args)

        return resultado, saida.getvalue().strip()

    def test_01_soma_original(self):
        self.assertEqual(somar_original(3, 5), 8)

    def test_02_divisao_original(self):
        self.assertEqual(dividir_original(10, 2), 5.0)

    def test_03_soma_explicita(self):
        resultado, log = self.capturar(
            somar_explicita, 3, 5
        )

        self.assertEqual(resultado, 8)
        self.assertEqual(
            log,
            "Executando somar_original(3, 5) = 8",
        )

    def test_04_divisao_explicita(self):
        resultado, log = self.capturar(
            dividir_explicita, 10, 2
        )

        self.assertEqual(resultado, 5.0)
        self.assertEqual(
            log,
            "Executando dividir_original(10, 2) = 5.0",
        )

    def test_05_soma_com_arroba(self):
        resultado, log = self.capturar(
            somar, 3, 5
        )

        self.assertEqual(resultado, 8)
        self.assertEqual(
            log,
            "Executando somar(3, 5) = 8",
        )

    def test_06_divisao_com_arroba(self):
        resultado, log = self.capturar(
            dividir, 10, 2
        )

        self.assertEqual(resultado, 5.0)
        self.assertEqual(
            log,
            "Executando dividir(10, 2) = 5.0",
        )

    def test_07_equivalencia_de_resultados(self):
        explicita, arroba = demonstrar_equivalencia()

        resultado1, _ = self.capturar(
            explicita, 7, 8
        )
        resultado2, _ = self.capturar(
            arroba, 7, 8
        )

        self.assertEqual(resultado1, resultado2)
        self.assertEqual(resultado1, 15)

    def test_08_equivalencia_de_logs(self):
        explicita, arroba = demonstrar_equivalencia()

        _, log1 = self.capturar(explicita, 7, 8)
        _, log2 = self.capturar(arroba, 7, 8)

        self.assertEqual(log1, log2)
        self.assertEqual(
            log1,
            "Executando operacao(7, 8) = 15",
        )

    def test_09_decorator_retorna_wrapper(self):
        self.assertEqual(
            somar.__name__,
            "wrapper",
        )

        self.assertEqual(
            dividir.__name__,
            "wrapper",
        )

    def test_10_original_permanece_sem_log(self):
        resultado, log = self.capturar(
            somar_original, 4, 6
        )

        self.assertEqual(resultado, 10)
        self.assertEqual(log, "")

    def test_11_o_mesmo_decorator_e_reutilizado(self):
        self.assertTrue(callable(adicionar_log))

        explicita, arroba = demonstrar_equivalencia()

        self.assertTrue(callable(explicita))
        self.assertTrue(callable(arroba))

    def test_12_divisao_por_zero_propaga_erro(self):
        with self.assertRaises(ZeroDivisionError):
            dividir(10, 0)

    def test_13_proxy_controla_acesso(self):
        comparacao = comparar_proxy_decorator()

        self.assertEqual(
            comparacao["proxy"]["objetivo"],
            "Controlar acesso a um objeto",
        )

    def test_14_decorator_adiciona_funcionalidades(self):
        comparacao = comparar_proxy_decorator()

        self.assertEqual(
            comparacao["decorator"]["objetivo"],
            "Adicionar funcionalidades",
        )

        self.assertIn(
            "Logs",
            comparacao["decorator"]["exemplos"],
        )

    def test_15_decoracao_com_argumentos_distintos(self):
        resultado, log = self.capturar(
            somar, -2, 7
        )

        self.assertEqual(resultado, 5)
        self.assertEqual(
            log,
            "Executando somar(-2, 7) = 5",
        )

    def test_16_analise_da_aula(self):
        analise = analisar_aula18()

        self.assertEqual(analise["aula"], 18)
        self.assertEqual(analise["padrao"], "Decorator")

        self.assertTrue(
            analise["sintaxe_explicita"]
        )
        self.assertTrue(
            analise["sintaxe_arroba"]
        )
        self.assertTrue(
            analise["equivalencia"]
        )
        self.assertFalse(
            analise["functools_wraps_implementado"]
        )


if __name__ == "__main__":
    unittest.main()
