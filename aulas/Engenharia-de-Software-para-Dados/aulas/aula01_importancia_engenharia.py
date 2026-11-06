from pathlib import Path
from datetime import datetime, timezone
import json


BASE = Path(__file__).resolve().parent.parent
RESULTADOS = BASE / "resultados"


def detectar_mudanca(referencia, atual, limite=0.15):
    """
    Compara duas taxas.

    O limite e didatico e nao representa
    criterio universal de monitoramento.
    """
    diferenca = abs(atual - referencia)

    return {
        "referencia": referencia,
        "atual": atual,
        "diferenca": round(diferenca, 4),
        "alerta": diferenca > limite,
    }


def verificar_disparidade(taxa_a, taxa_b, limite=0.10):
    """
    Compara taxas entre grupos ficticios.

    Uma diferenca e sinal de investigacao,
    nao comprovacao automatica de discriminacao.
    """
    diferenca = abs(taxa_a - taxa_b)

    return {
        "grupo_a": taxa_a,
        "grupo_b": taxa_b,
        "diferenca": round(diferenca, 4),
        "investigar": diferenca > limite,
    }


def avaliar_pedido_voz(confianca, ruido):
    """
    Define se um pedido automatizado deve
    seguir ou solicitar confirmacao humana.
    """
    if not 0 <= confianca <= 1:
        raise ValueError("Confianca fora de 0 a 1")

    if not 0 <= ruido <= 1:
        raise ValueError("Ruido fora de 0 a 1")

    seguro = confianca >= 0.85 and ruido <= 0.30

    return {
        "confianca": confianca,
        "ruido": ruido,
        "acao": (
            "PROSSEGUIR_NA_SIMULACAO"
            if seguro
            else "SOLICITAR_CONFIRMACAO"
        ),
    }


def main():
    print("=" * 60)
    print("ALURA - ENGENHARIA DE SOFTWARE PARA DADOS")
    print("AULA 01 - IMPORTANCIA DA ENGENHARIA")
    print("=" * 60)

    print("\n1. MUDANCA NOS DADOS - EXEMPLO DIDATICO")
    flu = detectar_mudanca(0.12, 0.35)
    print(json.dumps(flu, indent=2, ensure_ascii=False))

    print("\n2. DISPARIDADE ENTRE GRUPOS - EXEMPLO DIDATICO")
    contratacao = verificar_disparidade(0.80, 0.50)
    print(json.dumps(contratacao, indent=2, ensure_ascii=False))

    print("\n3. ROBUSTEZ DE VOZ - EXEMPLO DIDATICO")
    voz = avaliar_pedido_voz(0.55, 0.70)
    print(json.dumps(voz, indent=2, ensure_ascii=False))

    print("\n4. GERANDO EVIDENCIAS")

    RESULTADOS.mkdir(parents=True, exist_ok=True)

    relatorio = {
        "aula": 1,
        "curso": "Engenharia de software para dados",
        "tema": "Importancia da engenharia em projetos de dados",
        "gerado_em_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "casos_estudados": [
            "Google Flu Trends",
            "Amazon Hiring Tool",
            "McDonald's - IA no drive-thru",
        ],
        "simulacoes": {
            "mudanca_dados": flu,
            "disparidade_grupos": contratacao,
            "robustez_voz": voz,
        },
        "limitacoes": [
            "Todos os numeros sao inventados.",
            "Nao foram usados dados dos casos reais.",
            "Nao foi treinado modelo de ML.",
            "Alertas requerem investigacao e contexto.",
        ],
    }

    destino = RESULTADOS / "aula01_validacoes.json"

    destino.write_text(
        json.dumps(relatorio, ensure_ascii=False, indent=4),
        encoding="utf-8",
    )

    print("Relatorio:", destino.name)

    print("\n5. VERIFICACOES")

    assert flu["alerta"] is True
    assert contratacao["investigar"] is True
    assert voz["acao"] == "SOLICITAR_CONFIRMACAO"
    assert destino.is_file()

    print("\nRESULTADO FINAL")
    print("Cenarios simulados: 3")
    print("Alertas de mudanca nos dados: 1")
    print("Disparidades para investigar: 1")
    print("Pedidos que exigem confirmacao: 1")
    print("Relatorios JSON: 1")
    print("Verificacoes internas: APROVADAS")
    print("Aula 01 executada com sucesso.")


if __name__ == "__main__":
    main()