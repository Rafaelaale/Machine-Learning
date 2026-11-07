"""16 testes da Aula 27 - Strategy e Template Method."""

import sys
import unittest
from pathlib import Path


RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from src.aula27_strategy_template_method import (
    lista_de_frutas,
    por_tamanho,
    ordem_alfabetica,
    demonstrar_ordenacao,
    Pessoa,
    demonstrar_comparacoes,
    AUTHENTICATION_BACKENDS,
    SERIALIZADORES_CELERY,
    selecionar_serializador,
    FormularioContatoDidatico,
    demonstrar_formularios,
    analisar_aula27,
)




class TestStrategyTemplateMethod(unittest.TestCase):

    def test_01_lista_original(self):
        self.assertEqual(
            lista_de_frutas,
            ["maçã", "banana", "abacaxi", "laranja", "uva"],
        )

    def test_02_estrategia_por_tamanho(self):
        self.assertEqual(por_tamanho("uva"), 3)
        self.assertEqual(por_tamanho("banana"), 6)
        self.assertEqual(por_tamanho("abacaxi"), 7)

    def test_03_estrategia_alfabetica(self):
        self.assertEqual(
            ordem_alfabetica("maçã"),
            "maçã",
        )

    def test_04_ordenacao_por_tamanho(self):
        resultado = demonstrar_ordenacao()

        self.assertEqual(
            resultado["por_tamanho"],
            sorted(lista_de_frutas, key=len),
        )

    def test_05_ordenacao_alfabetica(self):
        resultado = demonstrar_ordenacao()

        self.assertEqual(
            resultado["alfabetica"],
            sorted(lista_de_frutas),
        )

    def test_06_ordenacao_lambda(self):
        resultado = demonstrar_ordenacao()

        self.assertEqual(
            resultado["por_lambda"],
            sorted(resultado["alfabetica"], key=len),
        )

    def test_07_strategy_com_callable(self):
        frutas = lista_de_frutas.copy()

        def ultima_letra(fruta):
            return fruta[-1]

        frutas.sort(key=ultima_letra)

        self.assertEqual(
            frutas,
            sorted(lista_de_frutas, key=ultima_letra),
        )

    def test_08_pessoa_less_than(self):
        alice = Pessoa("Alice", 30)
        bob = Pessoa("Bob", 25)

        self.assertFalse(alice < bob)
        self.assertTrue(bob < alice)

    def test_09_pessoa_igualdade(self):
        alice = Pessoa("Alice", 30)
        outra = Pessoa("Alice", 30)

        self.assertTrue(alice == outra)

    def test_10_pessoa_diferente(self):
        alice = Pessoa("Alice", 30)

        self.assertFalse(alice == Pessoa("Alice", 31))
        self.assertFalse(alice == Pessoa("Bob", 30))

    def test_11_ordenacao_de_pessoas(self):
        pessoas = [
            Pessoa("Alice", 30),
            Pessoa("Bob", 25),
            Pessoa("Carla", 40),
        ]

        pessoas.sort()

        self.assertEqual(
            [pessoa.nome for pessoa in pessoas],
            ["Bob", "Alice", "Carla"],
        )

    def test_12_backends_django(self):
        self.assertEqual(
            AUTHENTICATION_BACKENDS,
            [
                "django.contrib.auth.backends.ModelBackend",
                "django.contrib.auth.backends.RemoteUserBackend",
            ],
        )

    def test_13_serializadores_celery(self):
        self.assertEqual(
            selecionar_serializador("json"),
            "json",
        )
        self.assertEqual(
            selecionar_serializador("pickle"),
            "pickle",
        )
        self.assertEqual(
            len(SERIALIZADORES_CELERY),
            2,
        )

    def test_14_template_method_formulario_valido(self):
        formulario = FormularioContatoDidatico({
            "nome": "Maria",
            "email": "maria@example.com",
            "mensagem": "Olá!",
        })

        self.assertTrue(formulario.is_valid())
        self.assertEqual(formulario.errors, {})
        self.assertEqual(
            formulario.cleaned_data["email"],
            "maria@example.com",
        )

    def test_15_template_method_formulario_invalido(self):
        formulario = FormularioContatoDidatico({
            "nome": "Maria",
            "email": "maria@outro.com",
            "mensagem": "Olá!",
        })

        self.assertFalse(formulario.is_valid())
        self.assertIn("email", formulario.errors)

        resultado = demonstrar_formularios()

        self.assertTrue(resultado["valido"])
        self.assertFalse(resultado["invalido"])

    def test_16_unittest_setup_e_exemplos(self):
        class TestePreparacao(unittest.TestCase):
            preparacoes = 0

            def setUp(self):
                TestePreparacao.preparacoes += 1
                self.dados = {"nome": "Teste"}

            def test_primeiro(self):
                self.assertEqual(
                    self.dados["nome"],
                    "Teste",
                )

            def test_segundo(self):
                self.assertIn("nome", self.dados)

        suite = unittest.defaultTestLoader.loadTestsFromTestCase(
            TestePreparacao
        )

        resultado = unittest.TestResult()
        suite.run(resultado)

        self.assertTrue(resultado.wasSuccessful())
        self.assertEqual(resultado.testsRun, 2)
        self.assertEqual(TestePreparacao.preparacoes, 2)

        from exemplos.aula27_unittest_setup import (
            TestMinhaFuncionalidade,
        )

        exemplo = TestMinhaFuncionalidade("test_algo")
        resultado_exemplo = unittest.TestResult()
        exemplo.run(resultado_exemplo)

        self.assertTrue(resultado_exemplo.wasSuccessful())

        arquivos = [
            "aula27_django_forms.py",
            "aula27_configuracoes_frameworks.py",
            "aula27_unittest_setup.py",
        ]

        for nome in arquivos:
            caminho = RAIZ / "exemplos" / nome
            self.assertTrue(caminho.is_file())

            compile(
                caminho.read_text(encoding="utf-8"),
                str(caminho),
                "exec",
            )

        analise = analisar_aula27()

        self.assertEqual(analise["aula"], 27)
        self.assertTrue(
            analise["django_exemplo_real_separado"]
        )
        self.assertFalse(analise["pickle_habilitado"])


if __name__ == "__main__":
    unittest.main()
