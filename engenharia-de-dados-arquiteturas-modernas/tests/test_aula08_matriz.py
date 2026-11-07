"""Testes da matriz dimensional da Aula 08."""

import sys
import tempfile
import unittest
from pathlib import Path


BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from src.aula05_modelo_logico import (
    criar_modelo,
    registrar_venda,
)
from src.aula06_data_warehouse import carregar_dw

from src.aula08_matriz_dimensional import (
    DIMENSOES,
    INDICADORES,
    REQUISITOS_PENDENTES,
    consultar_vendas,
    definicao_aging,
    matriz,
    situacao_cruzamento,
    validar_matriz,
)


class TestMatrizDimensional(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        raiz = Path(cls.temp.name)

        cls.oltp = raiz / "operacional.db"
        cls.dw = raiz / "warehouse.db"

        criar_modelo(cls.oltp)
        registrar_venda(cls.oltp, 2)
        carregar_dw(cls.oltp, cls.dw)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_01_seis_indicadores(self):
        self.assertEqual(len(INDICADORES), 6)

    def test_02_dez_dimensoes(self):
        self.assertEqual(len(DIMENSOES), 10)

    def test_03_sessenta_cruzamentos(self):
        self.assertEqual(len(matriz()), 60)

    def test_04_matriz_valida(self):
        self.assertEqual(validar_matriz(), [])

    def test_05_vendas_por_categoria_disponivel(self):
        self.assertEqual(
            situacao_cruzamento(
                "valor_vendido", "categoria"
            ),
            "disponivel",
        )

    def test_06_faixa_etaria_pendente(self):
        self.assertEqual(
            situacao_cruzamento(
                "quantidade", "faixa_etaria"
            ),
            "pendente",
        )

    def test_07_aging_nao_aplicavel_a_quantidade(self):
        self.assertEqual(
            situacao_cruzamento("quantidade", "aging"),
            "nao_aplicavel",
        )

    def test_08_valor_vendido_por_categoria(self):
        resultado = consultar_vendas(
            self.dw, "valor_vendido", "categoria"
        )
        self.assertEqual(resultado[0]["valor"], 30000)

    def test_09_quantidade_por_produto(self):
        resultado = consultar_vendas(
            self.dw, "quantidade", "produto"
        )
        self.assertEqual(resultado[0]["valor"], 2)

    def test_10_preco_medio_ponderado(self):
        resultado = consultar_vendas(
            self.dw, "preco_medio", "produto"
        )
        self.assertEqual(resultado[0]["valor"], 15000)

    def test_11_bloqueia_dado_demografico_ausente(self):
        with self.assertRaises(ValueError):
            consultar_vendas(
                self.dw, "valor_vendido", "cidade"
            )

    def test_12_bloqueia_indicador_financeiro(self):
        with self.assertRaises(ValueError):
            consultar_vendas(
                self.dw, "valor_em_mora", "cliente"
            )

    def test_13_aging_sem_valores_ficticios(self):
        aging = definicao_aging()
        self.assertFalse(aging["implementado"])
        self.assertEqual(len(aging["faixas_dias"]), 4)

    def test_14_requisitos_de_novas_fontes(self):
        campos = {
            item["campo"]
            for item in REQUISITOS_PENDENTES
        }
        self.assertIn("data_nascimento", campos)
        self.assertIn(
            "data_vencimento_fatura", campos
        )
        self.assertIn(
            "promocao_no_momento_da_compra", campos
        )


if __name__ == "__main__":
    unittest.main()
