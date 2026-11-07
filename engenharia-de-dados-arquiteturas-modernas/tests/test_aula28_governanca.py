"""16 testes da Aula 28: catalogo, linhagem e qualidade."""

import copy
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

from src.aula28_governanca_dados import (
    criar_catalogo,
    criar_linhagem,
    caminho_linhagem,
    validar_registros_vendas,
    consultar_vendas_gold,
    verificar_referencias_dw,
    auditar_qualidade,
    assinaturas_origens,
    executar,
)

from src.aula25_lakehouse_minishop import (
    executar as executar_arquitetura,
)


class TestGovernancaDados(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.raiz = Path(cls.temp.name)
        cls.oltp = cls.raiz / "oltp.db"
        cls.lake = cls.raiz / "lake"

        criar_modelo(cls.oltp)
        registrar_venda(cls.oltp, 1)

        cls.arquitetura = executar_arquitetura(
            cls.oltp, cls.lake
        )

        cls.resultado = executar(
            cls.oltp, cls.lake
        )

        cls.gold = Path(
            cls.arquitetura["gold_analitica"]
        )

        cls.dw = Path(
            cls.arquitetura["data_warehouse"]
        )

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def venda_valida(self):
        return consultar_vendas_gold(self.gold)[0]

    def test_01_catalogo_possui_dw(self):
        self.assertIn(
            "fato_vendas",
            self.resultado["catalogo"]
                ["data_warehouse"]["tabelas"],
        )

    def test_02_catalogo_possui_gold(self):
        self.assertIn(
            "vendas_enriquecidas",
            self.resultado["catalogo"]
                ["lakehouse"]["tabelas"],
        )

    def test_03_catalogo_documenta_colunas(self):
        colunas = self.resultado["catalogo"][
            "data_warehouse"
        ]["tabelas"]["fato_vendas"]["colunas"]

        nomes = {coluna["nome"] for coluna in colunas}

        self.assertIn("valor_total_centavos", nomes)
        self.assertIn("sk_cliente", nomes)

    def test_04_catalogo_identifica_chaves(self):
        colunas = self.resultado["catalogo"][
            "data_warehouse"
        ]["tabelas"]["dim_cliente"]["colunas"]

        self.assertTrue(
            any(
                coluna["chave_primaria"]
                for coluna in colunas
            )
        )

    def test_05_catalogo_documenta_metricas(self):
        metricas = self.resultado["catalogo"][
            "camada_semantica"
        ]["metricas"]

        self.assertIn("faturamento", metricas)
        self.assertIn("ticket_medio", metricas)

    def test_06_linhagem_oltp_ate_consumo(self):
        percurso = self.resultado[
            "caminho_faturamento"
        ]

        self.assertEqual(percurso[0], "oltp")
        self.assertEqual(percurso[-1], "consumo")

        # O caminho mais curto pode passar pelo DW.
        self.assertIn("semantica", percurso)

        # Verifica separadamente a rota do Lakehouse.
        rota_gold = caminho_linhagem(
            self.resultado["linhagem"],
            "gold",
            "consumo",
        )

        self.assertEqual(
            rota_gold,
            ["gold", "lakehouse", "semantica", "consumo"],
        )

        # Verifica tambem a rota dimensional.
        rota_dw = caminho_linhagem(
            self.resultado["linhagem"],
            "dw",
            "consumo",
        )

        self.assertEqual(
            rota_dw,
            ["dw", "semantica", "consumo"],
        )

    def test_07_linhagem_silver_para_dw(self):
        percurso = caminho_linhagem(
            self.resultado["linhagem"],
            "silver",
            "dw",
        )

        self.assertEqual(
            percurso,
            ["silver", "dw"],
        )

    def test_08_linhagem_faturamento_documentada(self):
        metrica = self.resultado[
            "linhagem"
        ]["metrica_faturamento"]

        self.assertEqual(
            metrica["regra"],
            "SUM(valor_total_centavos)",
        )

    def test_09_qualidade_dados_validos(self):
        resultado = validar_registros_vendas(
            [self.venda_valida()]
        )

        self.assertTrue(resultado["aprovado"])
        self.assertEqual(resultado["erros"], [])

    def test_10_detecta_duplicidade(self):
        venda = self.venda_valida()

        resultado = validar_registros_vendas(
            [venda, copy.deepcopy(venda)]
        )

        self.assertFalse(resultado["aprovado"])
        self.assertTrue(
            any(
                erro["regra"] == "duplicidade"
                for erro in resultado["erros"]
            )
        )

    def test_11_detecta_valor_negativo(self):
        venda = self.venda_valida()
        venda["valor_total_centavos"] = -1

        resultado = validar_registros_vendas(
            [venda]
        )

        self.assertFalse(resultado["aprovado"])

    def test_12_detecta_campo_ausente(self):
        venda = self.venda_valida()
        del venda["cliente_nome"]

        resultado = validar_registros_vendas(
            [venda]
        )

        self.assertFalse(resultado["aprovado"])

    def test_13_integridade_referencial_dw(self):
        resultado = verificar_referencias_dw(self.dw)

        self.assertTrue(
            resultado["referencias_validas"]
        )
        self.assertTrue(resultado["aprovado"])

    def test_14_reconciliacao_gold_dw(self):
        qualidade = auditar_qualidade(
            self.arquitetura
        )

        self.assertTrue(
            qualidade["reconciliacao"]["iguais"]
        )

        self.assertTrue(
            qualidade["metricas_semanticas"][
                "faturamento_igual"
            ]
        )

    def test_15_consultas_preservam_dados(self):
        antes = assinaturas_origens(
            self.arquitetura
        )

        auditar_qualidade(self.arquitetura)

        depois = assinaturas_origens(
            self.arquitetura
        )

        self.assertEqual(antes, depois)

    def test_16_governanca_integral(self):
        self.assertTrue(
            self.resultado["qualidade"]["aprovado"]
        )

        self.assertTrue(
            self.resultado["dados_preservados"]
        )

        self.assertEqual(
            self.resultado["qualidade"][
                "reconciliacao"
            ]["lakehouse"]["faturamento_centavos"],
            15000,
        )


if __name__ == "__main__":
    unittest.main()
