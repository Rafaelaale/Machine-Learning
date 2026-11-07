"""16 testes da Aula 20 - Data Lake da Minishop."""

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
)

from src.aula20_data_lake_minishop import (
    executar,
    criar_bronze_dominios,
    preparar_silver,
    criar_gold_mensal,
    carregar_dw_da_silver,
    ler_silver,
    ler_jsonl,
    validar_camada,
)


class TestDataLakeMinishop(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()

        raiz = Path(self.temp.name)
        self.oltp = raiz / "oltp.db"
        self.lake = raiz / "lake"
        self.dw = raiz / "dw.db"

        criar_modelo(self.oltp)
        registrar_venda(self.oltp, 1)

        self.resultado = executar(
            self.oltp, self.lake, self.dw
        )

        self.raw = Path(
            self.resultado["snapshot"]["pasta"]
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

    def test_01_snapshot_raw_preservado(self):
        self.assertTrue(validar_snapshot(self.raw))

    def test_02_bronze_clientes(self):
        self.assertTrue(
            (
                self.bronze / "cliente"
                / "clientes.jsonl"
            ).is_file()
        )

    def test_03_bronze_vendas(self):
        self.assertTrue(
            (
                self.bronze / "vendas"
                / "itens_pedido.jsonl"
            ).is_file()
        )

    def test_04_bronze_financeiro(self):
        self.assertTrue(
            (
                self.bronze / "financeiro"
                / "faturas.jsonl"
            ).is_file()
        )

    def test_05_bronze_logistica(self):
        self.assertTrue(
            (
                self.bronze / "logistica"
                / "movimentos_estoque.jsonl"
            ).is_file()
        )

    def test_06_silver_produto_categoria(self):
        dados = ler_silver(self.silver)

        self.assertEqual(len(dados["produtos"]), 1)
        self.assertEqual(
            dados["produtos"][0]["categoria_nome"],
            "Informatica",
        )

    def test_07_silver_pedido_item(self):
        dados = ler_silver(self.silver)

        self.assertEqual(len(dados["vendas"]), 1)
        self.assertEqual(
            dados["vendas"][0]["valor_total_centavos"],
            15000,
        )

    def test_08_particao_mensal(self):
        particoes = list(
            (self.silver / "vendas").glob(
                "ano=*/mes=*/vendas.jsonl"
            )
        )
        self.assertEqual(len(particoes), 1)

    def test_09_gold_mensal(self):
        mensal = ler_jsonl(
            self.gold / "indicadores_mensais.jsonl"
        )

        self.assertEqual(len(mensal), 1)
        self.assertEqual(
            mensal[0]["faturamento_centavos"],
            15000,
        )

    def test_10_dw_alimentado_pela_silver(self):
        self.assertEqual(
            self.resultado["dw"]["indicadores"][
                "faturamento_centavos"
            ],
            15000,
        )

    def test_11_reconciliacao(self):
        mensal = ler_jsonl(
            self.gold / "indicadores_mensais.jsonl"
        )

        total = sum(
            item["faturamento_centavos"]
            for item in mensal
        )

        self.assertEqual(
            total,
            self.resultado["dw"]["indicadores"][
                "faturamento_centavos"
            ],
        )

    def test_12_reexecucao_idempotente(self):
        segunda = executar(
            self.oltp, self.lake, self.dw
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
        self.assertEqual(
            segunda["dw"]["indicadores"][
                "linhas_vendas"
            ],
            1,
        )

    def test_13_raw_nao_modificada(self):
        antes = hash_arquivo(
            self.raw / "oltp.sqlite"
        )

        preparar_silver(
            self.bronze, self.lake
        )

        criar_gold_mensal(
            self.silver, self.lake
        )

        depois = hash_arquivo(
            self.raw / "oltp.sqlite"
        )

        self.assertEqual(antes, depois)

    def test_14_corrupcao_detectada(self):
        copia = (
            Path(self.temp.name) / "bronze_corrompida"
        )

        shutil.copytree(
            self.bronze, copia
        )

        with (
            copia / "cliente" / "clientes.jsonl"
        ).open("a", encoding="utf-8") as arquivo:
            arquivo.write('{"alterado":true}\n')

        with self.assertRaises(ValueError):
            validar_camada(copia, "bronze")

        self.assertTrue(
            validar_camada(self.bronze, "bronze")
        )

    def test_15_dw_sem_oltp_original(self):
        indisponivel = (
            Path(self.temp.name) / "oltp_indisponivel.db"
        )

        self.oltp.rename(indisponivel)

        try:
            dados = ler_silver(self.silver)
            dia = dados["vendas"][0]["data"]

            novo_dw = (
                Path(self.temp.name) / "dw_recriado.db"
            )

            resultado = carregar_dw_da_silver(
                self.silver, novo_dw, dia, dia
            )

            self.assertEqual(
                resultado["indicadores"][
                    "faturamento_centavos"
                ],
                15000,
            )
        finally:
            indisponivel.rename(self.oltp)

    def test_16_novo_snapshot_preserva_anterior(self):
        registrar_venda(self.oltp, 1)

        novo_dw = (
            Path(self.temp.name) / "dw_novo.db"
        )

        novo = executar(
            self.oltp, self.lake, novo_dw
        )

        self.assertNotEqual(
            novo["snapshot"]["snapshot_id"],
            self.resultado["snapshot"]["snapshot_id"],
        )

        self.assertEqual(
            novo["dw"]["indicadores"][
                "faturamento_centavos"
            ],
            30000,
        )

        self.assertTrue(
            validar_snapshot(self.raw)
        )


if __name__ == "__main__":
    unittest.main()
