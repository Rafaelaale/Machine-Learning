import json
import unittest

import numpy as np
import pandas as pd

from pathlib import Path
from src.aula15_treinamento_sarimax import (
    RAIZ, ORDEM, ORDEM_SAZONAL, VARIAVEIS,
    carregar_dados, calcular_metrica,
    calcular_resultados, consolidar_previsoes,
)


class TestAula15(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.Xtr, cls.Xte, cls.ytr, cls.yte, cls.teste = (
            carregar_dados()
        )
        cls.previsoes = pd.read_csv(
            RAIZ / "resultados/aula15_previsoes_sarimax.csv",
            parse_dates=["data_hora"],
        )

    def test_01_ordem(self):
        self.assertEqual(ORDEM, (1, 1, 1))

    def test_02_sazonal(self):
        self.assertEqual(ORDEM_SAZONAL, (1, 0, 1, 7))

    def test_03_treino(self):
        self.assertEqual(self.Xtr.shape, (396, 12))

    def test_04_teste(self):
        self.assertEqual(self.Xte.shape, (60, 12))

    def test_05_alvos(self):
        self.assertEqual(len(self.ytr), 396)
        self.assertEqual(len(self.yte), 60)

    def test_06_colunas(self):
        self.assertEqual(self.Xtr.columns.tolist(), VARIAVEIS)
        self.assertEqual(self.Xte.columns.tolist(), VARIAVEIS)

    def test_07_previsoes(self):
        self.assertEqual(len(self.previsoes), 60)
        self.assertTrue(
            np.isfinite(self.previsoes["previsao_sarimax"]).all()
        )

    def test_08_datas(self):
        self.assertEqual(
            self.previsoes["data_hora"].tolist(),
            self.teste["data_hora"].tolist(),
        )

    def test_09_metricas(self):
        valores = calcular_metrica(
            self.previsoes["demanda"],
            self.previsoes["previsao_sarimax"],
        )
        self.assertEqual(set(valores), {"MAE", "RMSE", "MAPE"})
        self.assertTrue(all(np.isfinite(list(valores.values()))))

    def test_10_comparacao(self):
        _, comparacao, residuos = calcular_resultados(
            self.previsoes
        )
        self.assertEqual(len(comparacao), 4)
        self.assertEqual(len(residuos), 60)

    def test_11_consolidacao(self):
        dados = consolidar_previsoes(self.previsoes)
        self.assertEqual(dados.shape, (60, 6))

    def test_12_modelo_salvo(self):
        arquivo = RAIZ / "modelos/aula15_sarimax_111_1017.pkl"
        self.assertTrue(arquivo.is_file())
        self.assertGreater(arquivo.stat().st_size, 0)

    def test_13_relatorio(self):
        arquivo = RAIZ / "resultados/aula15_relatorio_sarimax.json"
        relatorio = json.loads(arquivo.read_text(encoding="utf-8"))
        self.assertEqual(relatorio["aula"], 15)
        self.assertEqual(len(relatorio["variaveis_externas"]), 12)

    def test_14_graficos(self):
        nomes = [
            "aula15_real_vs_sarimax.html",
            "aula15_comparacao_mape.html",
            "aula15_residuos_sarimax.html",
            "aula15_quatro_modelos.html",
        ]
        for nome in nomes:
            arquivo = RAIZ / "graficos" / nome
            self.assertTrue(arquivo.is_file())
            self.assertGreater(arquivo.stat().st_size, 0)


if __name__ == "__main__":
    unittest.main()
