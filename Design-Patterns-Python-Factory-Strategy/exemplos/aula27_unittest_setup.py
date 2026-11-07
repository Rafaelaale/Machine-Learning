"""Exemplo da transcricao: setUp em unittest."""

import unittest


class TestMinhaFuncionalidade(unittest.TestCase):

    def setUp(self):
        self.dados_teste = self.criar_dados_teste()

    def criar_dados_teste(self):
        return {
            "nome": "Teste",
            "idade": 30,
        }

    def test_algo(self):
        self.assertEqual(
            self.dados_teste["nome"],
            "Teste",
        )


if __name__ == "__main__":
    unittest.main()
