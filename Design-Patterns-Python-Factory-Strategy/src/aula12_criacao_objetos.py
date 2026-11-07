"""Aula 12 - Criando objetos do jeito errado.

Mostra:
1. Criacao rigida do servico de pagamento.
2. Escolha condicional entre cartao e PIX.
3. Alto acoplamento entre pedido e pagamentos.

Todos os pagamentos sao simulados com print.
Nao existem transacoes financeiras reais.
"""


# VERSAO 1 - CRIACAO RIGIDA

class ServicoDePagamento:
    """Servico de pagamento com cartao."""

    def processar(self, valor):
        print(f"Pagamento de R$ {valor} processado.")


class ServicoDePedidoRigido:
    """O pedido cria sua dependencia internamente."""

    def __init__(self):
        self.pagamento = ServicoDePagamento()

    def finalizar_pedido(self, total):
        self.pagamento.processar(total)


# VERSAO 2 - ESCOLHA CONDICIONAL

class ServicoDePix:
    """Servico de pagamento via PIX."""

    def processar(self, valor):
        print(f"Pagamento via PIX de R$ {valor} processado.")


class ServicoDePedido:
    """Escolhe o tipo de pagamento no construtor.

    A classe ainda conhece as implementacoes
    concretas e precisa ser alterada sempre
    que novos tipos de pagamento forem incluidos.
    """

    def __init__(self, tipo_pagamento="cartao"):
        if tipo_pagamento == "cartao":
            self.pagamento = ServicoDePagamento()
        elif tipo_pagamento == "pix":
            self.pagamento = ServicoDePix()
        else:
            raise ValueError("Tipo de pagamento inválido")

        self.tipo_pagamento = tipo_pagamento

    def finalizar_pedido(self, total):
        self.pagamento.processar(total)


def analisar_acoplamento():
    """Descreve as limitacoes observadas na aula."""
    return {
        "abordagem_rigida": {
            "pedido_cria_dependencia": True,
            "aceita_pix": False,
            "servico": "ServicoDePagamento",
        },
        "abordagem_condicional": {
            "pedido_cria_dependencia": True,
            "tipos": ["cartao", "pix"],
            "usa_if_elif": True,
            "exige_alterar_pedido_para_novo_tipo": True,
        },
        "factory_implementado": False,
        "pagamentos_reais": False,
    }
