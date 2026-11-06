"""Testes da preparacao para Git e GitHub."""

import sys
import tempfile
import unittest
from pathlib import Path


BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from src.aula13_versionamento import (
    avaliar_arquivo,
    auditar_projeto,
    validar_nome_branch,
)


class TestVersionamento(unittest.TestCase):

    def test_01_branch_feature(self):
        self.assertTrue(
            validar_nome_branch("feature/preprocessamento")
        )

    def test_02_branch_fix(self):
        self.assertTrue(
            validar_nome_branch("fix/tratamento-nulos")
        )

    def test_03_branch_sem_tipo(self):
        self.assertFalse(
            validar_nome_branch("preprocessamento")
        )

    def test_04_branch_com_espacos(self):
        self.assertFalse(
            validar_nome_branch("feature/dados novos")
        )

    def test_05_codigo_candidato(self):
        self.assertEqual(
            avaliar_arquivo("src/core.py")["status"],
            "candidato",
        )

    def test_06_ambiente_virtual_bloqueado(self):
        self.assertEqual(
            avaliar_arquivo(".venv/Lib/modulo.py")["status"],
            "nao_publicar",
        )

    def test_07_arquivo_env_bloqueado(self):
        self.assertEqual(
            avaliar_arquivo("config/.env")["status"],
            "nao_publicar",
        )

    def test_08_chave_bloqueada(self):
        self.assertEqual(
            avaliar_arquivo("chaves/privada.pem")["status"],
            "nao_publicar",
        )

    def test_09_dataset_em_revisao(self):
        self.assertEqual(
            avaliar_arquivo("data/raw/clientes.csv")["status"],
            "revisar",
        )

    def test_10_modelo_binario_bloqueado(self):
        self.assertEqual(
            avaliar_arquivo("models/modelo.pkl")["status"],
            "nao_publicar",
        )

    def test_11_auditoria_reproduzivel(self):
        with tempfile.TemporaryDirectory() as pasta:
            raiz = Path(pasta)
            (raiz / "src").mkdir()
            (raiz / "src" / "app.py").write_text(
                "print('teste')",
                encoding="utf-8",
            )

            primeira = auditar_projeto(raiz)
            segunda = auditar_projeto(raiz)

            self.assertEqual(
                primeira["classificacao"],
                segunda["classificacao"],
            )
            self.assertEqual(primeira["total_arquivos"], 1)

    def test_12_pasta_inexistente(self):
        with tempfile.TemporaryDirectory() as pasta:
            ausente = Path(pasta) / "inexistente"

            with self.assertRaises(FileNotFoundError):
                auditar_projeto(ausente)


if __name__ == "__main__":
    unittest.main()
