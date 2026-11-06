"""Aula 09: POO e programacao funcional aplicadas ao churn."""

from dataclasses import dataclass
from datetime import date
from functools import reduce
from typing import Callable

import pandas as pd


COLUNAS = (
    "total_spent",
    "num_orders",
    "days_since_last_purchase",
    "churn",
)


def calcular_dias_inativos(
    ultima_atividade: date,
    referencia: date,
) -> int:
    """Calcula dias inativos sem modificar os argumentos."""
    if ultima_atividade > referencia:
        raise ValueError("A ultima atividade nao pode ser futura")

    return (referencia - ultima_atividade).days


def classificar_risco(
    dias_inativos: int,
    frequencia_compras: int,
    limite_dias: int = 60,
    maximo_compras: int = 2,
) -> bool:
    """Aplica uma regra didatica, nao um modelo de ML."""
    if min(
        dias_inativos,
        frequencia_compras,
        limite_dias,
        maximo_compras,
    ) < 0:
        raise ValueError("Valores negativos nao sao aceitos")

    return (
        dias_inativos >= limite_dias
        and frequencia_compras <= maximo_compras
    )


def criar_alerta(cliente_id: str, em_risco: bool) -> str | None:
    """Retorna o texto de um alerta sem enviar mensagens."""
    if not em_risco:
        return None

    return f"Revisar relacionamento com cliente {cliente_id}"


@dataclass(frozen=True)
class ClienteChurn:
    """Representa um cliente sem permitir alteracao de atributos."""

    cliente_id: str
    ultima_atividade: date
    produto_id: str | None
    valor_total_compras: float
    frequencia_compras: int
    tempo_desde_primeira_compra: int | None
    status_churn: bool

    def __post_init__(self) -> None:
        """Valida os dados recebidos pela entidade."""
        if not self.cliente_id.strip():
            raise ValueError("Identificador obrigatorio")

        if not isinstance(self.ultima_atividade, date):
            raise TypeError("Ultima atividade deve ser uma data")

        if self.valor_total_compras < 0:
            raise ValueError("Valor de compras negativo")

        if self.frequencia_compras < 0:
            raise ValueError("Frequencia de compras negativa")

        if (
            self.tempo_desde_primeira_compra is not None
            and self.tempo_desde_primeira_compra < 0
        ):
            raise ValueError("Tempo desde primeira compra invalido")

    def calcular_tempo_inatividade(
        self,
        referencia: date,
    ) -> int:
        """Consulta o calculo funcional de inatividade."""
        return calcular_dias_inativos(
            self.ultima_atividade,
            referencia,
        )

    def prever_churn(
        self,
        referencia: date,
        regra: Callable[[int, int], bool] = classificar_risco,
    ) -> bool:
        """Executa uma regra recebida por composicao.

        Este metodo nao treina um modelo estatistico.
        """
        dias = self.calcular_tempo_inatividade(referencia)

        return regra(dias, self.frequencia_compras)

    def notificar_cliente(
        self,
        referencia: date,
    ) -> str | None:
        """Produz um alerta simulado, sem envio externo."""
        em_risco = self.prever_churn(referencia)

        return criar_alerta(self.cliente_id, em_risco)


def preparar_base(clientes: pd.DataFrame) -> pd.DataFrame:
    """Cria uma base de trabalho sem alterar o DataFrame original."""
    ausentes = set(COLUNAS) - set(clientes.columns)

    if ausentes:
        raise ValueError(
            "Colunas ausentes: " + ", ".join(sorted(ausentes))
        )

    resultado = clientes.loc[:, COLUNAS].copy()

    for coluna in COLUNAS:
        resultado[coluna] = pd.to_numeric(
            resultado[coluna],
            errors="coerce",
        )

    resultado = resultado.dropna().copy()

    validos = (
        (resultado["total_spent"] >= 0)
        & (resultado["num_orders"] >= 0)
        & (resultado["days_since_last_purchase"] >= 0)
        & (resultado["churn"].isin([0, 1]))
    )

    return resultado.loc[validos].copy()


def adicionar_risco(
    clientes: pd.DataFrame,
    limite_dias: int = 60,
) -> pd.DataFrame:
    """Adiciona classificacao de risco em uma nova copia."""
    if limite_dias < 0:
        raise ValueError("Limite de dias invalido")

    resultado = preparar_base(clientes)

    resultado["risco_regra"] = (
        (resultado["days_since_last_purchase"] >= limite_dias)
        & (resultado["num_orders"] <= 2)
    )

    return resultado


def resumir_riscos(clientes: pd.DataFrame) -> dict:
    """Agrega resultados com map, filter e reduce."""
    dados = adicionar_risco(clientes)

    riscos = list(map(bool, dados["risco_regra"]))

    identificados = list(filter(bool, riscos))

    total_risco = reduce(
        lambda acumulado, valor: acumulado + int(valor),
        identificados,
        0,
    )

    total = len(dados)

    return {
        "total_clientes": total,
        "clientes_em_risco": total_risco,
        "clientes_sem_risco": total - total_risco,
        "percentual_risco": (
            round(100 * total_risco / total, 2)
            if total
            else 0.0
        ),
    }
