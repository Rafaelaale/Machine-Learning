"""16 testes da Aula 21 - Decorando classes."""

import contextlib
import io
import inspect
import sys
import unittest
from pathlib import Path


RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from src.aula21_decorando_classes import (
    singleton,
    Configuracao,
    registry,
    registrar,
    PagamentoPix,
    PagamentoCartao,
    demonstrar_singleton,
    demonstrar_registry,
    analisar_aula21,
)


class TestDecorandoClasses(unittest.TestCase):

    def capturar(self, funcao, *args, **kwargs):
        saida = io.StringIO()

        with contextlib.redirect_stdout(saida):
            resultado = funcao(*args, **kwargs)

        return resultado, saida.getvalue()

    def test_01_singleton_retorna_mesma_instancia(self):
        @singleton
        class Exemplo:
            pass

        primeiro = Exemplo()
        segundo = Exemplo()

        self.assertIs(primeiro, segundo)

    def test_02_singleton_executa_init_uma_vez(self):
        chamadas = []

        @singleton
        class Exemplo:
            def __init__(self):
                chamadas.append("init")

        Exemplo()
        Exemplo()
        Exemplo()

        self.assertEqual(chamadas, ["init"])

    def test_03_configuracao_possui_valor_42(self):
        config, _ = self.capturar(Configuracao)

        self.assertEqual(config.valor, 42)

    def test_04_configuracao_eh_mesmo_objeto(self):
        primeiro, _ = self.capturar(Configuracao)
        segundo, _ = self.capturar(Configuracao)
        terceiro, _ = self.capturar(Configuracao)

        self.assertIs(primeiro, segundo)
        self.assertIs(segundo, terceiro)

    def test_05_wraps_preserva_nome_da_classe(self):
        self.assertEqual(
            Configuracao.__name__,
            "Configuracao",
        )

    def test_06_wraps_preserva_classe_original(self):
        original = Configuracao.__wrapped__

        self.assertTrue(inspect.isclass(original))

        self.assertEqual(
            original.__name__,
            "Configuracao",
        )

    def test_07_wrapper_nao_eh_classe(self):
        self.assertTrue(callable(Configuracao))
        self.assertFalse(
            isinstance(Configuracao, type)
        )

    def test_08_instancia_eh_da_classe_original(self):
        instancia, _ = self.capturar(Configuracao)

        self.assertIsInstance(
            instancia,
            Configuracao.__wrapped__,
        )

    def test_09_singletons_de_classes_diferentes(self):
        @singleton
        class ClasseA:
            pass

        @singleton
        class ClasseB:
            pass

        primeiro = ClasseA()
        segundo = ClasseB()

        self.assertIsNot(primeiro, segundo)

        self.assertIs(primeiro, ClasseA())
        self.assertIs(segundo, ClasseB())

    def test_10_argumentos_so_na_primeira_criacao(self):
        @singleton
        class Config:
            def __init__(self, valor):
                self.valor = valor

        primeira = Config(10)
        segunda = Config(20)

        self.assertIs(primeira, segunda)
        self.assertEqual(segunda.valor, 10)

    def test_11_registry_possui_pix_e_cartao(self):
        self.assertIn("pix", registry)
        self.assertIn("cartao", registry)

        self.assertIs(
            registry["pix"],
            PagamentoPix,
        )

        self.assertIs(
            registry["cartao"],
            PagamentoCartao,
        )

    def test_12_registry_retorna_classes(self):
        self.assertTrue(
            inspect.isclass(registry["pix"])
        )

        self.assertTrue(
            inspect.isclass(registry["cartao"])
        )

        self.assertIsInstance(
            registry["pix"](),
            PagamentoPix,
        )

    def test_13_decorator_registrar_retorna_classe(self):
        @registrar("teste_aula21_temporario")
        class ClasseTemporaria:
            pass

        try:
            self.assertIs(
                registry["teste_aula21_temporario"],
                ClasseTemporaria,
            )
            self.assertIsInstance(
                registry["teste_aula21_temporario"](),
                ClasseTemporaria,
            )
        finally:
            registry.pop("teste_aula21_temporario", None)

    def test_14_chave_duplicada_sobrescreve(self):
        chave = "teste_aula21_duplicado"

        @registrar(chave)
        class Primeira:
            pass

        try:
            self.assertIs(registry[chave], Primeira)

            @registrar(chave)
            class Segunda:
                pass

            self.assertIs(registry[chave], Segunda)
            self.assertIsNot(Primeira, Segunda)
        finally:
            registry.pop(chave, None)

    def test_15_closure_preserva_instancia(self):
        @singleton
        class ClasseLocal:
            pass

        primeiro = ClasseLocal()

        self.assertIs(
            ClasseLocal(),
            primeiro,
        )

        self.assertTrue(
            callable(ClasseLocal)
        )
        self.assertEqual(
            ClasseLocal.__name__,
            "ClasseLocal",
        )

    def test_16_demonstracoes_e_analise(self):
        resultado_singleton, _ = self.capturar(
            demonstrar_singleton
        )
        resultado_registry = demonstrar_registry()
        analise = analisar_aula21()

        self.assertTrue(
            resultado_singleton["mesma_instancia"]
        )

        self.assertEqual(
            resultado_singleton["valor"],
            42,
        )

        self.assertEqual(
            resultado_registry["chaves"],
            ["cartao", "pix"],
        )

        self.assertEqual(analise["aula"], 21)

        self.assertTrue(
            analise["singleton_com_nonlocal"]
        )

        self.assertTrue(
            analise["registry_com_decorator"]
        )

        self.assertFalse(
            analise["singleton_thread_safe"]
        )


if __name__ == "__main__":
    unittest.main()
