"""16 testes da Aula 18 - Arquitetura do Data Lake."""

import json
import shutil
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

from src.aula17_data_lake import (
    validar_snapshot,
    hash_arquivo,
    ingerir,
)

from src.aula18_arquitetura_data_lake import (
    executar_arquitetura,
    criar_silver,
    criar_gold,
    ler_silver,
    validar_camada,
    validar_venda,
    indicadores_gold,
)


class TestArquiteturaDataLake(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()

        raiz = Path(self.temp.name)

        self.oltp = raiz / "oltp.db"
        self.lake = raiz / "lake"

        criar_modelo(self.oltp)
        registrar_venda(self.oltp, 1)

        self.resultado = executar_arquitetura(
            self.oltp, self.lake
        )

        self.bronze = Path(
            self.resultado["bronze"]["pasta"]
        )
        self.silver = Path(
            self.resultado["silver"]["pasta"]
        )
        self.gold = Path(
            self.resultado["gold"]["pasta"]
        )

    def tearDown(self):
        self.temp.cleanup()

    def test_01_bronze_existe(self):
        self.assertTrue(
            (self.bronze / "oltp.sqlite").is_file()
        )

    def test_02_bronze_valida(self):
        self.assertTrue(
            validar_snapshot(self.bronze)
        )

    def test_03_silver_existe(self):
        self.assertTrue(
            (
                self.silver
                / "vendas_padronizadas.jsonl"
            ).is_file()
        )

    def test_04_gold_existe(self):
        self.assertTrue(
            (
                self.gold
                / "resumo.json"
            ).is_file()
        )

    def test_05_silver_integridade(self):
        manifesto = validar_camada(
            self.silver, "silver"
        )

        self.assertEqual(
            manifesto["camada"], "silver"
        )

    def test_06_gold_integridade(self):
        manifesto = validar_camada(
            self.gold, "gold"
        )

        self.assertEqual(
            manifesto["camada"], "gold"
        )

    def test_07_schema_on_read(self):
        registros = ler_silver(
            self.silver
        )

        self.assertEqual(len(registros), 1)
        self.assertEqual(
            registros[0]["quantidade"], 1
        )

    def test_08_rejeita_valor_inconsistente(self):
        registro = ler_silver(
            self.silver
        )[0]

        registro["valor_centavos"] = 1

        with self.assertRaises(ValueError):
            validar_venda(registro)

    def test_09_receita_gold(self):
        resumo = self.resultado[
            "gold"
        ]["resumo"]

        self.assertEqual(
            resumo["faturamento_centavos"],
            15000,
        )

    def test_10_quantidade_gold(self):
        resumo = self.resultado[
            "gold"
        ]["resumo"]

        self.assertEqual(
            resumo["unidades"], 1
        )

    def test_11_agregacao_diaria(self):
        vendas = ler_silver(
            self.silver
        )

        _, diarios, _ = indicadores_gold(
            vendas
        )

        self.assertEqual(len(diarios), 1)
        self.assertEqual(
            diarios[0]["faturamento_centavos"],
            15000,
        )

    def test_12_agregacao_produto(self):
        vendas = ler_silver(
            self.silver
        )

        _, _, produtos = indicadores_gold(
            vendas
        )

        self.assertEqual(len(produtos), 1)
        self.assertEqual(
            produtos[0]["produto"], "Teclado"
        )

    def test_13_reexecucao_sem_duplicar(self):
        segunda = executar_arquitetura(
            self.oltp, self.lake
        )

        self.assertFalse(
            segunda["bronze"]["novo"]
        )
        self.assertFalse(
            segunda["silver"]["novo"]
        )
        self.assertFalse(
            segunda["gold"]["novo"]
        )

    def test_14_preserva_bronze(self):
        antes = {
            item.name: hash_arquivo(item)
            for item in self.bronze.iterdir()
            if item.is_file()
        }

        criar_silver(
            self.bronze, self.lake
        )

        criar_gold(
            self.silver, self.lake
        )

        depois = {
            item.name: hash_arquivo(item)
            for item in self.bronze.iterdir()
            if item.is_file()
        }

        self.assertEqual(antes, depois)

    def test_15_detecta_silver_alterada(self):
        copia = (
            Path(self.temp.name)
            / "silver_corrompida"
        )

        shutil.copytree(
            self.silver, copia
        )

        with open(
            copia / "vendas_padronizadas.jsonl",
            "a",
            encoding="utf-8",
        ) as arquivo:
            arquivo.write(
                '{"alterado": true}\n'
            )

        with self.assertRaises(ValueError):
            validar_camada(
                copia, "silver"
            )

        self.assertTrue(
            validar_camada(
                self.silver, "silver"
            )
        )

    def test_16_novo_snapshot_nova_gold(self):
        registrar_venda(
            self.oltp, 1
        )

        novo = executar_arquitetura(
            self.oltp, self.lake
        )

        self.assertNotEqual(
            novo["bronze"]["snapshot_id"],
            self.resultado["bronze"]["snapshot_id"],
        )

        self.assertEqual(
            novo["gold"]["resumo"][
                "faturamento_centavos"
            ],
            30000,
        )

        self.assertEqual(
            self.resultado["gold"]["resumo"][
                "faturamento_centavos"
            ],
            15000,
        )


if __name__ == "__main__":
    unittest.main()
