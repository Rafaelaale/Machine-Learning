"""Testes da Aula 14 - preparacao SARIMAX."""

import json
import unittest

import numpy as np
import pandas as pd

from src.aula14_preparacao_exogenas_sarimax import (
    carregar_base_horaria,
    validar_calendario,
    agregar_base_diaria,
    preparar_base_modelagem,
    separar_dados,
    verificar_compatibilidade,
    diagnosticar_calendario,
    grafico_clima,
    grafico_divisao,
    VARIAVEIS_EXTERNAS,
    DUMMIES_ESPERADAS,
    CSV_BASE_DIARIA,
    CSV_BASE_MODELAGEM,
    CSV_TREINO,
    CSV_TESTE,
    CSV_X_TREINO,
    CSV_X_TESTE,
    CSV_Y_TREINO,
    CSV_Y_TESTE,
    CSV_VALIDACAO_CALENDARIO,
    JSON_RELATORIO,
    HTML_CLIMA,
    HTML_TREINO_TESTE,
)


class TestAula14(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.df = carregar_base_horaria()

        cls.validacao = validar_calendario(
            cls.df
        )

        cls.diaria = agregar_base_diaria(
            cls.df
        )

        (
            cls.modelagem,
            cls.dummies,
            cls.externas,
        ) = preparar_base_modelagem(
            cls.diaria
        )

        (
            cls.treino,
            cls.teste,
            cls.y_treino,
            cls.y_teste,
            cls.X_treino,
            cls.X_teste,
        ) = separar_dados(
            cls.modelagem,
            cls.externas,
        )

    def test_01_base_horaria(self):
        self.assertEqual(
            len(self.df),
            10886,
        )

    def test_02_colunas_contexto(self):
        self.assertEqual(
            len(self.df.columns),
            10,
        )

    def test_03_calendario_constante(self):
        self.assertTrue(
            (self.validacao == 1).all().all()
        )

    def test_04_dias_observados(self):
        self.assertEqual(
            len(self.diaria),
            456,
        )

    def test_05_demanda_preservada(self):
        self.assertAlmostEqual(
            float(self.df["demanda"].sum()),
            float(self.diaria["demanda"].sum()),
        )

    def test_06_colunas_climaticas(self):
        for nome in (
            "temperatura_media",
            "sensacao_termica_media",
            "umidade_media",
            "velocidade_vento_media",
        ):
            self.assertIn(
                nome,
                self.diaria.columns,
            )

    def test_07_calendario_diario(self):
        for nome in (
            "feriado",
            "dia_util",
            "dia_semana",
            "mes",
        ):
            self.assertIn(
                nome,
                self.diaria.columns,
            )

    def test_08_seis_dummies(self):
        self.assertEqual(
            self.dummies.columns.tolist(),
            DUMMIES_ESPERADAS,
        )

    def test_09_variaveis_externas(self):
        self.assertEqual(
            self.externas,
            VARIAVEIS_EXTERNAS,
        )
        self.assertEqual(
            len(self.externas),
            12,
        )

    def test_10_sem_demanda_em_X(self):
        self.assertNotIn(
            "demanda",
            self.X_treino.columns,
        )
        self.assertNotIn(
            "mes",
            self.X_treino.columns,
        )

    def test_11_divisao_temporal(self):
        self.assertEqual(
            len(self.treino),
            396,
        )
        self.assertEqual(
            len(self.teste),
            60,
        )
        self.assertLess(
            self.treino["data_hora"].max(),
            self.teste["data_hora"].min(),
        )

    def test_12_formato_X(self):
        self.assertEqual(
            self.X_treino.shape,
            (396, 12),
        )
        self.assertEqual(
            self.X_teste.shape,
            (60, 12),
        )

    def test_13_formato_y(self):
        self.assertEqual(
            self.y_treino.shape,
            (396,),
        )
        self.assertEqual(
            self.y_teste.shape,
            (60,),
        )
        self.assertTrue(
            np.isfinite(self.y_treino).all()
        )
        self.assertTrue(
            np.isfinite(self.X_treino).all().all()
        )

    def test_14_mesmo_teste_anterior(self):
        self.assertTrue(
            verificar_compatibilidade(
                self.treino,
                self.teste,
            )
        )

    def test_15_graficos_e_calendario(self):
        self.assertEqual(
            len(grafico_clima(self.diaria).data),
            2,
        )
        self.assertEqual(
            len(grafico_divisao(
                self.treino,
                self.teste,
            ).data),
            2,
        )
        diagnostico = diagnosticar_calendario(
            self.diaria
        )
        self.assertGreater(
            diagnostico["dias_ausentes"],
            0,
        )

    def test_16_arquivos_e_relatorio(self):
        for arquivo in (
            CSV_BASE_DIARIA,
            CSV_BASE_MODELAGEM,
            CSV_TREINO,
            CSV_TESTE,
            CSV_X_TREINO,
            CSV_X_TESTE,
            CSV_Y_TREINO,
            CSV_Y_TESTE,
            CSV_VALIDACAO_CALENDARIO,
            JSON_RELATORIO,
            HTML_CLIMA,
            HTML_TREINO_TESTE,
        ):
            self.assertTrue(
                arquivo.is_file(),
                str(arquivo),
            )
            self.assertGreater(
                arquivo.stat().st_size,
                0,
            )

        relatorio = json.loads(
            JSON_RELATORIO.read_text(
                encoding="utf-8"
            )
        )

        self.assertEqual(
            relatorio["aula"],
            14,
        )
        self.assertFalse(
            relatorio["sarimax_treinado"]
        )
        self.assertEqual(
            relatorio["quantidade_variaveis_externas"],
            12,
        )


if __name__ == "__main__":
    unittest.main()
