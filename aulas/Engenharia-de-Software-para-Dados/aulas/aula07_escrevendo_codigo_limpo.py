"""Executa a Aula 07 com o dataset oficial da Alura."""

import json
import sys
from pathlib import Path


BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from src.aula07_churn_limpo import (
    carregar_clientes,
    executar_pipeline,
)


DADOS = (
    BASE
    / "material_alura"
    / "projeto-CHURN"
    / "Churn-antes"
    / "dados_corretos2.csv"
)

RESULTADOS = BASE / "resultados"


def main():
    print("=" * 60)
    print("AULA 07 - ESCREVENDO CODIGO LIMPO")
    print("=" * 60)

    print("\n1. CARREGANDO DADOS DA ALURA")
    clientes = carregar_clientes(str(DADOS))

    print("Registros originais:", len(clientes))
    print("Colunas originais:", len(clientes.columns))

    print("\n2. EXECUTANDO PIPELINE MODULAR")
    resultado = executar_pipeline(clientes)

    print("Registros utilizados:", resultado["registros_utilizados"])
    print("Treinamento:", resultado["registros_treino"])
    print("Teste:", resultado["registros_teste"])
    print("Atributos:", resultado["atributos"])

    print("\n3. METRICAS DO MODELO")
    metricas = resultado["metricas"]

    print("Accuracy:", round(metricas["accuracy"], 4))
    print("Precision classe 1:", round(metricas["1"]["precision"], 4))
    print("Recall classe 1:", round(metricas["1"]["recall"], 4))
    print("F1 classe 1:", round(metricas["1"]["f1-score"], 4))

    print("\n4. DOCUMENTANDO RESULTADOS")
    RESULTADOS.mkdir(parents=True, exist_ok=True)

    relatorio = {
        "aula": 7,
        "tema": "Escrevendo codigo limpo",
        "fonte": "Alura - Churn-antes/dados_corretos2.csv",
        "pipeline": resultado,
        "observacoes": [
            "O CSV oficial nao foi modificado.",
            "Funcoes possuem responsabilidades separadas.",
            "Divisao reproduzivel entre treino e teste.",
            "Resultados representam apenas este dataset.",
            "O codigo nao foi colocado em producao.",
        ],
    }

    destino = RESULTADOS / "aula07_codigo_limpo_churn.json"

    destino.write_text(
        json.dumps(
            relatorio,
            indent=4,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print("Relatorio:", destino.name)

    print("\n5. VALIDACOES")
    assert resultado["registros_utilizados"] > 0
    assert resultado["registros_treino"] > 0
    assert resultado["registros_teste"] > 0
    assert 0 <= metricas["accuracy"] <= 1
    assert destino.is_file()

    print("\nAula 07 executada com sucesso.")


if __name__ == "__main__":
    main()