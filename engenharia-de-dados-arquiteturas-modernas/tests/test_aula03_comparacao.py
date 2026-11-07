"""Testes da Aula 03 sobre comparacao OLTP/OLAP."""

import sys
import tempfile
import unittest
from pathlib import Path


BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from src.aula03_comparador_oltp_olap import (
    CENARIOS,
    apurar_origem,
    classificar_pergunta,
    comparar_totais,
    consultar_analise,
    consultar_operacao,
    medir_execucao,
)
from src.minishop_oltp import criar_banco, registrar_compra
from src.minishop_olap import carregar_olap


class TestComparacao(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        raiz = Path(self.temp.name)
        self.oltp = raiz / "operacional.db"
        self.olap = raiz / "analitico.db"
        criar_banco(self.oltp)

    def tearDown(self):
        self.temp.cleanup()

    def comprar(self):
        return registrar_compra(
            self.oltp, 1, [(1, 1), (2, 2)]
        )

    def test_01_classificacao_oltp(self):
        self.assertEqual(
            classificar_pergunta("consultar_pedido"),
            "OLTP",
        )

    def test_02_classificacao_olap(self):
        self.assertEqual(
            classificar_pergunta("faturamento_mensal"),
            "OLAP",
        )

    def test_03_todas_operacoes_classificadas(self):
        self.assertEqual(len(CENARIOS), 8)
        self.assertTrue(
            all(
                classificar_pergunta(chave) in {"OLTP", "OLAP"}
                for chave in CENARIOS
            )
        )

    def test_04_operacao_desconhecida(self):
        with self.assertRaises(ValueError):
            classificar_pergunta("operacao_inexistente")

    def test_05_consulta_pontual(self):
        compra = self.comprar()

        pedido = consultar_operacao(
            self.oltp, compra["pedido_id"]
        )

        self.assertEqual(pedido["total_centavos"], 31000)
        self.assertEqual(pedido["status"], "confirmado")

    def test_06_pedido_ausente(self):
        self.assertIsNone(
            consultar_operacao(self.oltp, 999)
        )

    def test_07_consulta_agregada(self):
        self.comprar()
        carregar_olap(self.oltp, self.olap)

        resumo = consultar_analise(self.olap)

        self.assertEqual(
            resumo["indicadores"]["faturamento_centavos"],
            31000,
        )
        self.assertEqual(len(resumo["produtos"]), 2)

    def test_08_reconciliacao_aprovada(self):
        self.comprar()
        carregar_olap(self.oltp, self.olap)

        self.assertTrue(
            comparar_totais(self.oltp, self.olap)[
                "reconciliado"
            ]
        )

    def test_09_fotografia_desatualizada(self):
        self.comprar()
        carregar_olap(self.oltp, self.olap)

        registrar_compra(self.oltp, 2, [(3, 1)])

        resultado = comparar_totais(
            self.oltp, self.olap
        )

        self.assertFalse(resultado["reconciliado"])
        self.assertEqual(
            resultado["oltp"]["faturamento_centavos"],
            121000,
        )
        self.assertEqual(
            resultado["olap"]["faturamento_centavos"],
            31000,
        )

    def test_10_atualizacao_reconcilia(self):
        self.comprar()
        carregar_olap(self.oltp, self.olap)

        registrar_compra(self.oltp, 2, [(3, 1)])
        carregar_olap(self.oltp, self.olap)

        resultado = comparar_totais(
            self.oltp, self.olap
        )

        self.assertTrue(resultado["reconciliado"])
        self.assertEqual(resultado["olap"]["pedidos"], 2)

    def test_11_medicao_de_execucao(self):
        medida = medir_execucao(lambda: 42)

        self.assertEqual(medida["resultado"], 42)
        self.assertGreaterEqual(medida["duracao_ms"], 0)

    def test_12_origem_vazia(self):
        resultado = apurar_origem(self.oltp)

        self.assertEqual(resultado["pedidos"], 0)
        self.assertEqual(
            resultado["faturamento_centavos"], 0
        )


if __name__ == "__main__":
    unittest.main()
