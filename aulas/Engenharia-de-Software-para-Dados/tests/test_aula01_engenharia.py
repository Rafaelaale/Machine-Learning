import sys
import unittest
from pathlib import Path


RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from aulas.aula01_importancia_engenharia import (
    detectar_mudanca,
    verificar_disparidade,
    avaliar_pedido_voz,
)


class TestEngenhariaDados(unittest.TestCase):

    def test_detecta_mudanca(self):
        resultado = detectar_mudanca(0.12, 0.35)
        self.assertTrue(resultado["alerta"])

    def test_aceita_variacao_pequena(self):
        resultado = detectar_mudanca(0.12, 0.13)
        self.assertFalse(resultado["alerta"])

    def test_detecta_disparidade(self):
        resultado = verificar_disparidade(0.80, 0.50)
        self.assertTrue(resultado["investigar"])

    def test_grupos_proximos(self):
        resultado = verificar_disparidade(0.80, 0.78)
        self.assertFalse(resultado["investigar"])

    def test_voz_com_ruido(self):
        resultado = avaliar_pedido_voz(0.55, 0.70)
        self.assertEqual(
            resultado["acao"],
            "SOLICITAR_CONFIRMACAO",
        )

    def test_voz_segura_na_simulacao(self):
        resultado = avaliar_pedido_voz(0.96, 0.10)
        self.assertEqual(
            resultado["acao"],
            "PROSSEGUIR_NA_SIMULACAO",
        )

    def test_confianca_invalida(self):
        with self.assertRaises(ValueError):
            avaliar_pedido_voz(1.5, 0.10)

    def test_ruido_invalido(self):
        with self.assertRaises(ValueError):
            avaliar_pedido_voz(0.90, -0.20)


if __name__ == "__main__":
    unittest.main()