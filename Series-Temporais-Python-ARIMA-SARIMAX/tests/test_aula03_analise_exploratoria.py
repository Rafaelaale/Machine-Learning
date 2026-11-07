"""Testes da Aula 03."""
import unittest

from src.analise_exploratoria import (
    carregar_dados,
    agregar_dados,
    gerar_graficos,
    SERIE_DIARIA,
    RELATORIO,
    PASTA_GRAFICOS,
)


class TestAula03(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.df = carregar_dados()
        cls.diaria, cls.hora, cls.dia, cls.mes = (
            agregar_dados(cls.df)
        )

    def test_base(self):
        self.assertEqual(len(self.df), 10886)

    def test_serie_diaria(self):
        self.assertGreater(len(self.diaria), 0)

    def test_soma_demanda(self):
        self.assertEqual(
            int(self.df["demanda"].sum()),
            int(self.diaria["demanda_diaria"].sum()),
        )

    def test_horas(self):
        self.assertEqual(
            sorted(self.hora["hora"].tolist()),
            list(range(24)),
        )

    def test_dias_semana(self):
        self.assertEqual(len(self.dia), 7)

    def test_meses(self):
        self.assertEqual(len(self.mes), 12)

    def test_csv(self):
        self.assertTrue(SERIE_DIARIA.is_file())

    def test_graficos(self):
        self.assertTrue(RELATORIO.is_file())
        for numero in range(1, 6):
            self.assertEqual(
                len(list(PASTA_GRAFICOS.glob(
                    f"{numero:02d}_*.html"
                ))),
                1,
            )


if __name__ == "__main__":
    unittest.main()
