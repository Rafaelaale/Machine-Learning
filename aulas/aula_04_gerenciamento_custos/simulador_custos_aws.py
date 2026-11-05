from decimal import Decimal
from pathlib import Path
import json

# Tarifas ilustrativas em USD.
# Nao representam uma cotacao em tempo real.
PRECO_GLUE_DPU_HORA = Decimal("0.44")
PRECO_ATHENA_TB = Decimal("5.00")


def calcular_glue(dpus, minutos):
    horas = Decimal(str(minutos)) / Decimal("60")
    return Decimal(str(dpus)) * horas * PRECO_GLUE_DPU_HORA


def calcular_athena(tb_consultados):
    return Decimal(str(tb_consultados)) * PRECO_ATHENA_TB


def executar():
    print("===== AULA 04 - SIMULADOR DE CUSTOS AWS =====")
    print("Modo: LOCAL - NENHUMA CONEXAO COM A AWS")

    # Exercicio 1: Glue ETL
    custo_glue = calcular_glue(2, 30)

    # Exercicio 2: Athena
    custo_athena = calcular_athena("0.01")

    total = custo_glue + custo_athena

    print(f"Glue (2 DPUs, 30 minutos): US$ {custo_glue:.2f}")
    print(f"Athena (0.01 TB): US$ {custo_athena:.2f}")
    print(f"Total hipotetico: US$ {total:.2f}")

    # Simulacao da nossa politica de estudo.
    orcamento_real = Decimal("0.00")

    if total > orcamento_real:
        print("ALERTA: Uso real nao autorizado pelo orcamento.")
        print("ALTERNATIVA: executar processamento local.")

    resultado = {
        "aula": 4,
        "modo": "simulacao_local",
        "moeda": "USD",
        "glue": str(custo_glue),
        "athena": str(custo_athena),
        "total_hipotetico": str(total),
        "orcamento_real": str(orcamento_real),
        "cobranca_real": False
    }

    destino = Path(__file__).resolve().parents[2] / "resultados"
    destino.mkdir(parents=True, exist_ok=True)

    arquivo = destino / "aula_04_custos.json"
    arquivo.write_text(
        json.dumps(resultado, indent=4, ensure_ascii=False),
        encoding="utf-8"
    )

    assert custo_glue == Decimal("0.44")
    assert custo_athena == Decimal("0.05")
    assert total == Decimal("0.49")

    print("TESTES: 3/3 APROVADOS")
    print("RELATORIO:", arquivo)
    print("AULA 04 - CONCLUIDA")


if __name__ == "__main__":
    executar()
