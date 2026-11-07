"""Aula 16 - Padrao Registry.

O registro associa nomes a classes Factory Method.

O laboratorio reutiliza as fabricas da Aula 14.
Nao executa pagamentos reais.
"""

from src.aula14_factory_method import (
    ServicoDePedidoFactory,
    PedidoPixFactory,
    PedidoCartaoFactory,
    PedidoBoletoFactory,
)


class Registry:
    """Registro de classes de fabricas de pedidos."""

    def __init__(self):
        self.mapa = {}

    def registrar(self, chave, classe):
        # Conforme a aula, uma chave duplicada
        # substitui o registro anterior.
        self.mapa[chave] = classe

    def criar(self, chave) -> ServicoDePedidoFactory:
        classe = self.mapa.get(chave)

        if not classe:
            raise ValueError("Tipo inválido")

        return classe()


def construir_registro():
    """Composition Root: registra as factories conhecidas."""
    registro = Registry()

    registro.registrar("pix", PedidoPixFactory)
    registro.registrar("cartao", PedidoCartaoFactory)
    registro.registrar("boleto", PedidoBoletoFactory)

    return registro


def finalizar_pagamento(registro, tipo, valor=100):
    """Cria um pedido pela chave e finaliza a simulacao."""
    pedido = registro.criar(tipo)
    pedido.finalizar_pedido(valor)
    return pedido


# Extensao didatica:
# duas classes novas sem modificar Registry.

class PagamentoTransferencia:
    def processar(self, valor):
        print(
            f"Pagamento via transferência de R$ {valor} processado."
        )


class PedidoTransferenciaFactory(ServicoDePedidoFactory):
    def criar_pagamento(self):
        return PagamentoTransferencia()


def demonstrar_registro_dinamico():
    registro = construir_registro()

    antes = sorted(registro.mapa)

    registro.registrar(
        "transferencia",
        PedidoTransferenciaFactory,
    )

    depois = sorted(registro.mapa)
    pedido = registro.criar("transferencia")

    return {
        "antes": antes,
        "depois": depois,
        "factory": type(pedido).__name__,
        "produto": type(pedido.criar_pagamento()).__name__,
        "registry_foi_modificado": False,
    }


def demonstrar_substituicao():
    registro = Registry()

    registro.registrar("especial", PedidoPixFactory)
    classe_antes = registro.mapa["especial"].__name__

    registro.registrar(
        "especial",
        PedidoCartaoFactory,
    )
    classe_depois = registro.mapa["especial"].__name__

    return {
        "classe_antes": classe_antes,
        "classe_depois": classe_depois,
        "total_chaves": len(registro.mapa),
        "sobrescreveu": classe_antes != classe_depois,
    }


def analisar_registry():
    return {
        "aula": 16,
        "titulo": "Registry",
        "metodos": ["registrar", "criar"],
        "tipos_iniciais": ["pix", "cartao", "boleto"],
        "registro_em_tempo_de_execucao": True,
        "permite_sobrescrever_chaves": True,
        "adicao_sem_editar_registry": True,
        "registro_por_decorator": False,
        "pagamentos_reais": False,
    }
