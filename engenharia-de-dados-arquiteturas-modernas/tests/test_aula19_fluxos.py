"""16 testes da Aula 19 - Fluxos EL e ETL."""

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

from src.aula18_arquitetura_data_lake import (
    validar_camada,
)

from src.aula19_fluxos_data_lake import (
    fluxo_el,
    fluxo_etl,
    intervalo_snapshot,
    reconstruir_sem_oltp,
    reconciliar_gold_dw,
)


class TestFluxosDataLake(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.raiz = Path(self.temp.name)

        self.oltp = self.raiz / "origem.db"
        self.lake = self.raiz / "lake"
        self.dw = self.raiz / "dw.db"

        criar_modelo(self.oltp)
        registrar_venda(self.oltp, 1)

        self.el = fluxo_el(
            self.oltp, self.lake
        )

        self.bronze = Path(
            self.el["pasta_bronze"]
        )

        self.inicio, self.fim = intervalo_snapshot(
            self.bronze
        )

    def tearDown(self):
        self.temp.cleanup()

    def etl(self, destino=None):
        return fluxo_etl(
            self.bronze,
            destino or self.dw,
            self.inicio,
            self.fim,
            self.lake,
        )

    def test_01_el_cria_snapshot(self):
        self.assertTrue(
            (self.bronze / "oltp.sqlite").is_file()
        )

    def test_02_el_preserva_manifesto(self):
        self.assertTrue(
            (self.bronze / "manifest.json").is_file()
        )

    def test_03_integridade_bronze(self):
        self.assertTrue(
            validar_snapshot(self.bronze)
        )

    def test_04_periodo_do_snapshot(self):
        self.assertEqual(
            self.inicio,
            self.fim,
        )

    def test_05_etl_carrega_dw(self):
        resultado = self.etl()
        self.assertEqual(
            resultado["dw"]["indicadores"][
                "linhas_vendas"
            ],
            1,
        )

    def test_06_etl_faturamento(self):
        resultado = self.etl()
        self.assertEqual(
            resultado["dw"]["indicadores"][
                "faturamento_centavos"
            ],
            15000,
        )

    def test_07_etl_unidades(self):
        resultado = self.etl()
        self.assertEqual(
            resultado["dw"]["indicadores"][
                "unidades"
            ],
            1,
        )

    def test_08_etl_inventario(self):
        resultado = self.etl()
        self.assertEqual(
            resultado["dw"]["indicadores"][
                "saida_estoque"
            ],
            -1,
        )

    def test_09_silver_validada(self):
        resultado = self.etl()
        manifesto = validar_camada(
            resultado["silver"]["pasta"],
            "silver",
        )
        self.assertEqual(
            manifesto["camada"],
            "silver",
        )

    def test_10_gold_validada(self):
        resultado = self.etl()
        manifesto = validar_camada(
            resultado["gold"]["pasta"],
            "gold",
        )
        self.assertEqual(
            manifesto["camada"],
            "gold",
        )

    def test_11_reconciliacao_gold_dw(self):
        resultado = self.etl()

        self.assertTrue(
            reconciliar_gold_dw(
                resultado
            )["reconciliado"]
        )

    def test_12_bronze_nao_modificada(self):
        antes = hash_arquivo(
            self.bronze / "oltp.sqlite"
        )

        self.etl()

        depois = hash_arquivo(
            self.bronze / "oltp.sqlite"
        )

        self.assertEqual(
            antes, depois
        )

    def test_13_reexecutar_sem_duplicar(self):
        self.etl()
        segundo = self.etl()

        self.assertEqual(
            segundo["dw"]["indicadores"][
                "linhas_vendas"
            ],
            1,
        )

        self.assertEqual(
            segundo["dw"]["indicadores"][
                "faturamento_centavos"
            ],
            15000,
        )

    def test_14_reconstruir_sem_oltp(self):
        # O snapshot ja existe.
        # A fonte original se torna indisponivel.
        indisponivel = (
            self.raiz / "origem_indisponivel.db"
        )

        self.oltp.rename(indisponivel)

        try:
            novo_dw = self.raiz / "dw_recuperado.db"

            resultado = reconstruir_sem_oltp(
                self.bronze,
                novo_dw,
                self.lake,
            )

            self.assertEqual(
                resultado["dw"]["indicadores"][
                    "faturamento_centavos"
                ],
                15000,
            )

        finally:
            indisponivel.rename(self.oltp)

    def test_15_snapshot_alterado_bloqueado(self):
        copia = self.raiz / "raw_corrompida"

        shutil.copytree(
            self.bronze,
            copia,
        )

        with open(
            copia / "pedidos.jsonl",
            "a",
            encoding="utf-8",
        ) as arquivo:
            arquivo.write(
                '{"registro": "alterado"}\n'
            )

        with self.assertRaises(ValueError):
            reconstruir_sem_oltp(
                copia,
                self.raiz / "dw_corrompido.db",
                self.lake,
            )

        self.assertTrue(
            validar_snapshot(self.bronze)
        )

    def test_16_nova_venda_novo_snapshot(self):
        registrar_venda(
            self.oltp, 1
        )

        novo_el = fluxo_el(
            self.oltp, self.lake
        )

        self.assertNotEqual(
            self.el["snapshot_id"],
            novo_el["snapshot_id"],
        )

        novo_dw = self.raiz / "dw_novo.db"

        novo = reconstruir_sem_oltp(
            novo_el["pasta_bronze"],
            novo_dw,
            self.lake,
        )

        self.assertEqual(
            novo["dw"]["indicadores"][
                "faturamento_centavos"
            ],
            30000,
        )

        self.assertTrue(
            validar_snapshot(self.bronze)
        )


if __name__ == "__main__":
    unittest.main()
