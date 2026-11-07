"""Testes da Aula 11 - ETL incremental e SCD Tipo 2."""

import hashlib
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

from src.aula11_etl_minishop import (
    executar_etl,
    extrair,
    transformar,
    indicadores,
    historico_cliente,
)


class TestETLMinishop(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        raiz = Path(self.temp.name)

        self.oltp = raiz / "oltp.db"
        self.dw = raiz / "etl.db"

        criar_modelo(self.oltp)
        registrar_venda(self.oltp, 1)

        self.primeira = executar_etl(
            self.oltp, self.dw
        )

    def tearDown(self):
        self.temp.cleanup()

    def alterar_oltp(self, comando, parametros=()):
        with closing(
            sqlite3.connect(self.oltp)
        ) as conexao:
            with conexao:
                conexao.execute(
                    comando, parametros
                )

    def consulta_dw(self, comando, parametros=()):
        with closing(
            sqlite3.connect(self.dw)
        ) as conexao:
            return conexao.execute(
                comando, parametros
            ).fetchall()

    def test_01_carga_inicial(self):
        self.assertEqual(
            self.primeira["load"]["tipo"],
            "inicial",
        )

    def test_02_um_fato_inicial(self):
        self.assertEqual(
            indicadores(self.dw)["fatos"], 1
        )

    def test_03_valor_da_venda(self):
        self.assertEqual(
            indicadores(self.dw)["faturamento_centavos"],
            15000,
        )

    def test_04_reexecucao_sem_duplicar_fatos(self):
        segunda = executar_etl(self.oltp, self.dw)

        self.assertEqual(
            segunda["load"]["novos_fatos"], 0
        )
        self.assertEqual(
            indicadores(self.dw)["fatos"], 1
        )

    def test_05_segunda_execucao_incremental(self):
        segunda = executar_etl(self.oltp, self.dw)

        self.assertEqual(
            segunda["load"]["tipo"], "incremental"
        )

    def test_06_novo_pedido_incremental(self):
        registrar_venda(self.oltp, 1)

        segunda = executar_etl(self.oltp, self.dw)

        self.assertEqual(
            segunda["load"]["novos_fatos"], 1
        )
        self.assertEqual(
            indicadores(self.dw)["fatos"], 2
        )

    def test_07_faturamento_incremental(self):
        registrar_venda(self.oltp, 1)
        executar_etl(self.oltp, self.dw)

        self.assertEqual(
            indicadores(self.dw)["faturamento_centavos"],
            30000,
        )

    def test_08_lookup_reutiliza_cliente(self):
        registrar_venda(self.oltp, 1)
        executar_etl(self.oltp, self.dw)

        self.assertEqual(
            indicadores(self.dw)["versoes_clientes"],
            1,
        )

    def test_09_scd2_alteracao_cliente(self):
        self.alterar_oltp(
            "UPDATE clientes SET nome = ? WHERE cliente_id = 1",
            ("Ana Atualizada",),
        )

        executar_etl(self.oltp, self.dw)

        historico = historico_cliente(self.dw, 1)

        self.assertEqual(len(historico), 2)
        self.assertEqual(
            historico[0]["nome"], "Ana"
        )
        self.assertEqual(
            historico[1]["nome"], "Ana Atualizada"
        )
        self.assertFalse(historico[0]["ativo"])
        self.assertTrue(historico[1]["ativo"])

    def test_10_fato_antigo_mantem_sk(self):
        antiga = self.consulta_dw(
            "SELECT cliente_sk FROM fato_vendas"
        )[0][0]

        self.alterar_oltp(
            "UPDATE clientes SET nome = ? WHERE cliente_id = 1",
            ("Ana Atualizada",),
        )

        executar_etl(self.oltp, self.dw)

        atual = self.consulta_dw(
            "SELECT cliente_sk FROM fato_vendas"
        )[0][0]

        self.assertEqual(antiga, atual)

    def test_11_nova_venda_usa_nova_sk(self):
        self.alterar_oltp(
            "UPDATE clientes SET nome = ? WHERE cliente_id = 1",
            ("Ana Atualizada",),
        )

        registrar_venda(self.oltp, 1)
        executar_etl(self.oltp, self.dw)

        chaves = self.consulta_dw(
            """
            SELECT pedido_id_origem, cliente_sk
            FROM fato_vendas
            ORDER BY pedido_id_origem
            """
        )

        self.assertNotEqual(
            chaves[0][1], chaves[1][1]
        )

    def test_12_scd2_alteracao_produto(self):
        self.alterar_oltp(
            "UPDATE produtos SET nome = ? WHERE produto_id = 1",
            ("Teclado Novo",),
        )

        executar_etl(self.oltp, self.dw)

        versoes = self.consulta_dw(
            """
            SELECT nome, ativo
            FROM dim_produto
            ORDER BY versao
            """
        )

        self.assertEqual(len(versoes), 2)
        self.assertEqual(
            versoes[1], ("Teclado Novo", 1)
        )

    def test_13_origem_inexistente(self):
        with self.assertRaises(FileNotFoundError):
            executar_etl(
                self.oltp.parent / "ausente.db",
                self.dw,
            )

    def test_14_mesmo_caminho_proibido(self):
        with self.assertRaises(ValueError):
            executar_etl(self.oltp, self.oltp)

    def test_15_transformacao_invalida(self):
        registros = extrair(self.oltp)
        registros[0]["cliente_nome"] = "   "

        with self.assertRaises(ValueError):
            transformar(registros)

        self.assertEqual(
            indicadores(self.dw)["fatos"], 1
        )

    def test_16_fato_alterado_exige_reprocessamento(self):
        self.alterar_oltp(
            """
            UPDATE itens_pedido
            SET preco_unitario_centavos = 16000
            WHERE pedido_id = 1 AND produto_id = 1
            """
        )

        antes = indicadores(self.dw)

        with self.assertRaises(ValueError):
            executar_etl(self.oltp, self.dw)

        depois = indicadores(self.dw)

        self.assertEqual(antes, depois)


if __name__ == "__main__":
    unittest.main()
