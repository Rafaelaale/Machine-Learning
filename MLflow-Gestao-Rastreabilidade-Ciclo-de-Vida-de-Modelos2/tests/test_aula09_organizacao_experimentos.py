"""Testes da organizacao de experimentos."""

import json
import unittest

import pandas as pd

from mlflow.tracking import MlflowClient

from src.aula09_organizacao_experimentos import (
    ARQUIVO_JSON,
    ARQUIVO_CSV,
    ARQUIVO_FILTRO,
    ARQUIVO_MD,
    COMMON_TAGS,
    HYPOTHESES,
    CHECKLIST,
    CODE_VERSION,
    MODELOS,
    calcular_fingerprint,
    criar_tags,
    carregar_runs_originais,
    consultar_organizadas,
    consultar_candidatos,
    configurar_tracking,
)


class TestAula09(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        configurar_tracking()

        cls.client = MlflowClient()

        cls.experimento, cls.runs = (
            carregar_runs_originais(cls.client)
        )

        cls.relatorio = json.loads(
            ARQUIVO_JSON.read_text(
                encoding="utf-8"
            )
        )

    def test_01_tres_modelos(self):
        self.assertEqual(
            set(self.runs),
            MODELOS,
        )

    def test_02_tags_comuns(self):
        self.assertEqual(
            len(COMMON_TAGS),
            7,
        )

    def test_03_tres_hipoteses(self):
        self.assertEqual(
            set(HYPOTHESES),
            MODELOS,
        )

    def test_04_checklist(self):
        self.assertEqual(
            len(CHECKLIST),
            8,
        )

    def test_05_codigo(self):
        self.assertEqual(
            CODE_VERSION,
            "not_available",
        )

    def test_06_fingerprint(self):
        valor = calcular_fingerprint()

        self.assertEqual(len(valor), 64)
        self.assertEqual(
            valor,
            self.relatorio[
                "code_fingerprint_sha256"
            ],
        )

    def test_07_tags_registradas(self):
        for nome, run in self.runs.items():
            atualizada = self.client.get_run(
                run.info.run_id
            )

            esperado = criar_tags(
                nome,
                calcular_fingerprint(),
            )

            for chave, valor in esperado.items():
                if chave == "selection_status":
                    arquivo_selecao = (
                        ARQUIVO_JSON.parent
                        / "aula10_escolha_campeao.json"
                    )

                    if arquivo_selecao.is_file():
                        selecao = json.loads(
                            arquivo_selecao.read_text(
                                encoding="utf-8"
                            )
                        )
                        campeao_id = selecao["champion"]["run_id"]
                        valor = (
                            "champion candidate"
                            if run.info.run_id == campeao_id
                            else "challenger"
                        )

                self.assertEqual(
                    atualizada.data.tags.get(chave),
                    valor,
                )

    def test_08_runs_finalizadas(self):
        for run in self.runs.values():
            self.assertEqual(
                run.info.status,
                "FINISHED",
            )

    def test_09_consulta_organizada(self):
        tabela = consultar_organizadas(
            self.experimento.experiment_id
        )

        self.assertEqual(
            len(tabela),
            3,
        )

    def test_10_filtro_roc(self):
        tabela = consultar_candidatos(
            self.experimento.experiment_id
        )

        if not tabela.empty:
            self.assertTrue(
                (
                    tabela["metrics.roc_auc_teste"]
                    >= 0.85
                ).all()
            )

    def test_11_arquivos(self):
        for arquivo in (
            ARQUIVO_JSON,
            ARQUIVO_CSV,
            ARQUIVO_FILTRO,
            ARQUIVO_MD,
        ):
            self.assertTrue(
                arquivo.is_file()
            )

    def test_12_sem_campeao(self):
        self.assertIsNone(
            self.relatorio["campeao_definitivo"]
        )

        self.assertEqual(
            self.relatorio["novas_runs"],
            0,
        )

        self.assertEqual(
            len(pd.read_csv(ARQUIVO_CSV)),
            3,
        )


if __name__ == "__main__":
    unittest.main()
