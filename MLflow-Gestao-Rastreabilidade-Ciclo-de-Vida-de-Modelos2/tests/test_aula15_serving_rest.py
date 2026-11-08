"""Testes do serving REST local."""

import json
import unittest

import numpy as np
import requests

from src.aula15_serving_rest import (
    MODEL_URI,
    BASE_URL,
    RELATORIO_JSON,
    RESPOSTAS_JSON,
    PREVISOES_CSV,
    RELATORIO_MD,
    PAYLOAD_JSON,
    PAYLOAD_INVALIDO_JSON,
    COLUNAS,
    CAMPOS_RESPOSTA,
    criar_payload,
    chamar_api,
    extrair_predicao,
    conferir_modelo_registrado,
)


class TestAula15(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.dados = json.loads(
            RELATORIO_JSON.read_text(
                encoding="utf-8"
            )
        )

    def test_01_model_uri(self):
        self.assertEqual(
            self.dados["model_uri"],
            MODEL_URI,
        )

    def test_02_registry(self):
        versao = conferir_modelo_registrado()

        self.assertEqual(
            versao["version"],
            self.dados["model_version"],
        )

    def test_03_payload_colunas(self):
        payload = criar_payload(0.30)

        self.assertEqual(
            payload["dataframe_split"]["columns"],
            COLUNAS,
        )

    def test_04_payload_linha(self):
        payload = criar_payload(0.30)

        self.assertEqual(
            len(payload["dataframe_split"]["data"]),
            1,
        )

    def test_05_payload_threshold(self):
        self.assertAlmostEqual(
            criar_payload(0.40)["params"]["threshold"],
            0.40,
        )

    def test_06_threshold_invalido(self):
        with self.assertRaises(ValueError):
            criar_payload(1.5)

    def test_07_ping(self):
        resposta = requests.get(
            f"{BASE_URL}/ping",
            timeout=15,
        )

        self.assertEqual(
            resposta.status_code,
            200,
        )

    def test_08_health(self):
        resposta = requests.get(
            f"{BASE_URL}/health",
            timeout=15,
        )

        self.assertEqual(
            resposta.status_code,
            200,
        )

    def test_09_version(self):
        resposta = requests.get(
            f"{BASE_URL}/version",
            timeout=15,
        )

        self.assertEqual(
            resposta.status_code,
            200,
        )

    def test_10_http_inferencia(self):
        resposta = chamar_api(
            criar_payload(0.30)
        )

        self.assertEqual(
            resposta["status_code"],
            200,
        )

        self.assertIn(
            "predictions",
            resposta["body"],
        )

    def test_11_formato_resposta(self):
        predicao = extrair_predicao(
            chamar_api(criar_payload(0.50))
        )

        self.assertEqual(
            list(predicao.keys()),
            CAMPOS_RESPOSTA,
        )

    def test_12_probabilidades(self):
        previsoes = self.dados["previsoes"]

        self.assertEqual(
            len(previsoes),
            3,
        )

        probabilidades = [
            item["probabilidade_inadimplencia"]
            for item in previsoes
        ]

        self.assertTrue(
            np.allclose(
                probabilidades,
                probabilidades[0],
                atol=1e-10,
                rtol=0,
            )
        )

    def test_13_entrada_invalida(self):
        resposta = chamar_api(
            criar_payload(
                remover_coluna="score_interno"
            )
        )

        self.assertGreaterEqual(
            resposta["status_code"],
            400,
        )

        self.assertLess(
            resposta["status_code"],
            500,
        )

        self.assertIn(
            "score_interno",
            json.dumps(resposta["body"]),
        )

    def test_14_arquivos(self):
        for arquivo in (
            RELATORIO_JSON,
            RESPOSTAS_JSON,
            PREVISOES_CSV,
            RELATORIO_MD,
            PAYLOAD_JSON,
            PAYLOAD_INVALIDO_JSON,
        ):
            self.assertTrue(arquivo.is_file())

            self.assertGreater(
                arquivo.stat().st_size,
                0,
            )

    def test_15_consistencia(self):
        self.assertTrue(
            self.dados[
                "predicoes_conferidas_com_modelo"
            ]
        )

    def test_16_sem_novos_treinamentos(self):
        self.assertEqual(
            self.dados["novas_runs"],
            0,
        )

        self.assertEqual(
            self.dados["novas_versoes"],
            0,
        )

        self.assertEqual(
            self.dados["novos_treinamentos"],
            0,
        )


if __name__ == "__main__":
    unittest.main()
