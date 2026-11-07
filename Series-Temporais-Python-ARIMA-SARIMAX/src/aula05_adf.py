"""Aula 05 - Teste ADF de estacionariedade."""

import json
from pathlib import Path

import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import adfuller

from src.aula04_decomposicao import (
    carregar_serie_diaria,
    verificar_calendario,
    CSV_COMPONENTES,
)

RAIZ = Path(__file__).resolve().parent.parent

CSV_ADF = RAIZ / "resultados" / "resultados_adf_original.csv"
JSON_ADF = RAIZ / "resultados" / "aula05_adf.json"
CSV_COMPONENTES_AULA05 = (
    RAIZ / "resultados" / "componentes_serie_bike.csv"
)


def teste_adf(serie):
    """Executa ADF e retorna uma tabela de metricas e valores criticos."""

    valores = pd.to_numeric(
        pd.Series(serie), errors="raise"
    ).dropna()

    if len(valores) < 4:
        raise ValueError("Serie muito curta para o teste ADF.")

    if not np.isfinite(valores.to_numpy()).all():
        raise ValueError("Serie contem valores nao finitos.")

    if valores.nunique() < 2:
        raise ValueError("Serie constante: teste ADF nao aplicavel.")

    resultado = adfuller(valores, autolag="AIC")

    tabela_resultado = pd.DataFrame({
        "metrica": [
            "estatistica_adf",
            "p_valor",
            "lags_utilizados",
            "observacoes",
        ],
        "valor": [
            resultado[0],
            resultado[1],
            resultado[2],
            resultado[3],
        ],
    })

    valores_criticos = pd.DataFrame({
        "metrica": [
            f"valor_critico_{chave}"
            for chave in resultado[4].keys()
        ],
        "valor": list(resultado[4].values()),
    })

    return pd.concat(
        [tabela_resultado, valores_criticos],
        ignore_index=True,
    )


def extrair_metrica(tabela, metrica):
    """Retorna o valor de uma metrica da tabela ADF."""
    encontrados = tabela.loc[
        tabela["metrica"] == metrica,
        "valor",
    ]

    if encontrados.empty:
        raise KeyError(metrica)

    return float(encontrados.iloc[0])


def interpretar_adf(tabela, alfa=0.05):
    """Interpreta H0: presenca de raiz unitaria."""

    p_valor = extrair_metrica(tabela, "p_valor")

    if p_valor <= alfa:
        decisao = "Rejeitar H0"
        interpretacao = (
            "Ha evidencia contra a hipotese de raiz unitaria "
            "ao nivel de significancia escolhido."
        )
        evidencia = True
    else:
        decisao = "Nao rejeitar H0"
        interpretacao = (
            "Nao ha evidencia suficiente para rejeitar "
            "a hipotese de raiz unitaria."
        )
        evidencia = False

    return {
        "p_valor": p_valor,
        "alfa": alfa,
        "decisao": decisao,
        "interpretacao": interpretacao,
        "evidencia_estacionariedade": evidencia,
        "alerta": (
            "O ADF testa raiz unitaria sob suas hipoteses; "
            "nao demonstra sozinho todas as propriedades "
            "de estacionariedade."
        ),
    }


def executar_aula():
    """Analisa a demanda diaria original e salva resultados."""

    serie_diaria = carregar_serie_diaria()

    resultado_adf_original = teste_adf(
        serie_diaria["demanda"]
    )

    interpretacao = interpretar_adf(
        resultado_adf_original
    )

    calendario = verificar_calendario(serie_diaria)

    CSV_ADF.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    resultado_adf_original.to_csv(
        CSV_ADF,
        index=False,
        encoding="utf-8-sig",
    )

    componentes_salvos = False

    if CSV_COMPONENTES.is_file():
        componentes = pd.read_csv(CSV_COMPONENTES)

        componentes.to_csv(
            CSV_COMPONENTES_AULA05,
            index=False,
            encoding="utf-8-sig",
        )

        componentes_salvos = True

    relatorio = {
        "aula": 5,
        "tema": "Teste ADF de estacionariedade",
        "serie": "demanda diaria observada",
        "quantidade_dias_observados": len(serie_diaria),
        "estatistica_adf": extrair_metrica(
            resultado_adf_original, "estatistica_adf"
        ),
        "p_valor": interpretacao["p_valor"],
        "lags_utilizados": int(extrair_metrica(
            resultado_adf_original, "lags_utilizados"
        )),
        "observacoes_teste": int(extrair_metrica(
            resultado_adf_original, "observacoes"
        )),
        "interpretacao": interpretacao,
        "calendario": calendario,
        "componentes_copiados": componentes_salvos,
        "diferenciacao_aplicada": False,
        "modelo_treinado": False,
    }

    JSON_ADF.write_text(
        json.dumps(
            relatorio,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print("\n===== AULA 05 - TESTE ADF =====")
    print("\nRESULTADO:")
    print(resultado_adf_original.to_string(index=False))

    print("\np-valor = {:.4f}".format(
        interpretacao["p_valor"]
    ))
    print("Decisao:", interpretacao["decisao"])
    print(interpretacao["interpretacao"])

    print("\nQUALIDADE TEMPORAL:")
    print(calendario)
    print(
        "AVISO: o ADF foi aplicado aos dias observados; "
        "lacunas no calendario exigem cuidado na interpretacao."
    )

    print("\nARQUIVOS SALVOS:")
    print(CSV_ADF)
    print(JSON_ADF)

    if componentes_salvos:
        print(CSV_COMPONENTES_AULA05)

    print("\nAULA 05 EXECUTADA COM SUCESSO")
    return relatorio


if __name__ == "__main__":
    executar_aula()
