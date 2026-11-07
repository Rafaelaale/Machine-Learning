"""16 testes da Aula 13 - Slowly Changing Dimensions."""

import sqlite3
import sys
import tempfile
import unittest
from contextlib import closing
from pathlib import Path


BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from src.aula13_slowly_changing_dimensions import (
    CLIENTE,
    atualizar_scd1,
    buscar_sk_atual,
    buscar_sk_historica,
    conectar,
    executar_exemplo,
    faturamento_por_cidade,
    iniciar_scd2,
    mudar_cidade,
    preparar_banco,
    registrar_venda,
    validar_vigencias,
    versoes_cliente,
)


class TestSlowlyChangingDimensions(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.banco = Path(self.temp.name) / "scd.db"
        self.resultado = executar_exemplo(self.banco)

    def tearDown(self):
        self.temp.cleanup()

    def consultar(self, sql):
        with closing(conectar(self.banco)) as conexao:
            return conexao.execute(sql).fetchall()

    def test_01_banco_criado(self):
        self.assertTrue(self.banco.is_file())

    def test_02_scd1_reclassifica_historico(self):
        self.assertEqual(
            self.resultado["scd1"],
            {"Santos": 6500},
        )

    def test_03_scd2_preserva_niteroi(self):
        self.assertEqual(
            self.resultado["scd2"]["Niteroi"], 5000
        )

    def test_04_scd2_vendas_santos(self):
        self.assertEqual(
            self.resultado["scd2"]["Santos"], 1500
        )

    def test_05_duas_versoes_scd2(self):
        self.assertEqual(
            len(versoes_cliente(self.banco, CLIENTE)), 2
        )

    def test_06_sk_diferentes(self):
        versoes = versoes_cliente(self.banco, CLIENTE)
        self.assertNotEqual(
            versoes[0]["sk"], versoes[1]["sk"]
        )

    def test_07_apenas_versao_recente_ativa(self):
        versoes = versoes_cliente(self.banco, CLIENTE)
        self.assertFalse(versoes[0]["atual"])
        self.assertTrue(versoes[1]["atual"])

    def test_08_limite_exclusivo(self):
        versoes = versoes_cliente(self.banco, CLIENTE)
        self.assertEqual(
            versoes[0]["fim_exclusivo"], "2024-05-01"
        )
        self.assertEqual(
            versoes[1]["inicio"], "2024-05-01"
        )

    def test_09_lookup_antes_mudanca(self):
        with closing(conectar(self.banco)) as conexao:
            sk = buscar_sk_historica(
                conexao, CLIENTE, "2024-04-30"
            )
        self.assertEqual(
            sk, versoes_cliente(self.banco, CLIENTE)[0]["sk"]
        )

    def test_10_lookup_no_dia_mudanca(self):
        with closing(conectar(self.banco)) as conexao:
            sk = buscar_sk_historica(
                conexao, CLIENTE, "2024-05-01"
            )
        self.assertEqual(sk, buscar_sk_atual(self.banco, CLIENTE))

    def test_11_carga_retroativa_sk_antiga(self):
        retro = self.consultar(
            """
            SELECT cliente_sk FROM vendas_scd2
            WHERE evento_id = 'VENDA-RETRO'
            """
        )[0][0]
        self.assertNotEqual(
            retro, buscar_sk_atual(self.banco, CLIENTE)
        )

    def test_12_reexecucao_sem_duplicacao(self):
        antes = self.consultar(
            "SELECT COUNT(*) FROM vendas_scd2"
        )[0][0]
        executar_exemplo(self.banco)
        depois = self.consultar(
            "SELECT COUNT(*) FROM vendas_scd2"
        )[0][0]
        self.assertEqual(antes, depois)
        self.assertEqual(depois, 6)

    def test_13_periodos_validos(self):
        self.assertTrue(
            validar_vigencias(self.banco, CLIENTE)
        )

    def test_14_mudanca_fora_de_ordem_rejeitada(self):
        with self.assertRaises(ValueError):
            mudar_cidade(
                self.banco, CLIENTE, "Rio", "2024-04-01"
            )
        self.assertTrue(
            validar_vigencias(self.banco, CLIENTE)
        )

    def test_15_fato_sem_versao_rejeitado(self):
        with self.assertRaises(ValueError):
            registrar_venda(
                self.banco,
                "INVALIDO",
                CLIENTE,
                "1899-12-31",
                1000,
            )
        self.assertEqual(
            self.consultar(
                "SELECT COUNT(*) FROM vendas_scd2"
            )[0][0],
            6,
        )

    def test_16_integridade_referencial(self):
        with closing(conectar(self.banco)) as conexao:
            with self.assertRaises(sqlite3.IntegrityError):
                with conexao:
                    conexao.execute(
                        """
                        INSERT INTO vendas_scd2
                        (evento_id, cliente_sk,
                         data_venda, valor_centavos)
                        VALUES ('FALSO', 9999, '2024-01-01', 100)
                        """
                    )


if __name__ == "__main__":
    unittest.main()
