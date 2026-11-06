"""Pacote de pre-processamento de dados de clientes.

Aula 10 - Engenharia de Software para Dados.
"""

from pathlib import Path
from typing import Optional

import pandas as pd


COLUNAS_OBRIGATORIAS = (
    "total_spent",
    "num_orders",
    "days_since_last_purchase",
    "churn",
)

COLUNAS_DATA = (
    "signup_date",
    "last_purchase_date",
    "cancel_date",
    "data_ingestion",
)

COLUNAS_CATEGORICAS = (
    "product_category",
    "payment_method",
)


class PreProcessamento:
    """Executa tratamentos reutilizaveis para dados de churn.

    O objeto mantem o estado da base em self.df.

    Cada metodo possui uma responsabilidade especifica.
    """

    def __init__(self, caminho_arquivo: str):
        """Armazena o caminho do CSV recebido."""
        self.caminho_arquivo = Path(caminho_arquivo)
        self.df: Optional[pd.DataFrame] = None

    def _obter_dados(self) -> pd.DataFrame:
        """Garante que o arquivo tenha sido carregado."""
        if self.df is None:
            raise RuntimeError(
                "Execute carregar_dados antes do tratamento"
            )

        return self.df

    def carregar_dados(self) -> None:
        """Le o CSV e valida colunas essenciais."""
        if not self.caminho_arquivo.is_file():
            raise FileNotFoundError(self.caminho_arquivo)

        dados = pd.read_csv(
            self.caminho_arquivo,
            low_memory=False,
        )

        ausentes = set(COLUNAS_OBRIGATORIAS) - set(dados.columns)

        if ausentes:
            raise ValueError(
                "Colunas obrigatorias ausentes: "
                + ", ".join(sorted(ausentes))
            )

        self.df = dados.copy(deep=True)

    def tratar_datas(self) -> None:
        """Converte datas validas e marca datas invalidas com NaT."""
        dados = self._obter_dados().copy()

        for coluna in COLUNAS_DATA:
            if coluna in dados.columns:
                dados[coluna] = pd.to_datetime(
                    dados[coluna],
                    errors="coerce",
                )

        self.df = dados

    def preencher_nulos(self) -> None:
        """Aplica tratamentos especificos para colunas ausentes."""
        dados = self._obter_dados().copy()

        substituicoes = {
            "city": "Desconhecido",
            "payment_method": "outro",
            "product_category": "outro",
        }

        for coluna, padrao in substituicoes.items():
            if coluna in dados.columns:
                dados[coluna] = dados[coluna].fillna(padrao)

        coluna_dias = "days_since_last_purchase"

        dias = pd.to_numeric(
            dados[coluna_dias],
            errors="coerce",
        )

        mediana = dias.median()

        if pd.isna(mediana):
            raise ValueError(
                "Nao foi possivel calcular mediana dos dias"
            )

        dados[coluna_dias] = dias.fillna(mediana)

        self.df = dados

    def codificar_churn(self) -> None:
        """Converte rotulos conhecidos e preserva desconhecidos."""
        dados = self._obter_dados().copy()

        rotulos = (
            dados["churn"]
            .astype("string")
            .str.strip()
            .str.lower()
        )

        mapa = {
            "yes": 1,
            "no": 0,
            "sim": 1,
            "nao": 0,
            "não": 0,
            "true": 1,
            "false": 0,
            "1": 1,
            "0": 0,
        }

        dados["churn"] = (
            rotulos.map(mapa).astype("Int64")
        )

        self.df = dados

    def criar_colunas_derivadas(self) -> None:
        """Cria fidelidade e score de gasto a partir das compras."""
        dados = self._obter_dados().copy()

        for coluna in (
            "total_spent",
            "num_orders",
            "days_since_last_purchase",
        ):
            dados[coluna] = pd.to_numeric(
                dados[coluna],
                errors="raise",
            )

            if dados[coluna].isna().any():
                raise ValueError(
                    f"Valores ausentes na coluna {coluna}"
                )

            if (dados[coluna] < 0).any():
                raise ValueError(
                    f"Valores negativos na coluna {coluna}"
                )

        dados["fidelidade"] = (
            dados["num_orders"]
            / (dados["days_since_last_purchase"] + 1)
        )

        dados["score_gasto"] = (
            dados["total_spent"] * dados["num_orders"]
        )

        self.df = dados

    def codificar_categoricas(self) -> None:
        """Transforma categorias presentes em colunas indicadoras."""
        dados = self._obter_dados().copy()

        existentes = [
            coluna
            for coluna in COLUNAS_CATEGORICAS
            if coluna in dados.columns
        ]

        if existentes:
            dados = pd.get_dummies(
                dados,
                columns=existentes,
                dtype=int,
            )

        self.df = dados

    def salvar_dados(self, caminho_saida: str) -> None:
        """Grava o resultado em CSV, sem indice artificial."""
        dados = self._obter_dados()
        destino = Path(caminho_saida)

        destino.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        dados.to_csv(
            destino,
            index=False,
            encoding="utf-8",
        )

    def executar_pipeline(self, caminho_saida: str) -> None:
        """Executa as etapas na sequencia definida."""
        self.carregar_dados()
        self.tratar_datas()
        self.preencher_nulos()
        self.codificar_churn()
        self.criar_colunas_derivadas()
        self.codificar_categoricas()
        self.salvar_dados(caminho_saida)
