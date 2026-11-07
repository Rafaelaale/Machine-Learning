"""16 testes da Aula 06."""

import logging
import sys
import unittest
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from src.aula06_casos_uso_singleton import (
    verificar_none,
    verificar_booleanos,
    verificar_fluxos,
    verificar_logger,
    verificar_sqlalchemy,
    executar,
)


class TestCasosUsoSingleton(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.none = verificar_none()
        cls.bool = verificar_booleanos()
        cls.fluxos = verificar_fluxos()
        cls.log = verificar_logger()
        cls.sql = verificar_sqlalchemy()

    def test_01_none_unico(self):
        self.assertTrue(self.none["none_is_none"])

    def test_02_none_referencias(self):
        self.assertTrue(self.none["a_is_b"])
        self.assertTrue(self.none["a_is_c"])

    def test_03_true_unico(self):
        self.assertTrue(self.bool["true_unico"])

    def test_04_false_unico(self):
        self.assertTrue(self.bool["false_unico"])

    def test_05_booleanos_diferentes(self):
        self.assertTrue(
            self.bool["true_diferente_false"]
        )

    def test_06_stdin(self):
        self.assertTrue(
            self.fluxos["stdin_reutilizado"]
        )

    def test_07_stdout(self):
        self.assertTrue(
            self.fluxos["stdout_reutilizado"]
        )

    def test_08_stderr(self):
        self.assertTrue(
            self.fluxos["stderr_reutilizado"]
        )

    def test_09_fluxos_disponiveis(self):
        self.assertTrue(
            self.fluxos["fluxos_disponiveis"]
        )

    def test_10_logger_mesmo_objeto(self):
        self.assertTrue(self.log["mesmo_objeto"])

    def test_11_logger_mesmo_id(self):
        self.assertTrue(self.log["mesmo_id"])

    def test_12_logger_mesmo_nome(self):
        a = logging.getLogger("curso.singleton")
        b = logging.getLogger("curso.singleton")
        self.assertIs(a, b)

    def test_13_logger_nomes_diferentes(self):
        a = logging.getLogger("curso.um")
        b = logging.getLogger("curso.dois")
        self.assertIsNot(a, b)

    def test_14_sqlalchemy_mesma_thread(self):
        self.assertTrue(
            self.sql["mesma_thread_mesma_sessao"]
        )

    def test_15_sqlalchemy_outra_thread(self):
        self.assertFalse(
            self.sql["outra_thread_mesma_sessao"]
        )
        self.assertTrue(
            self.sql["remove_cria_nova_sessao"]
        )

    def test_16_laboratorio_completo(self):
        resultado = executar()

        self.assertEqual(resultado["aula"], 6)

        self.assertTrue(
            resultado["logging"]["mesmo_objeto"]
        )

        self.assertEqual(
            resultado["sqlalchemy"]["escopo"],
            "thread-local",
        )


if __name__ == "__main__":
    unittest.main()
