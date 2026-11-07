"""Aula 02 - Introducao aos Design Patterns.

Demonstra os conceitos basicos das categorias:
criacional, estrutural e comportamental.

Os exemplos sao introdutorios e nao substituem
as implementacoes completas dos padroes GoF.
"""

from dataclasses import dataclass
from typing import Callable


CATEGORIAS = {
    "criacional": {
        "objetivo": "Organizar a criacao de objetos",
        "exemplos": ["Singleton", "Factory", "Builder"],
    },
    "estrutural": {
        "objetivo": "Organizar a composicao de objetos",
        "exemplos": ["Adapter", "Decorator"],
    },
    "comportamental": {
        "objetivo": "Organizar a interacao e os comportamentos",
        "exemplos": ["Strategy", "Observer"],
    },
}


@dataclass(frozen=True)
class Notificacao:
    """Objeto simples do dominio de exemplo."""

    destinatario: str
    mensagem: str
    canal: str

    def descrever(self) -> str:
        return (
            f"[{self.canal}] "
            f"Para: {self.destinatario} | "
            f"Mensagem: {self.mensagem}"
        )


def criar_notificacao(
    destinatario: str,
    mensagem: str,
    canal: str = "email",
) -> Notificacao:
    """Demonstra a centralizacao da criacao de um objeto.

    Ainda nao implementa o padrao Factory completo.
    """
    if not isinstance(destinatario, str) or not destinatario.strip():
        raise ValueError("Destinatario obrigatorio")

    if not isinstance(mensagem, str) or not mensagem.strip():
        raise ValueError("Mensagem obrigatoria")

    if canal not in ("email", "sms"):
        raise ValueError("Canal nao suportado")

    return Notificacao(
        destinatario=destinatario.strip(),
        mensagem=mensagem.strip(),
        canal=canal,
    )


class MensagemFormatada:
    """Objeto base para demonstrar composicao."""

    def __init__(self, texto: str):
        self.texto = texto

    def renderizar(self) -> str:
        return self.texto


class MensagemComPrefixo:
    """Compoe outro objeto sem modificar sua classe."""

    def __init__(self, mensagem: MensagemFormatada, prefixo: str):
        self.mensagem = mensagem
        self.prefixo = prefixo

    def renderizar(self) -> str:
        return f"{self.prefixo}{self.mensagem.renderizar()}"


def aplicar_comportamento(
    valor: float,
    operacao: Callable[[float], float],
) -> float:
    """Recebe o comportamento como dependencia."""
    if not callable(operacao):
        raise TypeError("A operacao precisa ser chamavel")

    return operacao(valor)


def aplicar_desconto(valor: float) -> float:
    """Exemplo de comportamento selecionavel."""
    if valor < 0:
        raise ValueError("Valor nao pode ser negativo")

    return round(valor * 0.9, 2)


def aplicar_acrescimo(valor: float) -> float:
    """Segundo comportamento selecionavel."""
    if valor < 0:
        raise ValueError("Valor nao pode ser negativo")

    return round(valor * 1.1, 2)


def classificar_exemplo(categoria: str) -> dict:
    """Consulta o catalogo introdutorio dos padroes."""
    if categoria not in CATEGORIAS:
        raise ValueError("Categoria desconhecida")

    return {
        "categoria": categoria,
        **CATEGORIAS[categoria],
    }
