import sys
import unittest
from pathlib import Path


BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from src.aula04_sistemas_ml import (
    carregar_dados,
    validar_registro,
    previsao_tradicional,
    vetor,
    treinar_modelo,
    prever_ml,
    avaliar,
    detectar_mudanca_esquema,
    detectar_mudanca_media,
)


DADOS = BASE / "dados" / "aula04_churn_rotulado.csv"


class TestSistemasML(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.registros = carregar_dados(DADOS)
        cls.treino = [
            r for r in cls.registros
            if r["conjunto"] == "treino"
        ]
        cls.teste = [
            r for r in cls.registros
            if r["conjunto"] == "teste"
        ]
        cls.modelo = treinar_modelo(cls.treino)

    def test_carrega_dados(self):
        self.assertEqual(len(self.registros), 12)

    def test_particao_treinamento(self):
        self.assertEqual(len(self.treino), 8)

    def test_particao_teste(self):
        self.assertEqual(len(self.teste), 4)

    def test_regra_tradicional(self):
        self.assertEqual(
            previsao_tradicional(
                {"dias_sem_compra": 80, "reclamacoes_90d": 0}
            ),
            1,
        )

    def test_regra_cliente_ativo(self):
        self.assertEqual(
            previsao_tradicional(
                {"dias_sem_compra": 10, "reclamacoes_90d": 0}
            ),
            0,
        )

    def test_modelo_aprende_duas_classes(self):
        self.assertEqual(
            len(self.modelo["centroides"]), 2
        )

    def test_previsao_ml(self):
        self.assertEqual(
            prever_ml(self.modelo, self.teste[0]), 0
        )

    def test_avaliacao_ml(self):
        resultado = avaliar(
            self.teste,
            lambda r: prever_ml(self.modelo, r),
        )
        self.assertEqual(resultado["amostras"], 4)
        self.assertGreaterEqual(resultado["acuracia"], 0.75)

    def test_esquema_incompleto(self):
        resultado = detectar_mudanca_esquema(
            {"dias_sem_compra": 20}
        )
        self.assertFalse(resultado["esquema_valido"])
        self.assertIn(
            "reclamacoes_90d",
            resultado["colunas_ausentes"],
        )

    def test_falha_controlada_por_coluna_ausente(self):
        with self.assertRaises(ValueError):
            prever_ml(
                self.modelo, {"dias_sem_compra": 20}
            )

    def test_valor_negativo(self):
        with self.assertRaises(ValueError):
            validar_registro({
                "dias_sem_compra": -2,
                "reclamacoes_90d": 0,
            })

    def test_rotulo_invalido(self):
        with self.assertRaises(ValueError):
            validar_registro({
                "dias_sem_compra": 10,
                "reclamacoes_90d": 0,
                "churn": 5,
            }, exigir_rotulo=True)

    def test_treino_sem_duas_classes(self):
        apenas_classe_zero = [
            r for r in self.treino if r["churn"] == 0
        ]
        with self.assertRaises(ValueError):
            treinar_modelo(apenas_classe_zero)

    def test_alerta_de_mudanca(self):
        novos = [
            {"dias_sem_compra": 140, "reclamacoes_90d": 0}
        ]
        resultado = detectar_mudanca_media(
            self.treino, novos
        )
        self.assertTrue(resultado["alerta"])

    def test_avaliacao_vazia(self):
        with self.assertRaises(ValueError):
            avaliar([], previsao_tradicional)


if __name__ == "__main__":
    unittest.main()