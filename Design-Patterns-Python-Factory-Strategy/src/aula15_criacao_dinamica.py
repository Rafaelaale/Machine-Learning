"""Aula 15 - Criacao dinamica de objetos.

Reutiliza o Factory Method da Aula 14.

Demonstra:
1. Selecao com if/elif.
2. Selecao com dicionario.
3. Entrada do usuario.
4. Limitacoes de extensibilidade.

Nenhum pagamento real e efetuado.
"""

from src.aula14_factory_method import (
    ServicoDePedidoFactory,
    PedidoPixFactory,
    PedidoCartaoFactory,
    PedidoBoletoFactory,
)


TIPOS_DISPONIVEIS = ["pix", "cartao", "boleto"]


MAPA_PEDIDOS = {
    "pix": PedidoPixFactory,
    "cartao": PedidoCartaoFactory,
    "boleto": PedidoBoletoFactory,
}


def criar_pedido_condicional(tipo):
    """Exemplo inicial: selecao com if/elif."""
    if tipo == "pix":
        return PedidoPixFactory()
    elif tipo == "cartao":
        return PedidoCartaoFactory()
    elif tipo == "boleto":
        return PedidoBoletoFactory()
    else:
        raise ValueError("Tipo de pagamento inválido")


def criar_pedido_mapa(tipo):
    """Seleciona a classe por meio de um dicionario."""
    classe_pedido = MAPA_PEDIDOS.get(tipo)

    if classe_pedido is None:
        raise ValueError("Tipo inválido")

    return classe_pedido()


def processar_pedido(tipo, valor=100, estrategia="mapa"):
    """Cria dinamicamente o pedido e finaliza a simulacao."""
    if estrategia == "mapa":
        pedido = criar_pedido_mapa(tipo)
    elif estrategia == "condicional":
        pedido = criar_pedido_condicional(tipo)
    else:
        raise ValueError("Estratégia inválida")

    pedido.finalizar_pedido(valor)
    return pedido


def escolher_por_input(
    valor=100,
    entrada=input,
):
    """Demonstra a escolha em tempo de execucao.

    O parametro entrada permite simular input()
    nos testes, sem interacao humana.
    """
    tipo = entrada("Tipo de pagamento: ")
    return processar_pedido(tipo, valor=valor)


def analisar_criacao_dinamica():
    return {
        "aula": 15,
        "padrao_utilizado": "Factory Method",
        "tema": "Criacao dinamica",
        "tipos_disponiveis": list(TIPOS_DISPONIVEIS),
        "estrategias": ["condicional", "mapa"],
        "mapa": {
            tipo: classe.__name__
            for tipo, classe in MAPA_PEDIDOS.items()
        },
        "factory_method_reutilizado": True,
        "mapa_precisa_ser_editado_para_novos_tipos": True,
        "registro_automatico_implementado": False,
        "pagamentos_reais": False,
    }
