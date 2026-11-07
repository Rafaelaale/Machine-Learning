from contextlib import closing
"""16 testes da Aula 17 - Introducao ao Data Lake."""

import hashlib
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
    ingerir,
    validar_snapshot,
    ler_pedidos_jsonl,
    materializar_curado,
    extrair_vendas_do_snapshot,
    listar_snapshots,
    hash_arquivo,
    conectar_somente_leitura,
)


class TestDataLake(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        raiz = Path(self.temp.name)

        self.oltp = raiz / "oltp.db"
        self.lake = raiz / "lake"

        criar_modelo(self.oltp)
        registrar_venda(self.oltp, 1)

        self.ingestao = ingerir(
            self.oltp, self.lake
        )
        self.raw = Path(self.ingestao["pasta"])

    def tearDown(self):
        self.temp.cleanup()

    def test_01_snapshot_criado(self):
        self.assertTrue(
            (self.raw / "oltp.sqlite").is_file()
        )

    def test_02_banco_preservado(self):
        with closing(conectar_somente_leitura(
            self.raw / "oltp.sqlite"
        )) as con:
            quantidade = con.execute(
                "SELECT COUNT(*) FROM pedidos"
            ).fetchone()[0]

        self.assertEqual(quantidade, 1)

    def test_03_csv_bruto(self):
        arquivo = self.raw / "clientes.csv"
        self.assertTrue(arquivo.is_file())
        self.assertIn(
            "cliente_id",
            arquivo.read_text(encoding="utf-8"),
        )

    def test_04_jsonl_bruto(self):
        pedidos = ler_pedidos_jsonl(
            self.raw / "pedidos.jsonl"
        )
        self.assertEqual(len(pedidos), 1)

    def test_05_manifest_hashes(self):
        manifest = json.loads(
            (self.raw / "manifest.json").read_text(
                encoding="utf-8"
            )
        )

        for nome, digest in manifest["arquivos"].items():
            self.assertEqual(
                hash_arquivo(self.raw / nome),
                digest,
            )

    def test_06_integridade(self):
        self.assertTrue(
            validar_snapshot(self.raw)
        )

    def test_07_ingestao_idempotente(self):
        segunda = ingerir(
            self.oltp, self.lake
        )
        self.assertFalse(segunda["novo"])
        self.assertEqual(
            segunda["snapshot_id"],
            self.ingestao["snapshot_id"],
        )

    def test_08_origem_nao_modificada(self):
        antes = hash_arquivo(self.oltp)

        ingerir(self.oltp, self.lake)

        depois = hash_arquivo(self.oltp)
        self.assertEqual(antes, depois)

    def test_09_receita_do_snapshot(self):
        vendas = extrair_vendas_do_snapshot(
            self.raw
        )
        self.assertEqual(
            sum(v["valor_centavos"] for v in vendas),
            15000,
        )

    def test_10_quantidade_vendida(self):
        vendas = extrair_vendas_do_snapshot(
            self.raw
        )
        self.assertEqual(
            sum(v["quantidade"] for v in vendas),
            1,
        )

    def test_11_materializacao_curated(self):
        resultado = materializar_curado(
            self.raw, self.lake
        )
        pasta = Path(resultado["pasta"])

        self.assertTrue(
            (pasta / "vendas_tratadas.csv").is_file()
        )
        self.assertEqual(
            resultado["resumo"]["faturamento_centavos"],
            15000,
        )

    def test_12_curated_nao_altera_raw(self):
        antes = {
            p.name: hash_arquivo(p)
            for p in self.raw.iterdir()
            if p.is_file()
        }

        materializar_curado(
            self.raw, self.lake
        )

        depois = {
            p.name: hash_arquivo(p)
            for p in self.raw.iterdir()
            if p.is_file()
        }

        self.assertEqual(antes, depois)

    def test_13_novo_estado_novo_snapshot(self):
        registrar_venda(self.oltp, 1)

        novo = ingerir(
            self.oltp, self.lake
        )

        self.assertTrue(novo["novo"])
        self.assertNotEqual(
            novo["snapshot_id"],
            self.ingestao["snapshot_id"],
        )

    def test_14_historico_preservado(self):
        registrar_venda(self.oltp, 1)

        novo = ingerir(
            self.oltp, self.lake
        )

        antigo = extrair_vendas_do_snapshot(
            self.raw
        )
        recente = extrair_vendas_do_snapshot(
            novo["pasta"]
        )

        self.assertEqual(len(antigo), 1)
        self.assertEqual(len(recente), 2)
        self.assertTrue(
            validar_snapshot(self.raw)
        )

    def test_15_alteracao_raw_detectada(self):
        copia = (
            Path(self.temp.name) / "snapshot_alterado"
        )

        shutil.copytree(self.raw, copia)

        arquivo = copia / "pedidos.jsonl"

        with open(arquivo, "a", encoding="utf-8") as saida:
            saida.write('{"registro": "alterado"}\n')

        with self.assertRaises(ValueError):
            validar_snapshot(copia)

        self.assertTrue(
            validar_snapshot(self.raw)
        )

    def test_16_schema_on_read_invalido(self):
        arquivo = (
            Path(self.temp.name) / "invalido.jsonl"
        )

        arquivo.write_text(
            '{"pedido_id": 1}\n',
            encoding="utf-8",
        )

        with self.assertRaises(ValueError):
            ler_pedidos_jsonl(arquivo)


if __name__ == "__main__":
    unittest.main()
