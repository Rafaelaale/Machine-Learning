"""Testes do modelo conceitual Minishop."""

import sys
import unittest
from pathlib import Path


BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from src.aula04_modelo_conceitual import (
    ENTIDADES,
    RELACIONAMENTOS,
    REGRAS,
    PENDENCIAS,
    exportar_catalogo,
    obter_entidade,
    relacionamentos_de,
    validar_modelo,
)


class TestModeloConceitual(unittest.TestCase):

    def test_01_nove_entidades(self):
        self.assertEqual(len(ENTIDADES), 9)

    def test_02_oito_relacionamentos(self):
        self.assertEqual(len(RELACIONAMENTOS), 8)

    def test_03_modelo_valido(self):
        self.assertEqual(validar_modelo(), [])

    def test_04_cliente_com_email(self):
        cliente = obter_entidade("cliente")
        self.assertIn("email", cliente.atributos)

    def test_05_pedido_com_valor(self):
        pedido = obter_entidade("pedido")
        self.assertIn("valor", pedido.atributos)

    def test_06_categoria_presente(self):
        self.assertEqual(
            obter_entidade("categoria").nome,
            "categoria",
        )

    def test_07_movimento_presente(self):
        self.assertEqual(
            obter_entidade("movimento_inventario").nome,
            "movimento_inventario",
        )

    def test_08_entidade_inexistente(self):
        with self.assertRaises(KeyError):
            obter_entidade("entidade_inexistente")

    def test_09_cliente_faz_pedidos(self):
        relacoes = relacionamentos_de("cliente")
        self.assertTrue(any(
            r.destino == "pedido"
            and r.por_origem == "0..N"
            for r in relacoes
        ))

    def test_10_produto_pertence_categoria(self):
        relacoes = relacionamentos_de("produto")
        self.assertTrue(any(
            r.origem == "categoria"
            and r.por_destino == "1"
            for r in relacoes
        ))

    def test_11_regras_registradas(self):
        self.assertEqual(len(REGRAS), 8)
        self.assertIn("REGRA_06", REGRAS)

    def test_12_validacao_negocio_pendente(self):
        catalogo = exportar_catalogo()

        self.assertFalse(
            catalogo["modelo_aprovado_pelo_usuario"]
        )
        self.assertGreater(len(PENDENCIAS), 0)
        self.assertEqual(len(catalogo["entidades"]), 9)


if __name__ == "__main__":
    unittest.main()
