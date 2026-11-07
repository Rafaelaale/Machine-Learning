"""Aula 08 - Conectando ACF, PACF, AR, MA, ARMA e ARIMA."""

import json
from pathlib import Path

import pandas as pd


RAIZ = Path(__file__).resolve().parent.parent

CSV_PARAMETROS = (
    RAIZ / "resultados" / "aula08_parametros_iniciais.csv"
)

JSON_RELATORIO = (
    RAIZ / "resultados" / "aula08_preparacao_arima.json"
)

CSV_ACF_PACF = (
    RAIZ / "resultados" / "aula07_comparacao_lags.csv"
)

JSON_ADF = (
    RAIZ / "resultados" / "aula06_diferenciacao.json"
)


def criar_parametros_iniciais():
    """Reproduz a tabela de parametros apresentada na Alura."""

    parametros_iniciais = pd.DataFrame({
        "parametro": ["p", "d", "q"],
        "ideia": [
            "Memória dos valores passados",
            "Número de diferenciações",
            "Memória dos erros passados",
        ],
        "Ponto de partida": [
            "Avaliar pela PACF",
            "1",
            "Avaliar pela ACF",
        ],
    })

    return parametros_iniciais


def explicar_componentes():
    """Registra os conceitos estudados nesta aula."""

    return {
        "AR": {
            "nome": "Autoregressive",
            "conceito": (
                "Utiliza valores passados da própria série "
                "para explicar valores atuais."
            ),
            "parametro": "p",
            "referencia": "PACF",
        },
        "MA": {
            "nome": "Moving Average",
            "conceito": (
                "Utiliza erros passados do modelo. "
                "Não é a média móvel de suavização."
            ),
            "parametro": "q",
            "referencia": "ACF",
        },
        "ARMA": {
            "nome": "Autoregressive Moving Average",
            "conceito": (
                "Combina valores passados da série "
                "e erros passados do modelo."
            ),
            "componentes": ["AR", "MA"],
        },
        "ARIMA": {
            "nome": (
                "Autoregressive Integrated Moving Average"
            ),
            "conceito": (
                "Combina autorregressão, diferenciação "
                "e média móvel dos erros."
            ),
            "parametros": ["p", "d", "q"],
        },
    }


def consultar_evidencias():
    """Le relatórios anteriores sem modificar seus arquivos."""

    evidencias = {
        "acf_pacf_disponivel": False,
        "adf_disponivel": False,
        "p_valor_original": None,
        "p_valor_diferenciado": None,
        "d_inicial": 1,
        "p_definitivo": None,
        "q_definitivo": None,
    }

    if CSV_ACF_PACF.is_file():
        tabela = pd.read_csv(CSV_ACF_PACF)

        if {"lag", "acf", "pacf"}.issubset(
            tabela.columns
        ):
            evidencias["acf_pacf_disponivel"] = True
            evidencias["lags_disponiveis"] = int(
                tabela["lag"].max()
            )

    if JSON_ADF.is_file():
        dados = json.loads(
            JSON_ADF.read_text(encoding="utf-8")
        )

        evidencias["adf_disponivel"] = True

        evidencias["p_valor_original"] = (
            dados.get("p_valor_original")
        )

        evidencias["p_valor_diferenciado"] = (
            dados.get("p_valor_diferenciado")
        )

        p_original = evidencias["p_valor_original"]
        p_diferenciado = evidencias["p_valor_diferenciado"]

        if p_original is not None and p_diferenciado is not None:
            evidencias["rejeita_h0_original"] = (
                float(p_original) <= 0.05
            )

            evidencias["rejeita_h0_diferenciado"] = (
                float(p_diferenciado) <= 0.05
            )

    return evidencias


def executar_aula():
    """Salva a tabela e a fundamentação para o futuro ARIMA."""

    parametros_iniciais = criar_parametros_iniciais()

    componentes = explicar_componentes()

    evidencias = consultar_evidencias()

    CSV_PARAMETROS.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    parametros_iniciais.to_csv(
        CSV_PARAMETROS,
        index=False,
        encoding="utf-8-sig",
    )

    relatorio = {
        "aula": 8,
        "titulo": "Conectando ACF e PACF ao ARIMA",
        "parametros_iniciais": parametros_iniciais.to_dict(
            orient="records"
        ),
        "componentes": componentes,
        "evidencias_anteriores": evidencias,
        "interpretacao": (
            "PACF ajuda a investigar p; ACF ajuda a "
            "investigar q; d=1 e um ponto de partida "
            "associado a primeira diferenciacao."
        ),
        "cuidados": [
            "ACF e PACF nao escolhem automaticamente o modelo.",
            "O parametro d=1 ainda deve ser avaliado na modelagem.",
            "Lacunas de calendario exigem cuidado com os lags.",
            "Treino e teste devem respeitar a ordem temporal.",
        ],
        "modelo_treinado": False,
        "previsoes_geradas": False,
    }

    JSON_RELATORIO.write_text(
        json.dumps(
            relatorio,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print("\n===== AULA 08 - PARAMETROS ARIMA =====")

    print("\nTABELA DE PARAMETROS:")
    print(parametros_iniciais.to_string(index=False))

    print("\nCONCEITOS:")
    for nome, dados in componentes.items():
        print(f"{nome}: {dados['conceito']}")

    print("\nEVIDENCIAS DAS AULAS ANTERIORES:")
    print(json.dumps(
        evidencias,
        ensure_ascii=False,
        indent=2,
    ))

    print("\nPARAMETROS:")
    print("p: avaliar pela PACF")
    print("d: 1 como ponto de partida")
    print("q: avaliar pela ACF")

    print("\nARQUIVOS:")
    print(CSV_PARAMETROS)
    print(JSON_RELATORIO)

    print("\nAULA 08 EXECUTADA COM SUCESSO")

    return relatorio


if __name__ == "__main__":
    executar_aula()
