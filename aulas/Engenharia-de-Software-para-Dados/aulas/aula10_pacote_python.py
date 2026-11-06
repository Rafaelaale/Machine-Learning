"""Executa o pacote sobre os dados ficticios e oficiais."""

import json
from pathlib import Path

import pandas as pd

from pre_processamento import PreProcessamento


BASE = Path(__file__).resolve().parent.parent

CHURN = BASE / "projetos" / "churn_profissional"
DADOS = CHURN / "data"
RESULTADOS = BASE / "resultados"


def processar_arquivo(origem: Path, destino: Path) -> dict:
    """Executa o pacote e retorna um resumo verificavel."""
    processador = PreProcessamento(str(origem))

    processador.executar_pipeline(str(destino))

    original = pd.read_csv(origem, low_memory=False)
    processado = pd.read_csv(destino, low_memory=False)

    if len(original) != len(processado):
        raise AssertionError("Quantidade de registros alterada")

    return {
        "entrada": origem.name,
        "saida": destino.name,
        "linhas": len(processado),
        "colunas_entrada": len(original.columns),
        "colunas_saida": len(processado.columns),
        "nulos_churn": int(processado["churn"].isna().sum()),
        "fidelidade_criada": "fidelidade" in processado.columns,
        "score_gasto_criado": "score_gasto" in processado.columns,
    }


def main() -> None:
    print("=" * 60)
    print("AULA 10 - CONVERTENDO NOTEBOOKS EM PACOTES PYTHON")
    print("=" * 60)

    print("\n1. INSTANCIA DE PreProcessamento")
    print("Pacote instalado e importado com sucesso.")

    print("\n2. PROCESSANDO CSV FICTICIO")
    teste = processar_arquivo(
        DADOS / "raw" / "clientes_teste_aula10.csv",
        DADOS / "processed" / "clientes_teste_aula10_processados.csv",
    )
    print(json.dumps(teste, indent=2, ensure_ascii=False))

    print("\n3. PROCESSANDO CSV OFICIAL DA ALURA")
    oficial = processar_arquivo(
        DADOS / "raw" / "dados_corretos2.csv",
        DADOS / "processed" / "clientes_alura_aula10_processados.csv",
    )
    print(json.dumps(oficial, indent=2, ensure_ascii=False))

    print("\n4. VALIDANDO RESULTADOS")
    assert teste["linhas"] == 4
    assert oficial["linhas"] == 10000
    assert oficial["fidelidade_criada"]
    assert oficial["score_gasto_criado"]

    RESULTADOS.mkdir(parents=True, exist_ok=True)

    relatorio = {
        "aula": 10,
        "tema": "Convertendo notebooks em pacotes Python",
        "pacote": "pre_processamento",
        "versao": "0.1.0",
        "amostra_ficticia": teste,
        "amostra_alura": oficial,
        "limitacoes": [
            "Os dados ficticios sao apenas demonstrativos.",
            "Nenhum modelo de ML foi treinado nesta aula.",
            "Valores desconhecidos de churn ficam ausentes.",
            "Medianas e categorias ainda nao sao ajustadas "
            "separadamente em treino e teste.",
        ],
    }

    destino = RESULTADOS / "aula10_pacote_python.json"

    destino.write_text(
        json.dumps(relatorio, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print("\nRELATORIO:", destino.name)
    print("\nAULA 10 EXECUTADA COM SUCESSO!")


if __name__ == "__main__":
    main()
