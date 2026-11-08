"""Aula 01 — Conceitos de MLflow e reprodutibilidade."""

from pathlib import Path
import json


RAIZ = Path(__file__).resolve().parent.parent

CONCEITOS = {
    "curso": "MLflow: gestao e rastreabilidade do ciclo de vida de modelos",
    "aula": 1,
    "tema": "Apresentando o problema",
    "projeto": "Classificacao de risco de credito",
    "problema": (
        "Experimentos de Machine Learning sem rastreabilidade "
        "sao dificeis de comparar e reproduzir."
    ),
    "criterios_sucesso": [
        "desempenho tecnico",
        "reprodutibilidade",
        "operacionalizacao",
    ],
    "elementos_mlflow": [
        "experimentos",
        "execucoes",
        "parametros",
        "metricas",
        "artefatos",
        "registro de modelos",
        "versionamento",
        "inferencia",
    ],
    "modelo_treinado": False,
    "dados_carregados": False,
    "proxima_etapa": "Ambiente, dados e baseline",
}


def validar_conceitos():
    """Valida a estrutura conceitual da aula."""
    assert CONCEITOS["aula"] == 1
    assert len(CONCEITOS["criterios_sucesso"]) == 3
    assert not CONCEITOS["modelo_treinado"]
    assert not CONCEITOS["dados_carregados"]
    return True


def executar():
    """Registra os conceitos sem executar treinamento."""
    validar_conceitos()

    saida = RAIZ / "resultados"
    saida.mkdir(parents=True, exist_ok=True)

    arquivo = saida / "aula01_conceitos_mlflow.json"
    arquivo.write_text(
        json.dumps(CONCEITOS, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print("AULA 01: APRESENTANDO O PROBLEMA")
    print("PROJETO:", CONCEITOS["projeto"])
    print("CRITERIOS DE SUCESSO:")

    for criterio in CONCEITOS["criterios_sucesso"]:
        print(" -", criterio)

    print("MODELO TREINADO: NAO")
    print("DADOS CARREGADOS: NAO")
    print("CONCEITOS REGISTRADOS: OK")

    return CONCEITOS


if __name__ == "__main__":
    executar()
