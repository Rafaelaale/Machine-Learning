"""16 testes da Aula 20 - Metadados e empilhamento."""

import contextlib
import inspect
import io
import sys
import unittest
from pathlib import Path


RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from src.aula20_metadados_empilhamento import (
    adicionar_log,
    adicionar_log_sem_wraps,
    repetir,
    somar_sem_wraps,
    somar,
    dividir,
    somar_empilhada,
    somar_ordem_invertida,
    somar_original,
    demonstrar_ordem_aplicacao,
    demonstrar_metadados,
    analisar_aula20,
)


class TestMetadadosEmpilhamento(unittest.TestCase):

    def capturar(self, funcao, *args):
        saida = io.StringIO()

        with contextlib.redirect_stdout(saida):
            resultado = funcao(*args)

        return resultado, saida.getvalue()

    def test_01_sem_wraps_nome_wrapper(self):
        self.assertEqual(
            somar_sem_wraps.__name__,
            "wrapper",
        )

    def test_02_com_wraps_nome_original(self):
        self.assertEqual(somar.__name__, "somar")

    def test_03_documentacao_preservada(self):
        self.assertEqual(
            somar.__doc__,
            "Soma dois numeros.",
        )

    def test_04_wrapped_aponta_para_original(self):
        self.assertTrue(hasattr(somar, "__wrapped__"))
        self.assertEqual(
            somar.__wrapped__(2, 3),
            5,
        )
        self.assertEqual(
            somar.__wrapped__.__name__,
            "somar",
        )

    def test_05_sem_wraps_nao_possui_wrapped(self):
        self.assertFalse(
            hasattr(somar_sem_wraps, "__wrapped__")
        )

    def test_06_soma_com_wraps_funciona(self):
        resultado, _ = self.capturar(somar, 2, 3)
        self.assertEqual(resultado, 5)

    def test_07_log_com_wraps_funciona(self):
        _, saida = self.capturar(somar, 2, 3)

        self.assertEqual(
            saida,
            "Executando somar(2, 3) = 5\n",
        )

    def test_08_divisao_com_wraps(self):
        resultado, saida = self.capturar(
            dividir, 10, 2
        )

        self.assertEqual(resultado, 5.0)
        self.assertEqual(dividir.__name__, "dividir")
        self.assertIn(
            "Executando dividir(10, 2) = 5.0",
            saida,
        )

    def test_09_empilhamento_repete_tres_vezes(self):
        resultado, saida = self.capturar(
            somar_empilhada, 2, 3
        )

        self.assertIsNone(resultado)
        self.assertEqual(
            saida.count(
                "Executando somar_empilhada(2, 3) = 5"
            ),
            3,
        )

    def test_10_empilhamento_indica_ordem(self):
        _, saida = self.capturar(
            somar_empilhada, 2, 3
        )

        self.assertIn("[1]: Executando", saida)
        self.assertIn("[2]: Executando", saida)
        self.assertIn("[3]: Executando", saida)

    def test_11_ordem_invertida_altera_comportamento(self):
        resultado, saida = self.capturar(
            somar_ordem_invertida, 2, 3
        )

        self.assertIsNone(resultado)

        self.assertEqual(
            saida.count(
                "Executando wrapper(2, 3) = None"
            ),
            1,
        )

        self.assertEqual(
            saida.count("["),
            3,
        )

    def test_12_aplicacao_manual_empilhamento(self):
        funcao = demonstrar_ordem_aplicacao()

        resultado, saida = self.capturar(
            funcao, 2, 3
        )

        self.assertIsNone(resultado)

        self.assertEqual(
            saida.count(
                "Executando operacao(2, 3) = 5"
            ),
            3,
        )

    def test_13_funcao_original_nao_modificada(self):
        resultado, saida = self.capturar(
            somar_original, 2, 3
        )

        self.assertEqual(resultado, 5)
        self.assertEqual(saida, "")

    def test_14_metadados_com_inspect_unwrap(self):
        original = inspect.unwrap(somar)

        self.assertIs(
            original,
            somar.__wrapped__,
        )

        self.assertEqual(
            original.__name__,
            "somar",
        )

        # Repetir ainda nao utiliza wraps.
        self.assertEqual(
            somar_empilhada.__name__,
            "wrapper",
        )

    def test_15_excecoes_sao_propagadas(self):
        with self.assertRaises(ZeroDivisionError):
            dividir(10, 0)

        def falhar(a, b):
            raise RuntimeError("erro esperado")

        decorada = adicionar_log(falhar)

        with self.assertRaisesRegex(
            RuntimeError, "erro esperado"
        ):
            decorada(1, 2)

    def test_16_relatorio_e_analise(self):
        metadados = demonstrar_metadados()
        analise = analisar_aula20()

        self.assertEqual(
            metadados["sem_wraps"]["nome"],
            "wrapper",
        )

        self.assertEqual(
            metadados["com_wraps"]["nome"],
            "somar",
        )

        self.assertTrue(
            metadados["com_wraps"]["possui_wrapped"]
        )

        self.assertEqual(analise["aula"], 20)
        self.assertTrue(analise["functools_wraps"])
        self.assertTrue(analise["empilhamento"])

        self.assertFalse(
            analise[
                "decorator_repetir_preserva_retorno"
            ]
        )

        self.assertFalse(
            analise["decorators_com_classes"]
        )


if __name__ == "__main__":
    unittest.main()
