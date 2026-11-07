"""Aula 25 - Padrao Strategy.

Cada estrategia de desconto e um objeto independente.
O cliente recebe a estrategia por composicao.
calcular_preco utiliza polimorfismo, sem if/else.

A implementacao com funcoes sera estudada na proxima aula.
"""

from abc import ABC, abstractmethod


class RegraDeDesconto(ABC):
    """Contrato abstrato para estrategias de desconto."""

    @abstractmethod
    def calcular(self, total):
        pass


class DescontoVip(RegraDeDesconto):
    def calcular(self, total):
        return total * 0.8


class DescontoNovo(RegraDeDesconto):
    def calcular(self, total):
        return total * 0.9


class DescontoFuncionario(RegraDeDesconto):
    def calcular(self, total):
        return total * 0.7


class SemDesconto(RegraDeDesconto):
    def calcular(self, total):
        return total


class Cliente:
    """Cliente recebe sua estrategia por composicao."""

    def __init__(self, nome, estrategia: RegraDeDesconto):
        self.nome = nome
        self.regra_de_desconto = estrategia


def calcular_preco(cliente: Cliente, total):
    """Delega o calculo para a estrategia do cliente."""

    return cliente.regra_de_desconto.calcular(total)


def criar_clientes_exemplo():
    """Cria os clientes usados na transcricao."""

    return {
        "maria": Cliente("Maria", DescontoVip()),
        "joao": Cliente("João", DescontoNovo()),
        "ana": Cliente("Ana", SemDesconto()),
        "funcionario": Cliente(
            "Funcionário",
            DescontoFuncionario(),
        ),
    }


def demonstrar_troca_estrategia():
    """A mesma cliente recebe uma nova regra em tempo de execucao."""

    maria = Cliente("Maria", DescontoVip())

    preco_vip = calcular_preco(maria, 200)

    maria.regra_de_desconto = DescontoNovo()

    preco_novo = calcular_preco(maria, 200)

    return {
        "cliente": maria.nome,
        "preco_com_vip": preco_vip,
        "preco_com_novo": preco_novo,
        "estrategia_atual": type(
            maria.regra_de_desconto
        ).__name__,
    }


def demonstrar_extensibilidade():
    """Exemplo adicional: nova estrategia sem mudar calcular_preco."""

    class DescontoEspecial(RegraDeDesconto):
        def calcular(self, total):
            return total * 0.6

    cliente = Cliente("Cliente Especial", DescontoEspecial())

    return {
        "estrategia": "DescontoEspecial",
        "total_original": 200,
        "preco_final": calcular_preco(cliente, 200),
    }


def analisar_aula25():
    return {
        "aula": 25,
        "titulo": "Padrao Strategy",
        "contrato": "RegraDeDesconto",
        "metodo_abstrato": "calcular",
        "estrategias": [
            "DescontoVip",
            "DescontoNovo",
            "DescontoFuncionario",
            "SemDesconto",
        ],
        "composicao": True,
        "polimorfismo": True,
        "estrategias_intercambiaveis": True,
        "extensibilidade": True,
        "baixo_acoplamento": True,
        "responsabilidades_separadas": True,
        "strategy_com_funcoes": False,
    }
