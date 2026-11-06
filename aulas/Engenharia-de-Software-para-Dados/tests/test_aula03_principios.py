import sys
import unittest
from pathlib import Path


BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from src.aula03_principios import (
    carregar_clientes_produtos,
    resolver_produto,
    classificar_com_parametros,
    analisar_portfolio,
    resumir_portfolio,
    comparar_hipoteses,
)


DADOS = BASE / "dados" / "aula03_clientes_produtos.csv"

CATALOGO = {
    "P100": "Eletronicos",
    "P200": "Livros",
    "P300": "Vestuario",
}


class TestPrincipiosQuatroASete(unittest.TestCase):

    def setUp(self):
        self.clientes = carregar_clientes_produtos(DADOS)

    def test_carregamento(self):
        self.assertEqual(len(self.clientes), 8)

    def test_produtos_distintos(self):
        codigos = {
            item["produto_codigo"]
            for item in self.clientes
        }
        self.assertEqual(len(codigos), 3)

    def test_resolucao_produto(self):
        self.assertEqual(
            resolver_produto("P100", CATALOGO),
            "Eletronicos",
        )

    def test_novo_produto_sem_modificar_funcao(self):
        catalogo = {**CATALOGO, "P400": "Digital"}
        self.assertEqual(
            resolver_produto("P400", catalogo),
            "Digital",
        )

    def test_produto_desconhecido(self):
        self.assertEqual(
            resolver_produto("P999", CATALOGO),
            "PRODUTO_NAO_CADASTRADO",
        )

    def test_classificacao_inatividade(self):
        self.assertEqual(
            classificar_com_parametros(self.clientes[1]),
            "REVISAR_RELACIONAMENTO",
        )

    def test_classificacao_reclamacoes(self):
        self.assertEqual(
            classificar_com_parametros(self.clientes[2]),
            "REVISAR_RELACIONAMENTO",
        )

    def test_limite_invalido(self):
        with self.assertRaises(ValueError):
            classificar_com_parametros(
                self.clientes[0], limite_dias=-1
            )

    def test_analise_todos_produtos(self):
        resultados = analisar_portfolio(
            self.clientes, CATALOGO
        )
        self.assertEqual(len(resultados), 8)

    def test_resumo_portfolio(self):
        resultados = analisar_portfolio(
            self.clientes, CATALOGO
        )
        resumo = resumir_portfolio(resultados)

        self.assertEqual(len(resumo), 3)
        self.assertEqual(
            sum(item["revisar"] for item in resumo.values()),
            4,
        )

    def test_tres_hipoteses(self):
        hipoteses = comparar_hipoteses(
            self.clientes, CATALOGO, [30, 60, 90]
        )
        self.assertEqual(len(hipoteses), 3)

    def test_hipoteses_vazias(self):
        with self.assertRaises(ValueError):
            comparar_hipoteses(
                self.clientes, CATALOGO, []
            )


if __name__ == "__main__":
    unittest.main()