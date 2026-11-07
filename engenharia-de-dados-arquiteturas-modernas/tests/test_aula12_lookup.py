"""Testes da Aula 12 - Lookup e Surrogate Keys."""

import sqlite3
import sys
import tempfile
import unittest
from contextlib import closing
from pathlib import Path


BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from src.aula12_lookup_surrogate_keys import (
    CLIENTES_INICIAIS,
    CLIENTES_ATUALIZADOS,
    PRODUTOS_EXEMPLO,
    VENDAS_EXEMPLO,
    carregar_clientes,
    carregar_produtos,
    carregar_fatos,
    criar_banco,
    listar_clientes,
    resumo_fatos,
)


class TestLookupSurrogateKeys(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.banco = Path(self.temp.name) / "lookup.db"

        criar_banco(self.banco)
        self.inicial = carregar_clientes(
            self.banco, CLIENTES_INICIAIS
        )

    def tearDown(self):
        self.temp.cleanup()

    def consultar(self, sql, parametros=()):
        with closing(sqlite3.connect(self.banco)) as conexao:
            return conexao.execute(
                sql, parametros
            ).fetchall()

    def test_01_criacao_banco(self):
        self.assertTrue(self.banco.exists())

    def test_02_tres_clientes_iniciais(self):
        self.assertEqual(self.inicial["inseridos"], 3)

    def test_03_sk_inteira(self):
        clientes = listar_clientes(self.banco)
        self.assertIsInstance(clientes[0]["sk"], int)

    def test_04_codigo_com_zero_preservado(self):
        codigos = [
            c["codigo"] for c in listar_clientes(self.banco)
        ]
        self.assertIn("02342", codigos)

    def test_05_lookup_existente_nao_duplica(self):
        resultado = carregar_clientes(
            self.banco, CLIENTES_INICIAIS
        )
        self.assertEqual(resultado["inseridos"], 0)
        self.assertEqual(len(listar_clientes(self.banco)), 3)

    def test_06_atualiza_saldo(self):
        resultado = carregar_clientes(
            self.banco, CLIENTES_ATUALIZADOS
        )
        self.assertEqual(resultado["atualizados"], 2)

        cliente = next(
            c for c in listar_clientes(self.banco)
            if c["codigo"] == "23400"
        )
        self.assertEqual(cliente["saldo_centavos"], 30000)

    def test_07_atualiza_nome(self):
        carregar_clientes(
            self.banco, CLIENTES_ATUALIZADOS
        )
        cliente = next(
            c for c in listar_clientes(self.banco)
            if c["codigo"] == "02342"
        )
        self.assertEqual(cliente["nome"], "Cliente 2A")

    def test_08_cliente_inalterado(self):
        resultado = carregar_clientes(
            self.banco, CLIENTES_ATUALIZADOS
        )
        self.assertEqual(resultado["inalterados"], 1)

    def test_09_novo_cliente_recebe_sk(self):
        resultado = carregar_clientes(
            self.banco, CLIENTES_ATUALIZADOS
        )
        self.assertEqual(resultado["inseridos"], 1)
        self.assertEqual(len(listar_clientes(self.banco)), 4)

    def test_10_scd1_preserva_sk_existente(self):
        anterior = {
            c["codigo"]: c["sk"]
            for c in listar_clientes(self.banco)
        }
        carregar_clientes(
            self.banco, CLIENTES_ATUALIZADOS
        )
        atual = {
            c["codigo"]: c["sk"]
            for c in listar_clientes(self.banco)
        }
        self.assertEqual(anterior["02342"], atual["02342"])
        self.assertEqual(anterior["23400"], atual["23400"])

    def test_11_scd1_nao_cria_versoes(self):
        carregar_clientes(
            self.banco, CLIENTES_ATUALIZADOS
        )
        quantidade = self.consultar(
            """
            SELECT COUNT(*)
            FROM dim_clientes
            WHERE codigo_natural = '02342'
            """
        )[0][0]
        self.assertEqual(quantidade, 1)

    def test_12_lookup_fato_por_sk(self):
        carregar_clientes(
            self.banco, CLIENTES_ATUALIZADOS
        )
        carregar_produtos(self.banco, PRODUTOS_EXEMPLO)
        resultado = carregar_fatos(
            self.banco, VENDAS_EXEMPLO
        )
        self.assertEqual(resultado["novos_fatos"], 3)

    def test_13_faturamento(self):
        carregar_clientes(
            self.banco, CLIENTES_ATUALIZADOS
        )
        carregar_produtos(self.banco, PRODUTOS_EXEMPLO)
        carregar_fatos(self.banco, VENDAS_EXEMPLO)
        self.assertEqual(
            resumo_fatos(self.banco)["faturamento_centavos"],
            53000,
        )

    def test_14_fatos_nao_duplicados(self):
        carregar_clientes(
            self.banco, CLIENTES_ATUALIZADOS
        )
        carregar_produtos(self.banco, PRODUTOS_EXEMPLO)
        carregar_fatos(self.banco, VENDAS_EXEMPLO)
        segunda = carregar_fatos(
            self.banco, VENDAS_EXEMPLO
        )
        self.assertEqual(segunda["novos_fatos"], 0)
        self.assertEqual(resumo_fatos(self.banco)["fatos"], 3)

    def test_15_referencia_inexistente(self):
        carregar_produtos(self.banco, PRODUTOS_EXEMPLO)
        venda = [{
            "venda_id": 99,
            "cliente": "NAO-EXISTE",
            "produto": "PROD-01",
            "quantidade": 1,
            "valor_centavos": 100,
        }]
        with self.assertRaises(ValueError):
            carregar_fatos(self.banco, venda)
        self.assertEqual(resumo_fatos(self.banco)["fatos"], 0)

    def test_16_integridade_referencial(self):
        with closing(sqlite3.connect(self.banco)) as conexao:
            conexao.execute("PRAGMA foreign_keys = ON")

            with self.assertRaises(sqlite3.IntegrityError):
                with conexao:
                    conexao.execute(
                        """
                        INSERT INTO fato_vendas
                        VALUES (99, 999, 999, 1, 100)
                        """
                    )


if __name__ == "__main__":
    unittest.main()
