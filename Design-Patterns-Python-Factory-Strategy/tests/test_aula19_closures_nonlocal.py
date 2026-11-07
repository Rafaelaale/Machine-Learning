"""16 testes da Aula 19 - Decoradores parametrizados."""

import contextlib
import io
import sys
import unittest
from pathlib import Path


RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from src.aula19_closures_nonlocal import (
    repetir,
    limite,
    imprime,
    diz_ola_original,
    diz_ola_repetida,
    say_hello,
    criar_ola_limitado,
    criar_contador,
    analisar_aula19,
)


class TestClosuresNonlocal(unittest.TestCase):

    def capturar(self, funcao, *args, **kwargs):
        saida = io.StringIO()

        with contextlib.redirect_stdout(saida):
            resultado = funcao(*args, **kwargs)

        return resultado, saida.getvalue().splitlines()

    def test_01_repetir_retorna_decorator(self):
        decorator = repetir(5)
        self.assertTrue(callable(decorator))

    def test_02_repetir_retorna_wrapper(self):
        def exemplo():
            return 10

        wrapper = repetir(3)(exemplo)
        self.assertTrue(callable(wrapper))
        self.assertEqual(wrapper.__name__, "wrapper")

    def test_03_repetir_cinco_vezes(self):
        resultado, linhas = self.capturar(imprime)

        self.assertIsNone(resultado)
        self.assertEqual(len(linhas), 5)

        for i, linha in enumerate(linhas, start=1):
            self.assertEqual(
                linha,
                f"[{i}]: Executando função...",
            )

    def test_04_repetir_tres_vezes_manual(self):
        resultado, linhas = self.capturar(
            diz_ola_repetida
        )

        self.assertIsNone(resultado)
        self.assertEqual(
            linhas,
            [
                "[1]: Olá!",
                "[2]: Olá!",
                "[3]: Olá!",
            ],
        )

    def test_05_reutilizacao_do_decorator(self):
        _, linhas = self.capturar(say_hello)

        self.assertEqual(
            linhas,
            [
                "[1]: Hello!",
                "[2]: Hello!",
                "[3]: Hello!",
            ],
        )

    def test_06_repetir_com_argumentos(self):
        chamadas = []

        @repetir(3)
        def registrar(a, b):
            chamadas.append((a, b))

        _, linhas = self.capturar(registrar, 2, 4)

        self.assertEqual(
            chamadas,
            [(2, 4), (2, 4), (2, 4)],
        )
        self.assertEqual(
            linhas,
            ["[1]: [2]: [3]: "],
        )

    def test_07_repetir_com_kwargs(self):
        valores = []

        @repetir(2)
        def executar(*, valor):
            valores.append(valor)
            print(valor)

        _, linhas = self.capturar(
            executar,
            valor="teste",
        )

        self.assertEqual(valores, ["teste", "teste"])
        self.assertEqual(
            linhas,
            ["[1]: teste", "[2]: teste"],
        )

    def test_08_repetir_zero_vezes(self):
        chamadas = []

        @repetir(0)
        def acao():
            chamadas.append("executou")

        resultado, linhas = self.capturar(acao)

        self.assertIsNone(resultado)
        self.assertEqual(chamadas, [])
        self.assertEqual(linhas, [])

    def test_09_closure_guarda_valor_vezes(self):
        chamadas_duas = []
        chamadas_quatro = []

        @repetir(2)
        def dois():
            chamadas_duas.append(1)

        @repetir(4)
        def quatro():
            chamadas_quatro.append(1)

        self.capturar(dois)
        self.capturar(quatro)

        self.assertEqual(len(chamadas_duas), 2)
        self.assertEqual(len(chamadas_quatro), 4)

    def test_10_limite_tres_primeiras_chamadas(self):
        funcao = criar_ola_limitado(3)

        for _ in range(3):
            resultado, linhas = self.capturar(funcao)

            self.assertIsNone(resultado)
            self.assertEqual(linhas, ["Olá!"])

    def test_11_limite_bloqueia_quarta(self):
        funcao = criar_ola_limitado(3)

        for _ in range(3):
            self.capturar(funcao)

        resultado, linhas = self.capturar(funcao)

        self.assertIsNone(resultado)
        self.assertEqual(
            linhas,
            ["Limite de chamadas atingido."],
        )

    def test_12_limite_zero_bloqueia_primeira(self):
        chamadas = []

        @limite(0)
        def acao():
            chamadas.append(1)

        resultado, linhas = self.capturar(acao)

        self.assertIsNone(resultado)
        self.assertEqual(chamadas, [])
        self.assertEqual(
            linhas,
            ["Limite de chamadas atingido."],
        )

    def test_13_limite_preserva_retorno_e_argumentos(self):
        @limite(2)
        def multiplicar(a, *, fator):
            return a * fator

        self.assertEqual(multiplicar(5, fator=3), 15)
        self.assertEqual(multiplicar(4, fator=2), 8)

        resultado, linhas = self.capturar(
            multiplicar,
            7,
            fator=4,
        )

        self.assertIsNone(resultado)
        self.assertEqual(
            linhas,
            ["Limite de chamadas atingido."],
        )

    def test_14_nonlocal_atualiza_contador(self):
        consultar, decrementar = criar_contador(3)

        self.assertEqual(consultar(), 3)
        self.assertEqual(decrementar(), 2)
        self.assertEqual(consultar(), 2)
        self.assertEqual(decrementar(), 1)
        self.assertEqual(consultar(), 1)

    def test_15_closures_independentes(self):
        primeira = criar_ola_limitado(1)
        segunda = criar_ola_limitado(2)

        _, primeira_ok = self.capturar(primeira)
        _, primeira_bloqueada = self.capturar(primeira)
        _, segunda_ok = self.capturar(segunda)

        self.assertEqual(primeira_ok, ["Olá!"])
        self.assertEqual(
            primeira_bloqueada,
            ["Limite de chamadas atingido."],
        )
        self.assertEqual(segunda_ok, ["Olá!"])

    def test_16_metadados_e_analise(self):
        analise = analisar_aula19()

        self.assertEqual(analise["aula"], 19)
        self.assertTrue(
            analise["fabrica_de_decoradores"]
        )
        self.assertTrue(analise["utiliza_closure"])
        self.assertTrue(analise["utiliza_nonlocal"])
        self.assertTrue(analise["utiliza_args_kwargs"])
        self.assertFalse(
            analise["metadados_preservados_por_wraps"]
        )

        # O proximo video abordara metadados.
        self.assertEqual(imprime.__name__, "wrapper")

        # A funcao original nao foi alterada.
        self.assertEqual(
            diz_ola_original.__name__,
            "diz_ola_original",
        )


if __name__ == "__main__":
    unittest.main()
