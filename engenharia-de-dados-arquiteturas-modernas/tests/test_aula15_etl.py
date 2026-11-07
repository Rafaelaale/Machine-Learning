"""16 testes da Aula 15 - Arquitetura do ETL."""

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

from src.aula15_arquitetura_etl import (
    criar_dw,
    conectar,
    registrar_cliente,
    registrar_produto,
    registrar_promocao,
    registrar_tempo,
    lookup_cliente_historico,
    versoes_cliente,
    extrair_oltp,
    carregar_dimensoes_oltp,
    contagens,
)


class TestArquiteturaETL(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        raiz = Path(self.temp.name)

        self.dw = raiz / "dw15.db"
        criar_dw(self.dw)

    def tearDown(self):
        self.temp.cleanup()

    def cliente_inicial(self):
        return registrar_cliente(
            self.dw,
            "23400",
            "Cliente 1",
            "1900-01-01",
            cidade="Niteroi",
            estado="RJ",
        )

    def consulta(self, sql):
        with closing(conectar(self.dw)) as conexao:
            return conexao.execute(sql).fetchall()

    def test_01_estrutura_criada(self):
        self.assertTrue(self.dw.is_file())

    def test_02_cliente_primeira_sk(self):
        resultado = self.cliente_inicial()
        self.assertEqual(resultado["acao"], "novo_cliente")
        self.assertGreater(resultado["sk"], 0)

    def test_03_cliente_sem_mudanca(self):
        primeiro = self.cliente_inicial()

        segundo = registrar_cliente(
            self.dw, "23400", "Cliente 1",
            "1900-01-01",
            cidade="Niteroi", estado="RJ",
        )

        self.assertEqual(
            primeiro["sk"], segundo["sk"]
        )
        self.assertEqual(
            segundo["acao"], "reutilizado"
        )

    def test_04_correcao_nome_tipo1(self):
        primeiro = self.cliente_inicial()

        segundo = registrar_cliente(
            self.dw, "23400", "Cliente Corrigido",
            "1900-01-01",
            cidade="Niteroi", estado="RJ",
        )

        self.assertEqual(
            primeiro["sk"], segundo["sk"]
        )
        self.assertEqual(
            segundo["acao"], "correcao_tipo1"
        )
        self.assertEqual(
            len(versoes_cliente(self.dw, "23400")), 1
        )

    def test_05_mudanca_cidade_cria_scd2(self):
        primeiro = self.cliente_inicial()

        segundo = registrar_cliente(
            self.dw, "23400", "Cliente 1",
            "2024-05-01",
            cidade="Santos", estado="SP",
        )

        self.assertNotEqual(
            primeiro["sk"], segundo["sk"]
        )
        self.assertEqual(
            segundo["acao"], "nova_versao_scd2"
        )

    def test_06_datas_vigencia(self):
        self.cliente_inicial()

        registrar_cliente(
            self.dw, "23400", "Cliente 1",
            "2024-05-01",
            cidade="Santos", estado="SP",
        )

        versoes = versoes_cliente(self.dw, "23400")

        self.assertEqual(
            versoes[0]["valid_to"], "2024-05-01"
        )
        self.assertEqual(
            versoes[1]["valid_from"], "2024-05-01"
        )
        self.assertIsNone(
            versoes[1]["valid_to"]
        )

    def test_07_lookup_retroativo(self):
        primeiro = self.cliente_inicial()

        registrar_cliente(
            self.dw, "23400", "Cliente 1",
            "2024-05-01",
            cidade="Santos", estado="SP",
        )

        sk = lookup_cliente_historico(
            self.dw, "23400", "2024-04-15"
        )

        self.assertEqual(sk, primeiro["sk"])

    def test_08_lookup_atual_por_data(self):
        self.cliente_inicial()

        segundo = registrar_cliente(
            self.dw, "23400", "Cliente 1",
            "2024-05-01",
            cidade="Santos", estado="SP",
        )

        sk = lookup_cliente_historico(
            self.dw, "23400", "2024-05-15"
        )

        self.assertEqual(sk, segundo["sk"])

    def test_09_mudanca_fora_ordem_rejeitada(self):
        self.cliente_inicial()

        registrar_cliente(
            self.dw, "23400", "Cliente 1",
            "2024-05-01",
            cidade="Santos", estado="SP",
        )

        with self.assertRaises(ValueError):
            registrar_cliente(
                self.dw, "23400", "Cliente 1",
                "2024-04-01",
                cidade="Salvador", estado="BA",
            )

        self.assertEqual(
            len(versoes_cliente(self.dw, "23400")), 2
        )

    def test_10_produto_tipo1_preserva_sk(self):
        primeira = registrar_produto(
            self.dw, "P1", "Teclado",
            "C1", "Informatica"
        )

        segunda = registrar_produto(
            self.dw, "P1", "Teclado Atualizado",
            "C1", "Informatica"
        )

        self.assertEqual(primeira, segunda)
        self.assertEqual(
            contagens(self.dw)["dim_produto"], 1
        )

    def test_11_categoria_snowflake(self):
        registrar_produto(
            self.dw, "P1", "Teclado",
            "C1", "Informatica"
        )

        linhas = self.consulta(
            """
            SELECT p.nome_produto, c.nome_categoria
            FROM dim_produto p
            JOIN dim_categoria c
              ON c.categoria_sk = p.categoria_sk
            """
        )

        self.assertEqual(
            linhas, [("Teclado", "Informatica")]
        )

    def test_12_promocao_tipo1(self):
        primeira = registrar_promocao(
            self.dw, "PROMO1", "Campanha inicial"
        )

        segunda = registrar_promocao(
            self.dw, "PROMO1", "Campanha corrigida"
        )

        self.assertEqual(primeira, segunda)
        self.assertEqual(
            contagens(self.dw)["dim_promocao"], 1
        )

    def test_13_tempo_uma_sk_por_dia(self):
        with closing(conectar(self.dw)) as conexao:
            with conexao:
                primeira = registrar_tempo(
                    conexao, "2025-02-01"
                )
                segunda = registrar_tempo(
                    conexao, "2025-02-01"
                )

        self.assertEqual(primeira, 20250201)
        self.assertEqual(primeira, segunda)
        self.assertEqual(
            contagens(self.dw)["dim_tempo"], 1
        )

    def test_14_extracao_oltp(self):
        oltp = Path(self.temp.name) / "oltp.db"

        criar_modelo(oltp)
        registrar_venda(oltp, 1)

        dados = extrair_oltp(oltp)

        self.assertGreaterEqual(
            len(dados["clientes"]), 1
        )
        self.assertGreaterEqual(
            len(dados["produtos"]), 1
        )
        self.assertEqual(len(dados["datas"]), 1)

    def test_15_carga_dimensional_idempotente(self):
        oltp = Path(self.temp.name) / "oltp.db"

        criar_modelo(oltp)
        registrar_venda(oltp, 1)

        carregar_dimensoes_oltp(oltp, self.dw)
        antes = contagens(self.dw)

        carregar_dimensoes_oltp(oltp, self.dw)
        depois = contagens(self.dw)

        for tabela in (
            "dim_cliente", "dim_categoria",
            "dim_produto", "dim_tempo"
        ):
            self.assertEqual(
                antes[tabela], depois[tabela]
            )

        self.assertEqual(
            depois["auditoria_dimensoes"], 2
        )

    def test_16_origem_somente_leitura(self):
        oltp = Path(self.temp.name) / "oltp.db"

        criar_modelo(oltp)
        registrar_venda(oltp, 1)

        antes = extrair_oltp(oltp)

        carregar_dimensoes_oltp(
            oltp, self.dw
        )

        depois = extrair_oltp(oltp)

        self.assertEqual(antes, depois)


if __name__ == "__main__":
    unittest.main()
