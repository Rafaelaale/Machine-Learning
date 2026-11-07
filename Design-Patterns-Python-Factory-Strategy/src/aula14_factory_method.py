"""Aula 14 - Padrao Factory Method.

Define um metodo de criacao abstrato e permite
que subclasses escolham o objeto concreto.

Todos os pagamentos sao simulados.
"""

from abc import ABC, abstractmethod


class ServicoDePedidoFactory(ABC):
    """Creator abstrato do Factory Method."""

    @abstractmethod
    def criar_pagamento(self):
        """Factory Method: cria o servico adequado."""
        pass

    def finalizar_pedido(self, total):
        """Fluxo comum, independente do tipo de pagamento."""
        pagamento = self.criar_pagamento()
        pagamento.processar(total)


class PagamentoCartao:
    """Produto concreto: pagamento por cartao."""

    def processar(self, valor):
        print(
            f"Pagamento no cartão de R$ {valor} processado."
        )


class PagamentoPix:
    """Produto concreto: pagamento por PIX."""

    def processar(self, valor):
        print(
            f"Pagamento via PIX de R$ {valor} processado."
        )


class PedidoCartaoFactory(ServicoDePedidoFactory):
    """Concrete Creator para cartao."""

    def criar_pagamento(self):
        return PagamentoCartao()


class PedidoPixFactory(ServicoDePedidoFactory):
    """Concrete Creator para PIX."""

    def criar_pagamento(self):
        return PagamentoPix()


# EXTENSAO DIDATICA DO PADRAO
# Nao modifica nenhuma classe ja existente.

class PagamentoBoleto:
    def processar(self, valor):
        print(
            f"Pagamento via boleto de R$ {valor} processado."
        )


class PedidoBoletoFactory(ServicoDePedidoFactory):
    def criar_pagamento(self):
        return PagamentoBoleto()


def analisar_factory_method():
    return {
        "aula": 14,
        "padrao": "Factory Method",
        "criador_abstrato": "ServicoDePedidoFactory",
        "metodo_fabrica": "criar_pagamento",
        "metodo_comum": "finalizar_pedido",
        "fabricas": [
            "PedidoCartaoFactory",
            "PedidoPixFactory",
        ],
        "extensao_didatica": "PedidoBoletoFactory",
        "principio_open_closed": True,
        "necessita_editar_fabrica_existente_para_boleto": False,
        "criacao_dinamica_por_json": False,
        "pagamentos_reais": False,
    }
