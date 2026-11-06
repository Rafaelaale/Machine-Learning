import sys
import unittest
from pathlib import Path


BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from src.aula02_churn import (
    carregar_clientes,
    validar_cliente,
    classificar_atencao,
    analisar_clientes,
    resumir,
)


DADOS = BASE / "dados" / "aula02_clientes_ficticios.csv"


class TestPrincipiosEngenharia(unittest.TestCase):

    def setUp(self):
        self.clientes = carregar_clientes(DADOS)

    def test_carregamento_dados(self):
        self.assertEqual(len(self.clientes), 8)

    def test_identificador(self):
        self.assertEqual(
            self.clientes[0]["cliente_id"], "C001"
        )

    def test_classificacao_por_inatividade(self):
        self.assertEqual(
            classificar_atencao(self.clientes[1]),
            "REVISAR_RELACIONAMENTO"
        )

    def test_classificacao_por_reclamacoes(self):
        self.assertEqual(
            classificar_atencao(self.clientes[2]),
            "REVISAR_RELACIONAMENTO"
        )

    def test_acompanhamento_normal(self):
        self.assertEqual(
            classificar_atencao(self.clientes[0]),
            "ACOMPANHAMENTO_NORMAL"
        )

    def test_validacao_valores_negativos(self):
        registro = {
            "cliente_id": "TESTE",
            "dias_sem_compra": "-1",
            "compras_90d": "0",
            "reclamacoes_90d": "0",
            "valor_total": "100",
        }
        with self.assertRaises(ValueError):
            validar_cliente(registro)

    def test_total_classificacoes(self):
        resultados = analisar_clientes(self.clientes)
        resumo = resumir(resultados)

        self.assertEqual(
            resumo["clientes_para_revisao"], 4
        )
        self.assertEqual(
            resumo["acompanhamento_normal"], 4
        )

    def test_percentual(self):
        resultados = analisar_clientes(self.clientes)
        resumo = resumir(resultados)

        self.assertEqual(
            resumo["percentual_revisao"], 50.0
        )

    def test_lista_vazia(self):
        resumo = resumir([])

        self.assertEqual(
            resumo["total_clientes"], 0
        )
        self.assertEqual(
            resumo["percentual_revisao"], 0.0
        )


if __name__ == "__main__":
    unittest.main()