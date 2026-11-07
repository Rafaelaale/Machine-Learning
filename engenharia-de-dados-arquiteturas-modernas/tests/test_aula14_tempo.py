"""16 testes da Aula 14 - Tempo e reprocessamento."""

import sqlite3
import sys
import tempfile
import unittest
from contextlib import closing
from pathlib import Path


BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from src.aula05_modelo_logico import (
    criar_modelo,
    registrar_venda,
)

from src.aula14_dimensao_tempo_politicas import (
    preparar_banco,
    registrar_cliente,
    chave_tempo,
    reprocessar_periodo,
    consultar_resumo,
    valores_por_mes,
    serie_diaria,
    extrair_periodo_oltp,
    importar_periodo_oltp,
    conectar,
)


class TestDimensaoTempoPoliticas(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.raiz = Path(self.temp.name)
        self.banco = self.raiz / "dw.db"

        preparar_banco(self.banco)

        for codigo in ("02342", "40032", "56700"):
            registrar_cliente(
                self.banco, codigo, "Cliente " + codigo
            )

        self.janeiro = [{
            "movimento_id": "JAN-1",
            "cliente": "40032",
            "data": "2025-01-10",
            "valor_centavos": 2000,
        }]

        self.fevereiro = [
            {
                "movimento_id": "FEV-1",
                "cliente": "02342",
                "data": "2025-02-01",
                "valor_centavos": 1000,
            },
            {
                "movimento_id": "FEV-2",
                "cliente": "40032",
                "data": "2025-02-10",
                "valor_centavos": 800,
            },
        ]

        self.corrigido = [
            {
                "movimento_id": "FEV-1",
                "cliente": "02342",
                "data": "2025-02-01",
                "valor_centavos": 1500,
            },
            {
                "movimento_id": "FEV-3",
                "cliente": "56700",
                "data": "2025-02-20",
                "valor_centavos": 1400,
            },
        ]

        reprocessar_periodo(
            self.banco, 2025, 1,
            self.janeiro, lote_completo=True
        )

        reprocessar_periodo(
            self.banco, 2025, 2,
            self.fevereiro, lote_completo=True
        )

    def tearDown(self):
        self.temp.cleanup()

    def consultar(self, sql):
        with closing(conectar(self.banco)) as conexao:
            return conexao.execute(sql).fetchall()

    def test_01_chave_numerica(self):
        self.assertEqual(chave_tempo("2025-02-01"), 20250201)

    def test_02_chave_ano_bissexto(self):
        self.assertEqual(chave_tempo("2024-02-29"), 20240229)

    def test_03_data_invalida(self):
        with self.assertRaises(ValueError):
            chave_tempo("2025-02-30")

    def test_04_calendario_continuo(self):
        serie = serie_diaria(self.banco)
        self.assertEqual(serie[0]["data"], "2025-01-10")
        self.assertEqual(serie[-1]["data"], "2025-02-10")
        self.assertEqual(len(serie), 32)

    def test_05_dias_sem_vendas(self):
        serie = serie_diaria(self.banco)
        dia = next(
            item for item in serie
            if item["data"] == "2025-02-02"
        )
        self.assertEqual(dia["valor_centavos"], 0)

    def test_06_dimensao_sem_duplicatas(self):
        resultado = self.consultar(
            """
            SELECT COUNT(*), COUNT(DISTINCT tempo_sk)
            FROM dim_tempo
            """
        )[0]
        self.assertEqual(resultado[0], resultado[1])

    def test_07_atualiza_valor(self):
        reprocessar_periodo(
            self.banco, 2025, 2,
            self.corrigido, lote_completo=True
        )
        self.assertEqual(
            valores_por_mes(self.banco)["2025-02"],
            2900,
        )

    def test_08_remove_fato_ausente(self):
        reprocessar_periodo(
            self.banco, 2025, 2,
            self.corrigido, lote_completo=True
        )
        linhas = self.consultar(
            """
            SELECT movimento_id
            FROM fato_movimentos
            WHERE movimento_id = 'FEV-2'
            """
        )
        self.assertEqual(linhas, [])

    def test_09_insere_fato_novo(self):
        reprocessar_periodo(
            self.banco, 2025, 2,
            self.corrigido, lote_completo=True
        )
        linhas = self.consultar(
            """
            SELECT valor_centavos
            FROM fato_movimentos
            WHERE movimento_id = 'FEV-3'
            """
        )
        self.assertEqual(linhas, [(1400,)])

    def test_10_preserva_outro_mes(self):
        reprocessar_periodo(
            self.banco, 2025, 2,
            self.corrigido, lote_completo=True
        )
        self.assertEqual(
            valores_por_mes(self.banco)["2025-01"],
            2000,
        )

    def test_11_reexecucao_idempotente(self):
        reprocessar_periodo(
            self.banco, 2025, 2,
            self.corrigido, lote_completo=True
        )
        antes = consultar = consultar_resumo(self.banco)

        reprocessar_periodo(
            self.banco, 2025, 2,
            self.corrigido, lote_completo=True
        )
        depois = consultar_resumo(self.banco)

        self.assertEqual(antes["fatos"], depois["fatos"])
        self.assertEqual(
            antes["total_centavos"],
            depois["total_centavos"],
        )

    def test_12_lote_incompleto_bloqueado(self):
        antes = consultar_resumo(self.banco)

        with self.assertRaises(ValueError):
            reprocessar_periodo(
                self.banco, 2025, 2,
                self.corrigido,
            )

        depois = consultar_resumo(self.banco)
        self.assertEqual(antes, depois)

    def test_13_movimento_fora_mes_bloqueado(self):
        invalido = [{
            "movimento_id": "OUTRO",
            "cliente": "02342",
            "data": "2025-03-01",
            "valor_centavos": 100,
        }]

        with self.assertRaises(ValueError):
            reprocessar_periodo(
                self.banco, 2025, 2,
                invalido, lote_completo=True
            )

        self.assertEqual(
            valores_por_mes(self.banco)["2025-02"],
            1800,
        )

    def test_14_rollback_lookup_inexistente(self):
        antes = consultar_resumo(self.banco)

        invalido = [{
            "movimento_id": "FALHA",
            "cliente": "SEM-CLIENTE",
            "data": "2025-02-01",
            "valor_centavos": 100,
        }]

        with self.assertRaises(ValueError):
            reprocessar_periodo(
                self.banco, 2025, 2,
                invalido, lote_completo=True
            )

        depois = consultar_resumo(self.banco)
        self.assertEqual(antes, depois)

    def test_15_lote_vazio_exclui_mes(self):
        reprocessar_periodo(
            self.banco, 2025, 2, [],
            lote_completo=True,
        )
        self.assertEqual(
            valores_por_mes(self.banco),
            {"2025-01": 2000},
        )
        self.assertEqual(
            consultar_resumo(self.banco)["dias_calendario"],
            1,
        )

    def test_16_extracao_oltp_somente_leitura(self):
        oltp = self.raiz / "minishop_oltp.db"
        destino = self.raiz / "minishop_dw_real.db"

        criar_modelo(oltp)
        registrar_venda(oltp, 1)

        with closing(
            sqlite3.connect(
                oltp.resolve().as_uri() + "?mode=ro",
                uri=True,
            )
        ) as conexao:
            periodo = conexao.execute(
                """
                SELECT substr(data_pedido, 1, 7)
                FROM pedidos
                LIMIT 1
                """
            ).fetchone()[0]

        ano, mes = map(int, periodo.split("-"))
        antes = extrair_periodo_oltp(oltp, ano, mes)

        resultado = importar_periodo_oltp(
            oltp, destino, ano, mes
        )

        depois = extrair_periodo_oltp(oltp, ano, mes)

        self.assertEqual(antes, depois)
        self.assertEqual(resultado["linhas_novas"], 1)
        self.assertEqual(
            consultar_resumo(destino)["total_centavos"],
            15000,
        )


if __name__ == "__main__":
    unittest.main()
