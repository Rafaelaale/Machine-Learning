"""Comparacao didatica: regras fixas e ML.

Modelo ML: classificador por centroides.
Usa somente a biblioteca padrao do Python.

Os rotulos de churn sao inteiramente ficticios.
"""

import csv
from pathlib import Path


ATRIBUTOS = ("dias_sem_compra", "reclamacoes_90d")


def validar_registro(registro, exigir_rotulo=False):
    obrigatorios = set(ATRIBUTOS)

    if exigir_rotulo:
        obrigatorios.add("churn")

    ausentes = obrigatorios - set(registro)

    if ausentes:
        raise ValueError(
            "Colunas obrigatorias ausentes: "
            + ", ".join(sorted(ausentes))
        )

    dados = {}

    for atributo in ATRIBUTOS:
        valor = int(registro[atributo])

        if valor < 0:
            raise ValueError(
                f"{atributo} nao pode ser negativo"
            )

        dados[atributo] = valor

    if exigir_rotulo:
        rotulo = int(registro["churn"])

        if rotulo not in (0, 1):
            raise ValueError("Rotulo precisa ser 0 ou 1")

        dados["churn"] = rotulo

    return dados


def carregar_dados(caminho):
    with Path(caminho).open(
        encoding="utf-8-sig", newline=""
    ) as arquivo:
        leitor = csv.DictReader(arquivo)

        obrigatorias = {
            "cliente_id", "conjunto",
            "churn", *ATRIBUTOS,
        }

        if not obrigatorias.issubset(
            leitor.fieldnames or []
        ):
            raise ValueError("Esquema do CSV incompleto")

        registros = []

        for linha in leitor:
            dados = validar_registro(
                linha, exigir_rotulo=True
            )

            conjunto = linha["conjunto"].strip()

            if conjunto not in ("treino", "teste"):
                raise ValueError("Conjunto desconhecido")

            dados["cliente_id"] = linha["cliente_id"]
            dados["conjunto"] = conjunto

            registros.append(dados)

    return registros


def previsao_tradicional(registro):
    """Regra fixa, sem treinamento."""

    dados = validar_registro(registro)

    if (
        dados["dias_sem_compra"] >= 60
        or dados["reclamacoes_90d"] >= 2
    ):
        return 1

    return 0


def vetor(registro):
    """Escalas fixas definidas antes do treinamento."""

    dados = validar_registro(registro)

    return (
        dados["dias_sem_compra"] / 100.0,
        dados["reclamacoes_90d"] / 3.0,
    )


def treinar_modelo(registros):
    """Aprende centroides das duas classes.

    Nao e uma implementacao de sklearn.
    """

    acumuladores = {
        0: [0.0, 0.0],
        1: [0.0, 0.0],
    }

    contagens = {0: 0, 1: 0}

    for registro in registros:
        dados = validar_registro(
            registro, exigir_rotulo=True
        )

        classe = dados["churn"]
        valores = vetor(dados)

        for indice in range(2):
            acumuladores[classe][indice] += valores[indice]

        contagens[classe] += 1

    if not all(contagens.values()):
        raise ValueError(
            "Treinamento requer exemplos das duas classes"
        )

    centroides = {}

    for classe in (0, 1):
        centroides[classe] = [
            valor / contagens[classe]
            for valor in acumuladores[classe]
        ]

    return {
        "algoritmo": "centroide_mais_proximo",
        "atributos": list(ATRIBUTOS),
        "centroides": centroides,
        "amostras_treinamento": len(registros),
    }


def prever_ml(modelo, registro):
    """Escolhe a classe com menor distancia quadratica."""

    valores = vetor(registro)
    distancias = {}

    for classe_texto, centroide in modelo["centroides"].items():
        classe = int(classe_texto)

        distancias[classe] = sum(
            (valor - referencia) ** 2
            for valor, referencia in zip(
                valores, centroide
            )
        )

    return min(distancias, key=distancias.get)


def avaliar(registros, funcao_previsao):
    if not registros:
        raise ValueError("Conjunto de avaliacao vazio")

    acertos = 0

    for registro in registros:
        previsto = funcao_previsao(registro)

        if previsto == registro["churn"]:
            acertos += 1

    return {
        "amostras": len(registros),
        "acertos": acertos,
        "acuracia": round(
            acertos / len(registros), 4
        ),
    }


def detectar_mudanca_esquema(registro):
    ausentes = sorted(
        set(ATRIBUTOS) - set(registro)
    )

    return {
        "esquema_valido": not ausentes,
        "colunas_ausentes": ausentes,
    }


def detectar_mudanca_media(
    referencia, atual, limite=20
):
    """Alerta didatico; nao substitui monitoramento real."""

    if not referencia or not atual:
        raise ValueError("Amostras vazias")

    media_referencia = sum(
        item["dias_sem_compra"] for item in referencia
    ) / len(referencia)

    media_atual = sum(
        item["dias_sem_compra"] for item in atual
    ) / len(atual)

    diferenca = abs(
        media_atual - media_referencia
    )

    return {
        "media_referencia": round(media_referencia, 2),
        "media_atual": round(media_atual, 2),
        "diferenca": round(diferenca, 2),
        "alerta": diferenca > limite,
    }