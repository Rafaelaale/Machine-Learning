"""16 testes da Aula 16 - Orquestracao ETL."""

import sqlite3
import sys
import tempfile
import unittest
from contextlib import closing
from datetime import date
from pathlib import Path


BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from src.aula05_modelo_logico import (
    criar_modelo,
    registrar_venda,
)

from src.aula15_arquitetura_etl import (
    registrar_cliente,
)

from src.aula16_orquestracao_etl import (
    executar_etl,
    extrair,
    indicadores,
    ultimos_30_dias,
    validar_periodo,
    conectar,
)


class TestOrquestracaoETL(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        raiz = Path(self.temp.name)

        self.oltp = raiz / "oltp.db"
        self.dw = raiz / "dw.db"

        criar_modelo(self.oltp)
        registrar_venda(self.oltp, 1)

        with closing(
            sqlite3.connect(self.oltp)
        ) as con:
            self.data = con.execute(
                """
                SELECT substr(data_pedido, 1, 10)
                FROM pedidos
                LIMIT 1
                """
            ).fetchone()[0]

        self.primeira = executar_etl(
            self.oltp, self.dw,
            self.data, self.data,
        )

    def tearDown(self):
        self.temp.cleanup()

    def sql(self, consulta):
        with closing(conectar(self.dw)) as con:
            return con.execute(consulta).fetchall()

    def test_01_periodo_valido(self):
        self.assertEqual(
            validar_periodo(self.data, self.data)[0],
            date.fromisoformat(self.data),
        )

    def test_02_periodo_invertido(self):
        with self.assertRaises(ValueError):
            validar_periodo(
                "2025-02-02", "2025-02-01"
            )

    def test_03_ultimos_30_dias(self):
        inicio, fim = ultimos_30_dias(
            date(2025, 3, 1)
        )
        self.assertEqual(inicio, "2025-01-31")
        self.assertEqual(fim, "2025-03-01")

    def test_04_extracao_oltp(self):
        dados = extrair(
            self.oltp, self.data, self.data
        )
        self.assertEqual(len(dados["vendas"]), 1)

    def test_05_faturamento(self):
        self.assertEqual(
            indicadores(self.dw)["faturamento_centavos"],
            15000,
        )

    def test_06_inventario(self):
        self.assertEqual(
            indicadores(self.dw)["saida_estoque"], -1
        )

    def test_07_categoria_antes_de_produto(self):
        linhas = self.sql(
            """
            SELECT p.nome_produto, c.nome_categoria
            FROM dim_produto p
            JOIN dim_categoria c
              ON c.categoria_sk = p.categoria_sk
            WHERE p.cod_produto = '1'
            """
        )
        self.assertEqual(
            linhas, [("Teclado", "Informatica")]
        )

    def test_08_cliente_scd2_preparado(self):
        linhas = self.sql(
            """
            SELECT cod_cliente, valid_from, valid_to
            FROM dim_cliente
            WHERE cod_cliente = '1'
            """
        )
        self.assertEqual(
            linhas, [("1", "1900-01-01", None)]
        )

    def test_09_tempo_numerico(self):
        chave = int(self.data.replace("-", ""))
        linhas = self.sql(
            f"""
            SELECT tempo_sk FROM dim_tempo
            WHERE tempo_sk = {chave}
            """
        )
        self.assertEqual(linhas, [(chave,)])

    def test_10_promocao_constante(self):
        linhas = self.sql(
            """
            SELECT cod_promocao FROM dim_promocao
            ORDER BY cod_promocao
            """
        )
        self.assertEqual(
            linhas, [("FALSE",), ("TRUE",)]
        )

    def test_11_aging_preparado(self):
        linhas = self.sql(
            "SELECT COUNT(*) FROM dim_aging"
        )
        self.assertEqual(linhas[0][0], 8)

    def test_12_financeiro_sem_valores_inventados(self):
        self.assertEqual(
            indicadores(self.dw)["linhas_financeiro"], 0
        )

    def test_13_reexecucao_sem_duplicar(self):
        executar_etl(
            self.oltp, self.dw,
            self.data, self.data
        )
        dados = indicadores(self.dw)

        self.assertEqual(dados["linhas_vendas"], 1)
        self.assertEqual(dados["linhas_inventario"], 1)
        self.assertEqual(dados["execucoes"], 2)

    def test_14_correcao_reprocessada(self):
        with closing(sqlite3.connect(self.oltp)) as con:
            with con:
                con.execute(
                    """
                    UPDATE itens_pedido
                    SET preco_unitario_centavos = 16000
                    WHERE pedido_id = 1
                      AND produto_id = 1
                    """
                )

        executar_etl(
            self.oltp, self.dw,
            self.data, self.data
        )

        self.assertEqual(
            indicadores(self.dw)["faturamento_centavos"],
            16000,
        )

    def test_15_exclusao_reprocessada(self):
        # Elimina o pagamento no OLTP temporario,
        # tornando o pedido inelegivel para a carga.
        with closing(sqlite3.connect(self.oltp)) as con:
            with con:
                con.execute(
                    "DELETE FROM pagamentos WHERE pedido_id = 1"
                )

        executar_etl(
            self.oltp, self.dw,
            self.data, self.data
        )

        dados = indicadores(self.dw)

        self.assertEqual(dados["linhas_vendas"], 0)
        self.assertEqual(dados["linhas_inventario"], 0)

    def test_16_lookup_scd2_historico(self):
        # Cria mudanca posterior ao fato original.
        inicio_antigo = date.fromisoformat(self.data)

        # Mudanca no dia seguinte, sem alterar o OLTP.
        from datetime import timedelta

        mudanca = (
            inicio_antigo + timedelta(days=1)
        ).isoformat()

        registrar_cliente(
            self.dw,
            "1",
            "Ana",
            mudanca,
            cidade="Salvador",
            estado="BA",
        )

        # O cliente da primeira versao nao tinha cidade.
        # Como o novo cadastro com atributos diferentes
        # foi inserido depois do fato, o lookup do passado
        # deve continuar apontando para a primeira SK.
        executar_etl(
            self.oltp, self.dw,
            self.data, self.data
        )

        versoes = self.sql(
            """
            SELECT cliente_sk, valid_from, valid_to
            FROM dim_cliente
            WHERE cod_cliente = '1'
            ORDER BY valid_from
            """
        )

        sk_fato = self.sql(
            "SELECT cliente_sk FROM fato_vendas"
        )[0][0]

        self.assertEqual(len(versoes), 2)
        self.assertEqual(sk_fato, versoes[0][0])


if __name__ == "__main__":
    unittest.main()
