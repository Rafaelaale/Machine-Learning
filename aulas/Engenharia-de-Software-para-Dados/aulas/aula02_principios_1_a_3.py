from pathlib import Path
import sys
import json


BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from src.aula02_churn import (
    carregar_clientes,
    analisar_clientes,
    resumir,
)


DADOS = BASE / "dados" / "aula02_clientes_ficticios.csv"
RESULTADOS = BASE / "resultados"


def titulo(mensagem):
    print("\n" + "=" * 65)
    print(mensagem)
    print("=" * 65)


def main():
    titulo("ALURA - AULA 02")
    print("PRINCIPIOS DA ENGENHARIA DE SOFTWARE")

    titulo("1. RAZAO DE EXISTIR")

    objetivo = (
        "Identificar clientes ficticios que merecem "
        "uma revisao de relacionamento."
    )

    print("Objetivo:", objetivo)
    print("Beneficio esperado: apoiar a equipe de retencao.")
    print("O sistema nao decide cancelamentos.")

    titulo("2. KISS - SIMPLICIDADE")

    clientes = carregar_clientes(DADOS)
    resultados = analisar_clientes(clientes)
    resumo = resumir(resultados)

    print("Carregamento centralizado: OK")
    print("Validacao dos dados: OK")
    print("Classificacao em funcao unica: OK")

    for cliente in resultados:
        print(
            cliente["cliente_id"],
            "->",
            cliente["classificacao"]
        )

    titulo("3. MANTER A VISAO")

    arquitetura = {
        "objetivo": objetivo,
        "entrada": "dados/aula02_clientes_ficticios.csv",
        "modulo": "src/aula02_churn.py",
        "execucao": "aulas/aula02_principios_1_a_3.py",
        "testes": "tests/test_aula02_principios.py",
        "saida": "resultados/aula02_analise_churn.json",
        "restricoes": [
            "Usar apenas dados ficticios.",
            "Nao calcular probabilidade de churn.",
            "Nao substituir avaliacao humana.",
            "Preservar regras simples e testaveis.",
        ],
    }

    for nome, descricao in arquitetura.items():
        print(nome, ":", descricao)

    titulo("4. GERANDO RELATORIO")

    RESULTADOS.mkdir(parents=True, exist_ok=True)

    relatorio = {
        "aula": 2,
        "principios": [
            "Razao de existir",
            "KISS",
            "Manter a visao",
        ],
        "arquitetura": arquitetura,
        "resumo": resumo,
        "clientes": resultados,
        "tipo": "laboratorio didatico",
        "observacao": (
            "Classificacao por regras ficticias; "
            "nao e previsao estatistica de churn."
        ),
    }

    destino = RESULTADOS / "aula02_analise_churn.json"

    destino.write_text(
        json.dumps(
            relatorio, ensure_ascii=False, indent=4
        ),
        encoding="utf-8",
    )

    print("Relatorio:", destino.name)

    titulo("5. VERIFICACOES")

    assert len(clientes) == 8
    assert resumo["total_clientes"] == 8
    assert resumo["clientes_para_revisao"] == 4
    assert resumo["acompanhamento_normal"] == 4
    assert resumo["percentual_revisao"] == 50.0
    assert destino.is_file()

    salvo = json.loads(
        destino.read_text(encoding="utf-8")
    )

    assert salvo["aula"] == 2
    assert len(salvo["principios"]) == 3

    titulo("RESULTADO FINAL")

    print("Principios aplicados: 3")
    print("Clientes ficticios analisados: 8")
    print("Clientes para revisao: 4")
    print("Clientes em acompanhamento normal: 4")
    print("Percentual para revisao: 50.0%")
    print("Relatorios JSON gerados: 1")
    print("Verificacoes internas: APROVADAS")
    print("Aula 02 executada com sucesso.")


if __name__ == "__main__":
    main()