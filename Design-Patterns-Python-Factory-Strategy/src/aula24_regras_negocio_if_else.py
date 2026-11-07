"""Aula 24 - Regras de negocio: if/else ao resgate de novo.

Introducao ao problema resolvido pelo padrao Strategy.

Implementa a funcao simples e a versao expandida,
conforme a transcricao da aula.

A separacao das estrategias fica para a proxima aula.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Cliente:
    nome: str
    tipo: str
    parceiro: Optional[str] = None


def calcular_preco_inicial(cliente, total):
    """Versao inicial: tres tipos com desconto."""

    if cliente.tipo == "vip":
        return total * 0.8
    elif cliente.tipo == "novo":
        return total * 0.9
    elif cliente.tipo == "funcionario":
        return total * 0.7
    else:
        return total


def calcular_preco(cliente, total):
    """Versao expandida com regras comerciais acumuladas."""

    if cliente.tipo == "vip":
        preco = total * 0.8

    elif cliente.tipo == "novo":
        preco = total * 0.9

    elif cliente.tipo == "funcionario":
        preco = total * 0.7

    elif cliente.tipo == "parceria":
        preco = total * 0.85

        if cliente.parceiro == "empresa_x":
            preco -= 10

        elif cliente.parceiro == "empresa_y":
            preco -= 5

    elif cliente.tipo == "black_friday":
        preco = total * 0.5

        if total > 500:
            preco *= 0.9

    else:
        preco = total

    return preco


CODE_SMELLS = (
    "complexidade crescente",
    "dificil manutencao",
    "dificil testabilidade",
    "violacao do principio aberto/fechado",
    "baixa coesao",
    "alto acoplamento",
    "dificil reutilizacao",
)


def analisar_aula24():
    """Registra as observacoes de design apresentadas na aula."""

    return {
        "aula": 24,
        "titulo": "Regras de negocio if else ao resgate de novo",
        "problema": "regras comerciais concentradas em if/elif/else",
        "versao_inicial": [
            "vip",
            "novo",
            "funcionario",
            "outros",
        ],
        "regras_acrescentadas": [
            "parceria",
            "empresa_x",
            "empresa_y",
            "black_friday",
        ],
        "code_smells": list(CODE_SMELLS),
        "principio_afetado": "aberto/fechado",
        "solucao_proposta": (
            "separar as estrategias de calculo "
            "de preco em funcoes ou objetos diferentes"
        ),
        "strategy_implementado": False,
    }
