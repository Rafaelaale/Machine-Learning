"""16 testes da Aula 22."""

import shutil
import sys
import tempfile
import unittest
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from src.aula05_modelo_logico import criar_modelo, registrar_venda
from src.aula17_data_lake import validar_snapshot, hash_arquivo
from src.aula22_arquitetura_lakehouse import (
    executar, criar_lakehouse, validar_catalogo, consultar_parquet,
    resumo_vendas, vendas_por_mes, vendas_por_produto,
    vendas_por_cliente, reconciliar_gold,
)


class TestArquiteturaLakehouse(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.raiz = Path(cls.temp.name)
        cls.oltp = cls.raiz / "oltp.db"
        cls.lake = cls.raiz / "lake"
        criar_modelo(cls.oltp)
        registrar_venda(cls.oltp, 1)
        cls.resultado = executar(cls.oltp, cls.lake)
        cls.raw = Path(cls.resultado["snapshot"]["pasta"])
        cls.silver = Path(cls.resultado["silver"]["pasta"])
        cls.gold = Path(cls.resultado["gold"]["pasta"])
        cls.lakehouse = Path(cls.resultado["lakehouse"]["pasta"])

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_01_catalogo_existe(self):
        self.assertTrue((self.lakehouse / "catalogo.json").is_file())

    def test_02_quatro_tabelas(self):
        self.assertEqual(
            set(validar_catalogo(self.lakehouse)["tabelas"]),
            {"clientes", "produtos", "vendas", "movimentos"},
        )

    def test_03_parquet_real(self):
        for nome in ("clientes", "produtos", "vendas", "movimentos"):
            with (self.lakehouse / f"{nome}.parquet").open("rb") as f:
                self.assertEqual(f.read(4), b"PAR1")
                f.seek(-4, 2)
                self.assertEqual(f.read(4), b"PAR1")

    def test_04_sql_sobre_parquet(self):
        self.assertEqual(
            consultar_parquet(
                self.lakehouse, "SELECT COUNT(*) AS total FROM vendas"
            )[0]["total"], 1,
        )

    def test_05_faturamento(self):
        self.assertEqual(
            resumo_vendas(self.lakehouse)["faturamento_centavos"], 15000
        )

    def test_06_unidades(self):
        self.assertEqual(
            resumo_vendas(self.lakehouse)["unidades"], 1
        )

    def test_07_cliente(self):
        self.assertEqual(
            vendas_por_cliente(self.lakehouse)[0]["nome"], "Ana"
        )

    def test_08_produto(self):
        self.assertEqual(
            vendas_por_produto(self.lakehouse)[0]["produto_nome"], "Teclado"
        )

    def test_09_categoria(self):
        self.assertEqual(
            vendas_por_produto(self.lakehouse)[0]["categoria_nome"],
            "Informatica",
        )

    def test_10_consulta_mensal(self):
        self.assertEqual(
            vendas_por_mes(self.lakehouse)[0]["faturamento_centavos"],
            15000,
        )

    def test_11_gold_reconciliada(self):
        self.assertTrue(
            reconciliar_gold(
                self.lakehouse, self.gold
            )["reconciliado"]
        )

    def test_12_idempotencia(self):
        resultado = criar_lakehouse(self.silver, self.lake)
        self.assertFalse(resultado["novo"])

    def test_13_bronze_preservada(self):
        antes = hash_arquivo(self.raw / "oltp.sqlite")
        resumo_vendas(self.lakehouse)
        self.assertEqual(
            antes, hash_arquivo(self.raw / "oltp.sqlite")
        )
        self.assertTrue(validar_snapshot(self.raw))

    def test_14_detecta_corrupcao(self):
        copia = self.raiz / self.lakehouse.name
        shutil.copytree(self.lakehouse, copia)
        with (copia / "vendas.parquet").open("ab") as f:
            f.write(b"alterado")
        with self.assertRaises(ValueError):
            validar_catalogo(copia)

    def test_15_consulta_sem_oltp(self):
        fora = self.raiz / "oltp_indisponivel.db"
        self.oltp.rename(fora)
        try:
            self.assertEqual(
                resumo_vendas(self.lakehouse)["faturamento_centavos"],
                15000,
            )
        finally:
            fora.rename(self.oltp)

    def test_16_snapshot_novo_preserva_anterior(self):
        registrar_venda(self.oltp, 1)
        novo = executar(self.oltp, self.lake)
        self.assertNotEqual(
            novo["snapshot"]["snapshot_id"],
            self.resultado["snapshot"]["snapshot_id"],
        )
        self.assertEqual(novo["resumo"]["faturamento_centavos"], 30000)
        self.assertEqual(
            resumo_vendas(self.lakehouse)["faturamento_centavos"],
            15000,
        )


if __name__ == "__main__":
    unittest.main()
