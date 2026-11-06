"""Executa simulacoes de colaboracao no projeto de churn."""

import json
import sys
from pathlib import Path


BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from src.aula14_fluxo_colaborativo import (
    Mudanca,
    avaliar_integracao,
    comparar_fluxos,
    recomendar_fluxo,
)


def main() -> None:
    print("=" * 60)
    print("AULA 14 - FLUXO DE TRABALHO COLABORATIVO")
    print("=" * 60)

    print("\n1. SIMULANDO NOVA FUNCIONALIDADE")

    melhoria = Mudanca(
        identificador="CHURN-014",
        branch="feature/preprocessamento",
        arquivos_alterados=4,
        dias_aberta=1,
        testes_aprovados=True,
        revisao_aprovada=True,
        cobertura=98.02,
    )

    comparacao = comparar_fluxos(melhoria)

    print(json.dumps(
        comparacao,
        indent=2,
        ensure_ascii=False,
    ))

    assert comparacao["gitflow"]["aprovada"]
    assert comparacao["trunk"]["aprovada"]

    print("\n2. SIMULANDO FALHA NOS TESTES")

    com_falha = Mudanca(
        identificador="CHURN-015",
        branch="fix/erro-dados",
        arquivos_alterados=2,
        dias_aberta=1,
        testes_aprovados=False,
        revisao_aprovada=True,
        cobertura=98.02,
    )

    bloqueio = avaliar_integracao(
        com_falha,
        "trunk",
    )

    print("Integracao aprovada:", bloqueio["aprovada"])
    print("Impedimentos:", bloqueio["impedimentos"])

    assert not bloqueio["aprovada"]

    print("\n3. AVALIANDO MODELO DE CHURN")

    modelo = Mudanca(
        identificador="CHURN-016",
        branch="feature/modelo-churn",
        arquivos_alterados=6,
        dias_aberta=1,
        testes_aprovados=True,
        revisao_aprovada=True,
        cobertura=98.02,
        recall_churn=0.0,
        altera_modelo=True,
    )

    avaliacao_modelo = avaliar_integracao(
        modelo,
        "trunk",
        destino_producao=True,
        recall_minimo=0.60,
    )

    print("Cobertura do codigo: 98.02%")
    print("Recall da classe churn: 0.0")
    print("Criterio didatico de recall: 0.60")
    print("Aprovado para producao:", avaliacao_modelo["aprovada"])
    print("Impedimentos:", avaliacao_modelo["impedimentos"])

    assert not avaliacao_modelo["aprovada"]

    print("\n4. COMPARANDO ESTRATEGIAS")

    estrategia_rapida = recomendar_fluxo(
        lancamentos_frequentes=True,
        equipe_tem_automacao=True,
        versoes_planejadas=False,
    )

    estrategia_planejada = recomendar_fluxo(
        lancamentos_frequentes=False,
        equipe_tem_automacao=False,
        versoes_planejadas=True,
    )

    print("Entregas frequentes:", estrategia_rapida)
    print("Releases planejadas:", estrategia_planejada)

    print("\n5. SALVANDO RELATORIO")

    resultado = {
        "aula": 14,
        "tema": "Fluxo de Trabalho Colaborativo",
        "comparacao": comparacao,
        "falha_nos_testes": bloqueio,
        "modelo_para_producao": avaliacao_modelo,
        "sugestoes": {
            "entregas_frequentes": estrategia_rapida,
            "releases_planejadas": estrategia_planejada,
        },
        "observacoes": [
            "Simulacoes sem comandos Git.",
            "Limites de cobertura sao configuraveis.",
            "Recall minimo de 0.60 e somente didatico.",
            "Nenhum merge ou deploy foi realizado.",
        ],
    }

    destino = (
        BASE / "resultados" / "aula14_fluxo_colaborativo.json"
    )

    destino.write_text(
        json.dumps(resultado, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print("Relatorio:", destino.name)
    print("\nAULA 14 EXECUTADA COM SUCESSO!")


if __name__ == "__main__":
    main()
