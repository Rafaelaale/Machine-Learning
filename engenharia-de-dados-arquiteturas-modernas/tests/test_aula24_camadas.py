"""16 testes da Aula 24 - Contas a receber."""

import json
import sys
import tempfile
import unittest
from pathlib import Path


BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from src.aula24_exemplo_camadas import (
    executar,
    ler_json,
    arquivo_hash,
    consultar_gold,
    indicadores,
    indicadores_dw,
    validar_manifesto,
    inadimplencia_por_local,
    classificar_aging,
    formato_data,
)


class TestExemploCamadas(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.resultado = executar(
            raiz=Path(cls.temp.name)
        )
        cls.raiz = Path(cls.resultado["raiz"])
        cls.gold = Path(cls.resultado["gold"])

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def registros(self):
        return {
            item["id_fatura"]: item
            for item in consultar_gold(
                self.gold,
                "SELECT * FROM dados",
            )
        }

    def test_01_oltp_criado(self):
        self.assertTrue(
            Path(self.resultado["oltp"]).is_file()
        )

    def test_02_bronze_clientes_json(self):
        clientes = ler_json(
            Path(self.resultado["bronze"]) / "clientes.json"
        )
        self.assertEqual(len(clientes), 2)

    def test_03_bronze_parquet_real(self):
        arquivo = (
            Path(self.resultado["bronze"])
            / "faturas_2026_janeiro.parquet"
        )
        with arquivo.open("rb") as entrada:
            self.assertEqual(entrada.read(4), b"PAR1")
            entrada.seek(-4, 2)
            self.assertEqual(entrada.read(4), b"PAR1")

    def test_04_silver_extrai_cidade(self):
        self.assertEqual(
            self.registros()["FAT001"]["cidade"],
            "Belo Horizonte",
        )

    def test_05_silver_extrai_estado(self):
        self.assertEqual(
            self.registros()["FAT002"]["estado"],
            "SP",
        )

    def test_06_fatura_pago_em_dia(self):
        linha = self.registros()["FAT001"]
        self.assertEqual(linha["status"], "PAGO")
        self.assertEqual(linha["aging"], "Em dia")

    def test_07_fatura_aberta(self):
        linha = self.registros()["FAT002"]
        self.assertEqual(linha["status"], "ABERTO")
        self.assertEqual(linha["saldo_aberto_centavos"], 80000)

    def test_08_fatura_paga_atrasada(self):
        linha = self.registros()["FAT003"]
        self.assertEqual(
            linha["atraso_pagamento_dias"], 8
        )
        self.assertTrue(linha["pago_com_atraso"])

    def test_09_aging_em_31_janeiro(self):
        linha = self.registros()["FAT002"]
        self.assertEqual(
            linha["dias_vencido_referencia"], 16
        )
        self.assertEqual(linha["aging"], "16-30")

    def test_10_inadimplencia_atual(self):
        linhas = self.registros()
        self.assertTrue(
            linhas["FAT002"]["inadimplente_atual"]
        )
        self.assertFalse(
            linhas["FAT003"]["inadimplente_atual"]
        )

    def test_11_totais_financeiros(self):
        totais = indicadores(self.gold)
        self.assertEqual(totais["emitido_centavos"], 230000)
        self.assertEqual(totais["recebido_centavos"], 150000)
        self.assertEqual(totais["vencido_centavos"], 80000)

    def test_12_inadimplencia_por_cidade(self):
        cidades = {
            item["localidade"]: item
            for item in inadimplencia_por_local(
                self.gold, "cidade"
            )
        }
        self.assertEqual(
            cidades["Campinas"]["vencido_centavos"],
            80000,
        )
        self.assertEqual(
            cidades["Belo Horizonte"]["vencido_centavos"],
            0,
        )

    def test_13_dw_dimensional_reconciliado(self):
        dw = indicadores_dw(
            self.resultado["dw"]
        )
        self.assertEqual(dw[0], 3)
        self.assertEqual(dw[1], 230000)
        self.assertEqual(dw[4], 80000)

    def test_14_integridade_bronze_silver_gold(self):
        for camada in ("bronze", "silver", "gold"):
            self.assertTrue(
                validar_manifesto(
                    self.resultado[camada],
                    camada,
                )
            )

    def test_15_idempotencia(self):
        anterior = arquivo_hash(
            self.gold / "contas_receber_gold.parquet"
        )
        executar(raiz=self.raiz.parent)
        posterior = arquivo_hash(
            self.gold / "contas_receber_gold.parquet"
        )
        self.assertEqual(anterior, posterior)

    def test_16_referencia_altera_aging(self):
        # FAT003 ja foi paga em 28/01/2026.
        # Comparamos referencias posteriores a esse pagamento.
        #
        # FAT002:
        # 29/01: 14 dias de atraso -> faixa 0-15.
        # 31/01: 16 dias de atraso -> faixa 16-30.
        #
        # O saldo vencido permanece R$ 800,00.

        outra = executar(
            raiz=Path(self.temp.name),
            referencia="2026-01-29",
        )

        registros_29 = {
            item["id_fatura"]: item
            for item in consultar_gold(
                outra["gold"],
                "SELECT * FROM dados",
            )
        }

        registros_31 = self.registros()

        self.assertEqual(
            registros_29["FAT002"]["dias_vencido_referencia"],
            14,
        )

        self.assertEqual(
            registros_29["FAT002"]["aging"],
            "0-15",
        )

        self.assertEqual(
            registros_31["FAT002"]["dias_vencido_referencia"],
            16,
        )

        self.assertEqual(
            registros_31["FAT002"]["aging"],
            "16-30",
        )

        self.assertEqual(
            outra["indicadores"]["vencido_centavos"],
            80000,
        )

        self.assertEqual(
            self.resultado["indicadores"]["vencido_centavos"],
            80000,
        )

if __name__ == "__main__":
    unittest.main()
