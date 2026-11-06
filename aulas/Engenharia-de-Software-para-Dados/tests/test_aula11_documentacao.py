"""Testes de documentacao e consistencia da Aula 11."""

import json
import sys
import tempfile
import unittest
from pathlib import Path


BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from src.aula11_documentacao import (
    DOCUMENTOS,
    verificar_documentos,
    verificar_links_readme,
    verificar_termos_essenciais,
)


CHURN = BASE / "projetos" / "churn_profissional"


class TestDocumentacao(unittest.TestCase):

    def test_01_documentos_presentes(self):
        self.assertTrue(verificar_documentos(CHURN)["aprovado"])

    def test_02_quantidade_documentos(self):
        self.assertEqual(
            verificar_documentos(CHURN)["total_esperado"],
            8,
        )

    def test_03_readme_nao_vazio(self):
        self.assertGreater(
            (CHURN / "README.md").stat().st_size,
            100,
        )

    def test_04_links_validos(self):
        self.assertTrue(
            verificar_links_readme(CHURN)["aprovado"]
        )

    def test_05_resumo_com_termos_essenciais(self):
        self.assertTrue(
            verificar_termos_essenciais(CHURN)["aprovado"]
        )

    def test_06_detectar_documento_ausente(self):
        with tempfile.TemporaryDirectory() as pasta:
            resultado = verificar_documentos(Path(pasta))
            self.assertFalse(resultado["aprovado"])
            self.assertIn(
                "README.md",
                resultado["ausentes"],
            )

    def test_07_detectar_documento_vazio(self):
        with tempfile.TemporaryDirectory() as pasta:
            raiz = Path(pasta)
            (raiz / "README.md").write_text(
                "", encoding="utf-8"
            )

            resultado = verificar_documentos(raiz)
            self.assertIn("README.md", resultado["vazios"])

    def test_08_detectar_link_quebrado(self):
        with tempfile.TemporaryDirectory() as pasta:
            raiz = Path(pasta)

            (raiz / "README.md").write_text(
                "[Arquivo](ausente.md)",
                encoding="utf-8",
            )

            resultado = verificar_links_readme(raiz)
            self.assertFalse(resultado["aprovado"])

    def test_09_validar_link_existente(self):
        with tempfile.TemporaryDirectory() as pasta:
            raiz = Path(pasta)

            (raiz / "arquivo.md").write_text(
                "Conteudo", encoding="utf-8"
            )
            (raiz / "README.md").write_text(
                "[Arquivo](arquivo.md)",
                encoding="utf-8",
            )

            resultado = verificar_links_readme(raiz)
            self.assertTrue(resultado["aprovado"])

    def test_10_dados_origem(self):
        caminho = (
            CHURN / "data" / "raw" / "dados_corretos2.csv"
        )
        self.assertTrue(caminho.is_file())

    def test_11_pacote_documentado(self):
        conteudo = (
            CHURN / "doc" / "ARQUITETURA.md"
        ).read_text(encoding="utf-8")

        self.assertIn("pre_processamento", conteudo)
        self.assertIn("PreProcessamento", conteudo)

    def test_12_limitacao_registrada(self):
        conteudo = (
            CHURN / "doc" / "REGRAS_NEGOCIO.md"
        ).read_text(encoding="utf-8")

        self.assertIn("Recall", conteudo)
        self.assertIn("0.0", conteudo)

    def test_13_metricas_batem_com_relatorio(self):
        caminho = (
            BASE / "resultados"
            / "aula07_codigo_limpo_churn.json"
        )

        relatorio = json.loads(
            caminho.read_text(encoding="utf-8")
        )

        metricas = relatorio["pipeline"]["metricas"]

        self.assertAlmostEqual(
            metricas["accuracy"], 0.698, places=3
        )
        self.assertEqual(
            metricas["1"]["recall"], 0.0
        )

    def test_14_regras_documentadas(self):
        conteudo = (
            CHURN / "doc" / "REGRAS_NEGOCIO.md"
        ).read_text(encoding="utf-8")

        self.assertIn("days_since_last_purchase >= 60", conteudo)
        self.assertIn("num_orders <= 2", conteudo)

    def test_15_responsaveis_nao_inventados(self):
        conteudo = (
            CHURN / "doc" / "RESPONSABILIDADES.md"
        ).read_text(encoding="utf-8")

        self.assertIn("A definir", conteudo)

    def test_16_licenca_nao_inventada(self):
        conteudo = (
            CHURN / "doc" / "LICENCIAMENTO.md"
        ).read_text(encoding="utf-8")

        self.assertIn(
            "ainda nao definida",
            conteudo,
        )


if __name__ == "__main__":
    unittest.main()
