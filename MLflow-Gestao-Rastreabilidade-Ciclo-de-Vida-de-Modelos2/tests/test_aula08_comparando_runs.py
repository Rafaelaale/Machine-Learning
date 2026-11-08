"""Testes da comparacao de runs."""

import json
import unittest

import pandas as pd

from src.aula08_comparando_runs import (
    CSV_RANKING,
    CSV_PAPEIS,
    CSV_SHORTLIST,
    CSV_RIGOROSA,
    JSON_RESUMO,
    MD_RESUMO,
    CANDIDATOS,
    COMPARISON_COLS,
    EXPERIMENT_NAME,
    consultar_experimento,
    criar_ranking,
    buscar_shortlist,
)


class TestAula08(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.experimento, cls.runs = (
            consultar_experimento()
        )

        cls.ranking, cls.papeis = criar_ranking(
            cls.runs
        )

        cls.resumo = json.loads(
            JSON_RESUMO.read_text(encoding="utf-8")
        )

    def test_01_experimento(self):
        self.assertEqual(
            self.experimento.name,
            EXPERIMENT_NAME,
        )

    def test_02_tres_runs(self):
        self.assertEqual(len(self.runs), 3)

    def test_03_candidatos(self):
        self.assertEqual(
            set(self.ranking["params.candidate_name"]),
            CANDIDATOS,
        )

    def test_04_colunas(self):
        self.assertEqual(
            list(self.ranking.columns),
            COMPARISON_COLS,
        )

    def test_05_ranking_ordenado(self):
        valores = (
            self.ranking["metrics.roc_auc_teste"]
            .tolist()
        )

        self.assertEqual(
            valores,
            sorted(valores, reverse=True),
        )

    def test_06_papeis(self):
        self.assertEqual(
            self.papeis.iloc[0]["candidate_role"],
            "champion_candidate",
        )

        self.assertEqual(
            list(self.papeis["candidate_role"]).count(
                "challenger"
            ),
            2,
        )

    def test_07_shortlist_inicial(self):
        tabela = buscar_shortlist(
            self.experimento.experiment_id,
            0.70,
        )

        if not tabela.empty:
            self.assertTrue(
                (tabela["metrics.roc_auc_teste"] >= 0.85).all()
            )

            self.assertTrue(
                (tabela["metrics.recall_inadimplente"] >= 0.70).all()
            )

    def test_08_shortlist_rigorosa(self):
        tabela = buscar_shortlist(
            self.experimento.experiment_id,
            0.85,
        )

        if not tabela.empty:
            self.assertTrue(
                (tabela["metrics.recall_inadimplente"] >= 0.85).all()
            )

    def test_09_listas_consistentes(self):
        inicial = buscar_shortlist(
            self.experimento.experiment_id, 0.70
        )

        rigorosa = buscar_shortlist(
            self.experimento.experiment_id, 0.85
        )

        self.assertTrue(
            set(rigorosa["run_id"]).issubset(
                set(inicial["run_id"])
            )
        )

    def test_10_arquivos(self):
        for arquivo in (
            CSV_RANKING,
            CSV_PAPEIS,
            CSV_SHORTLIST,
            CSV_RIGOROSA,
            JSON_RESUMO,
            MD_RESUMO,
        ):
            self.assertTrue(arquivo.is_file())

    def test_11_csv_e_json(self):
        tabela = pd.read_csv(CSV_RANKING)

        self.assertEqual(len(tabela), 3)

        self.assertEqual(
            self.resumo["total_runs_comparadas"],
            3,
        )

    def test_12_sem_selecao_definitiva(self):
        self.assertFalse(
            self.resumo[
                "campeao_definitivo_selecionado"
            ]
        )

        self.assertEqual(
            self.resumo["novas_runs_criadas"],
            0,
        )


if __name__ == "__main__":
    unittest.main()
