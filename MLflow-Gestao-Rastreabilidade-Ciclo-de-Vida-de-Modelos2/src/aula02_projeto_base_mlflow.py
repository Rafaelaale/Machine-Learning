"""Aula 02: Projeto base e componentes do MLflow.

Material conceitual. Nao executa treinamento.
"""

import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

COMPONENTES = {
    "Tracking": {
        "objetivo": "Rastrear experimentos e execucoes",
        "elementos": [
            "parametros",
            "metricas",
            "artefatos",
            "metadados",
        ],
    },
    "Model Registry": {
        "objetivo": "Registrar e versionar modelos",
        "elementos": [
            "modelos registrados",
            "versoes",
        ],
    },
    "Models": {
        "objetivo": "Empacotar modelos para uso posterior",
        "elementos": [
            "carregamento",
            "inferencia",
            "serving",
        ],
    },
    "Projects": {
        "objetivo": "Organizar execucoes reproduziveis",
        "elementos": [
            "codigo",
            "parametros de execucao",
            "ambiente",
        ],
    },
}

EXPERIMENTOS_EXEMPLO = [
    "Credit Risk Baseline",
    "Credit Risk Model Selection",
]

METRICAS_CLASSIFICACAO = [
    "accuracy",
    "precision",
    "recall",
    "f1",
    "roc_auc",
]

CRONOGRAMA = {
    1: "Problema de reprodutibilidade",
    2: "Componentes e projeto base",
    3: "Primeiro rastreamento manual",
    4: "Autolog e rastreamento automatico",
    5: "Comparacao de runs e selecao",
    6: "Registro de modelos",
    7: "Empacotamento para deploy",
    8: "Inferencia via API",
    9: "Execucao reproduzivel",
    10: "Tracking remoto e arquitetura MLOps",
}


def diferenciar_registros():
    """Distingue configuracoes, medidas e arquivos."""
    return {
        "parametro": (
            "Configuracao de treinamento, como "
            "max_depth ou n_estimators."
        ),
        "metrica": (
            "Resultado numerico da avaliacao, "
            "como F1 ou recall."
        ),
        "artefato": (
            "Arquivo associado a execucao, "
            "como grafico ou relatorio."
        ),
    }


def validar_conteudo():
    """Verifica a estrutura da aula."""
    assert len(COMPONENTES) == 4
    assert len(EXPERIMENTOS_EXEMPLO) == 2
    assert len(CRONOGRAMA) == 10
    assert len(diferenciar_registros()) == 3
    return True


def executar():
    """Salva o resumo conceitual sem criar runs."""
    validar_conteudo()

    conteudo = {
        "aula": 2,
        "titulo": "Projeto base",
        "projeto": "Classificacao de risco de credito",
        "conceito_experimento": (
            "Agrupamento de execucoes relacionadas."
        ),
        "conceito_run": (
            "Uma execucao especifica com parametros, "
            "metricas, artefatos e metadados."
        ),
        "componentes": COMPONENTES,
        "exemplos_experimentos": EXPERIMENTOS_EXEMPLO,
        "tipos_de_registro": diferenciar_registros(),
        "metricas_possiveis": METRICAS_CLASSIFICACAO,
        "cronograma": CRONOGRAMA,
        "dados_reais_fornecidos": False,
        "modelo_treinado": False,
        "runs_criadas": 0,
        "proxima_etapa": (
            "Configurar MLflow, conhecer a base "
            "de dados e registrar a primeira execucao."
        ),
    }

    pasta = RAIZ / "resultados"
    pasta.mkdir(parents=True, exist_ok=True)

    destino = pasta / "aula02_projeto_base_mlflow.json"

    destino.write_text(
        json.dumps(
            conteudo,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print("\n===== AULA 02: PROJETO BASE =====")
    print("PROJETO:", conteudo["projeto"])

    print("\nCOMPONENTES MLflow:")
    for nome, detalhes in COMPONENTES.items():
        print(f"- {nome}: {detalhes['objetivo']}")

    print("\nEXPERIMENTOS DE EXEMPLO:")
    for nome in EXPERIMENTOS_EXEMPLO:
        print("-", nome)

    print("\nPARAMETRO, METRICA E ARTEFATO:")
    for tipo, descricao in diferenciar_registros().items():
        print(f"- {tipo}: {descricao}")

    print("\nMODELOS TREINADOS: 0")
    print("RUNS CRIADAS: 0")
    print("CONTEUDO REGISTRADO: OK")

    return conteudo


if __name__ == "__main__":
    executar()
