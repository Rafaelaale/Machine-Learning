"""Aula 13 - Simple Factory.

Duas implementacoes:
1. Factory por funcao.
2. Factory por classe com metodo estatico.

Os pagamentos sao apenas simulacoes.
"""

from typing import Protocol


class ServicoDePagamento(Protocol):
    """Contrato estrutural dos servicos de pagamento."""

    def processar(self, valor) -> None:
        ...


class ServicoDeCartao:
    def processar(self, valor):
        print(f"Pagamento de R$ {valor} processado.")


class ServicoDePix:
    def processar(self, valor):
        print(
            f"Pagamento via PIX de R$ {valor} processado."
        )


# PRIMEIRA VERSAO: FACTORY POR FUNCAO

def criar_servico_pagamento(tipo):
    """Centraliza a escolha da classe concreta."""

    if tipo == "cartao":
        return ServicoDeCartao()
    elif tipo == "pix":
        return ServicoDePix()
    else:
        raise ValueError("Tipo de pagamento inválido")


class ServicoDePedidoComFuncao:
    """Usa a fabrica por funcao."""

    def __init__(self, tipo_pagamento):
        self.pagamento = criar_servico_pagamento(
            tipo_pagamento
        )

    def finalizar_pedido(self, total):
        self.pagamento.processar(total)


# SEGUNDA VERSAO: FACTORY POR CLASSE

class FabricaDePagamento:
    @staticmethod
    def criar(tipo):
        if tipo == "cartao":
            return ServicoDeCartao()
        elif tipo == "pix":
            return ServicoDePix()
        else:
            raise ValueError(
                "Tipo de pagamento inválido"
            )


class ServicoDePedido:
    """Usa a fabrica por classe.

    A classe nao cria diretamente
    ServicoDeCartao ou ServicoDePix.
    """

    def __init__(self, tipo_pagamento):
        self.pagamento = FabricaDePagamento.criar(
            tipo_pagamento
        )

    def finalizar_pedido(self, total):
        self.pagamento.processar(total)


def analisar_simple_factory():
    return {
        "aula": 13,
        "padrao": "Simple Factory",
        "implementacoes": [
            "Funcao",
            "Classe com metodo estatico",
        ],
        "tipos_suportados": ["cartao", "pix"],
        "criacao_centralizada": True,
        "pedido_instancia_servicos_concretos": False,
        "factory_precisa_mudar_para_novos_tipos": True,
        "pagamentos_reais": False,
    }
