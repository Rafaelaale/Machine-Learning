"""Simulacao de GitFlow e Trunk-Based Development.

Aula 14 - Engenharia de Software para Dados.

Nao executa comandos Git e nao altera repositorios.
"""

from dataclasses import dataclass
from typing import Optional
import re


PADROES_BRANCH = {
    "feature": r"feature/[a-z0-9]+(?:-[a-z0-9]+)*",
    "fix": r"fix/[a-z0-9]+(?:-[a-z0-9]+)*",
    "hotfix": r"hotfix/[a-z0-9]+(?:-[a-z0-9]+)*",
    "release": r"release/[0-9]+\.[0-9]+\.[0-9]+",
}


def validar_branch(nome: str) -> bool:
    """Valida nomes de branches usando a politica didatica."""
    if not isinstance(nome, str):
        return False

    if nome in {"main", "develop"}:
        return True

    return any(
        re.fullmatch(padrao, nome) is not None
        for padrao in PADROES_BRANCH.values()
    )


@dataclass(frozen=True)
class Mudanca:
    """Representa uma alteracao submetida a revisao."""

    identificador: str
    branch: str
    arquivos_alterados: int
    dias_aberta: int
    testes_aprovados: bool
    revisao_aprovada: bool
    cobertura: float
    recall_churn: Optional[float] = None
    altera_modelo: bool = False

    def __post_init__(self) -> None:
        """Rejeita metadados inconsistentes."""
        if not self.identificador.strip():
            raise ValueError("Identificador obrigatorio")

        if not validar_branch(self.branch):
            raise ValueError("Nome de branch invalido")

        if self.arquivos_alterados < 0:
            raise ValueError("Quantidade de arquivos invalida")

        if self.dias_aberta < 0:
            raise ValueError("Duracao da branch invalida")

        if not 0 <= self.cobertura <= 100:
            raise ValueError("Cobertura fora de 0 a 100")

        if self.recall_churn is not None:
            if not 0 <= self.recall_churn <= 1:
                raise ValueError("Recall fora de 0 a 1")


def avaliar_integracao(
    mudanca: Mudanca,
    estrategia: str,
    destino_producao: bool = False,
    cobertura_minima: Optional[float] = None,
    recall_minimo: Optional[float] = None,
) -> dict:
    """Avalia criterios didaticos antes da integracao.

    A politica de cobertura e configuravel.
    Os limites nao representam normas universais.
    """
    if estrategia not in {"gitflow", "trunk"}:
        raise ValueError("Estrategia desconhecida")

    if cobertura_minima is None:
        cobertura_minima = (
            85.0 if estrategia == "gitflow" else 90.0
        )

    if not 0 <= cobertura_minima <= 100:
        raise ValueError("Limite de cobertura invalido")

    if recall_minimo is not None:
        if not 0 <= recall_minimo <= 1:
            raise ValueError("Limite de recall invalido")

    impedimentos = []
    alertas = []

    if not mudanca.testes_aprovados:
        impedimentos.append("Testes automatizados falharam")

    if not mudanca.revisao_aprovada:
        impedimentos.append("Code review pendente")

    if mudanca.cobertura < cobertura_minima:
        impedimentos.append("Cobertura abaixo da politica")

    if estrategia == "trunk":
        if mudanca.dias_aberta > 2:
            alertas.append("Branch aberta por muitos dias")

        if mudanca.arquivos_alterados > 10:
            alertas.append("Alteracao grande para integracao rapida")

    if destino_producao and mudanca.altera_modelo:
        if recall_minimo is None:
            impedimentos.append(
                "Criterio de recall nao definido para producao"
            )
        elif mudanca.recall_churn is None:
            impedimentos.append(
                "Recall do modelo nao foi medido"
            )
        elif mudanca.recall_churn < recall_minimo:
            impedimentos.append(
                "Recall abaixo do criterio de negocio"
            )

    return {
        "id": mudanca.identificador,
        "estrategia": estrategia,
        "branch": mudanca.branch,
        "destino_producao": destino_producao,
        "aprovada": not impedimentos,
        "impedimentos": impedimentos,
        "alertas": alertas,
        "cobertura_minima": cobertura_minima,
        "recall_minimo": recall_minimo,
    }


def comparar_fluxos(mudanca: Mudanca) -> dict:
    """Compara as estrategias usando a mesma alteracao."""
    return {
        "gitflow": avaliar_integracao(
            mudanca, "gitflow"
        ),
        "trunk": avaliar_integracao(
            mudanca, "trunk"
        ),
    }


def recomendar_fluxo(
    lancamentos_frequentes: bool,
    equipe_tem_automacao: bool,
    versoes_planejadas: bool,
) -> str:
    """Produz uma sugestao didatica, nao uma regra absoluta."""
    if versoes_planejadas and not lancamentos_frequentes:
        return "gitflow"

    if lancamentos_frequentes and equipe_tem_automacao:
        return "trunk"

    return "avaliar_contexto"
