"""16 testes da Aula 26 - Funcoes de primeira classe."""

import inspect
import sys
import unittest
from pathlib import Path


RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from src.aula26_funcoes_lambdas import (
    calcular_preco,
    desconto_vip,
    desconto_novo,
    desconto_funcionario,
    sem_desconto,
    desconto_estudante,
    black_friday,
    parceria_empresa_x,
    parceria_empresa_y,
    soma,
    ESTRATEGIAS,
    criar_estrategia_percentual,
    demonstrar_primeira_classe,
    demonstrar_lambda_direta,
    demonstrar_divergencia_black_friday,
    analisar_aula26,
)


class TestFuncoesLambdas(unittest.TestCase):

    def test_01_desconto_vip(self):
        self.assertAlmostEqual(
            calcular_preco(200, desconto_vip), 160
        )

    def test_02_desconto_novo(self):
        self.assertAlmostEqual(
            calcular_preco(200, desconto_novo), 180
        )

    def test_03_desconto_funcionario(self):
        self.assertAlmostEqual(
            calcular_preco(200, desconto_funcionario), 140
        )

    def test_04_sem_desconto(self):
        self.assertEqual(
            calcular_preco(200, sem_desconto), 200
        )

    def test_05_desconto_estudante(self):
        self.assertAlmostEqual(
            calcular_preco(200, desconto_estudante), 170
        )

    def test_06_black_friday_ate_500(self):
        self.assertAlmostEqual(
            calcular_preco(200, black_friday), 100
        )
        self.assertAlmostEqual(
            calcular_preco(500, black_friday), 250
        )

    def test_07_black_friday_acima_500(self):
        # Segue a formula literal da transcricao.
        self.assertAlmostEqual(
            calcular_preco(600, black_friday), 540
        )
        self.assertAlmostEqual(
            calcular_preco(501, black_friday), 450.9
        )

    def test_08_parceria_empresa_x(self):
        self.assertAlmostEqual(
            calcular_preco(200, parceria_empresa_x), 160
        )

    def test_09_parceria_empresa_y(self):
        self.assertAlmostEqual(
            calcular_preco(200, parceria_empresa_y), 165
        )

    def test_10_lambda_soma(self):
        self.assertEqual(soma(3, 5), 8)
        self.assertEqual(soma(-2, 7), 5)
        self.assertEqual(soma.__name__, "<lambda>")

    def test_11_lambda_direta(self):
        self.assertAlmostEqual(
            demonstrar_lambda_direta(), 225
        )
        self.assertAlmostEqual(
            calcular_preco(
                300,
                lambda total: total * 0.75,
            ),
            225,
        )

    def test_12_funcoes_sao_primeira_classe(self):
        resultado = demonstrar_primeira_classe()

        self.assertEqual(resultado["preco_vip"], 160)
        self.assertEqual(resultado["preco_novo"], 180)
        self.assertEqual(
            resultado["precos_lista"],
            [160.0, 180.0, 200],
        )

    def test_13_estrategias_em_dicionario(self):
        self.assertEqual(len(ESTRATEGIAS), 8)

        for estrategia in ESTRATEGIAS.values():
            self.assertTrue(callable(estrategia))

        self.assertAlmostEqual(
            calcular_preco(200, ESTRATEGIAS["vip"]),
            160,
        )
        self.assertAlmostEqual(
            calcular_preco(200, ESTRATEGIAS["empresa_x"]),
            160,
        )

    def test_14_funcao_retorna_funcao(self):
        estrategia = criar_estrategia_percentual(0.6)

        self.assertTrue(callable(estrategia))
        self.assertAlmostEqual(
            calcular_preco(200, estrategia), 120
        )

        outra = criar_estrategia_percentual(0.75)

        self.assertAlmostEqual(
            calcular_preco(200, outra), 150
        )

    def test_15_calcular_preco_delega_sem_if(self):
        codigo = inspect.getsource(calcular_preco)

        self.assertIn("estrategia(total)", codigo)
        self.assertNotIn("if ", codigo)
        self.assertNotIn("elif ", codigo)

        chamadas = []

        def estrategia_personalizada(total):
            chamadas.append(total)
            return 42

        resultado = calcular_preco(
            100,
            estrategia_personalizada,
        )

        self.assertEqual(resultado, 42)
        self.assertEqual(chamadas, [100])

    def test_16_divergencia_e_analise(self):
        divergencia = demonstrar_divergencia_black_friday()
        analise = analisar_aula26()

        self.assertEqual(analise["aula"], 26)
        self.assertEqual(analise["padrao"], "Strategy")
        self.assertTrue(
            analise["funcoes_primeira_classe"]
        )
        self.assertTrue(analise["lambda"])
        self.assertFalse(
            analise["usa_classes_de_estrategia"]
        )

        self.assertEqual(
            divergencia["resultado_formula_transcrita"],
            540,
        )
        self.assertEqual(
            divergencia["resultado_citado_na_transcricao"],
            270,
        )
        self.assertAlmostEqual(
            divergencia["formula_da_aula_24_para_600"],
            270,
        )
        self.assertFalse(
            divergencia["valores_coincidem"]
        )


if __name__ == "__main__":
    unittest.main()
