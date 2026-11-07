"""16 testes da Aula 05 - Condicao de corrida."""

import sys
import threading
import unittest
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from src.aula04_singleton_pythonico import Singleton
from src.aula05_singleton_threads import (
    N_THREADS,
    SingletonComCorridaControlada,
    executar_threads,
    testar_singleton_original,
    demonstrar_corrida_controlada,
    resumo,
    executar,
)


class TestSingletonThreads(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.real = testar_singleton_original(100)
        cls.controlado = demonstrar_corrida_controlada()

    def test_01_quantidade_threads(self):
        self.assertEqual(N_THREADS, 100)

    def test_02_barreira_compartilhada_funciona(self):
        barreira = threading.Barrier(2)
        self.assertEqual(barreira.parties, 2)

    def test_03_experimento_real_executa(self):
        self.assertEqual(self.real["threads"], 100)

    def test_04_captura_100_referencias(self):
        self.assertEqual(
            len(self.real["objetos"]),
            100,
        )

    def test_05_contagem_real_valida(self):
        self.assertGreaterEqual(
            self.real["instancias_distintas"],
            1,
        )
        self.assertLessEqual(
            self.real["instancias_distintas"],
            100,
        )

    def test_06_ids_correspondem_a_objetos(self):
        self.assertEqual(
            len(self.real["ids"]),
            self.real["instancias_distintas"],
        )

    def test_07_instancias_sao_singleton(self):
        self.assertTrue(all(
            isinstance(objeto, Singleton)
            for objeto in self.real["objetos"]
        ))

    def test_08_experimento_controlado_duas_threads(self):
        self.assertEqual(
            self.controlado["threads"],
            2,
        )

    def test_09_corrida_cria_duas_instancias(self):
        self.assertEqual(
            self.controlado["instancias_distintas"],
            2,
        )

    def test_10_corrida_leitura_duplicada(self):
        self.assertEqual(
            self.controlado["leituras"],
            2,
        )

    def test_11_objetos_controlados_sao_distintos(self):
        a, b = self.controlado["objetos"]
        self.assertIsNot(a, b)

    def test_12_objetos_controlados_tem_json(self):
        for objeto in self.controlado["objetos"]:
            self.assertIsInstance(objeto.dados, dict)
            self.assertIn("aplicacao", objeto.dados)

    def test_13_controle_nao_altera_aula04(self):
        self.assertIsNot(
            SingletonComCorridaControlada,
            Singleton,
        )

    def test_14_resumo_nao_contem_objetos(self):
        dados = resumo(self.controlado)
        self.assertNotIn("objetos", dados)
        self.assertEqual(
            dados["instancias_distintas"],
            2,
        )

    def test_15_rejeita_uma_thread(self):
        with self.assertRaises(ValueError):
            executar_threads(1, Singleton)

    def test_16_laboratorio_completo(self):
        resultado = executar(20)

        self.assertTrue(
            resultado["corrida_demonstrada"]
        )
        self.assertFalse(
            resultado["thread_safe_implementado"]
        )
        self.assertEqual(
            resultado["experimento_controlado"][
                "instancias_distintas"
            ],
            2,
        )


if __name__ == "__main__":
    unittest.main()
