"""Executa o exemplo didatico de contas a receber."""

import json
import sys
from pathlib import Path


BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from src.aula24_exemplo_camadas import (
    executar,
    consultar_gold,
)


def main():
    resultado = executar()

    print("===== AULA 24 - EXEMPLO DAS CAMADAS =====")

    print("\n1. CAMADAS CRIADAS")
    for nome in ("oltp", "bronze", "silver", "gold", "dw"):
        print(nome.upper(), resultado[nome])

    print("\n2. GOLD - AGING DAS FATURAS")

    linhas = consultar_gold(
        resultado["gold"],
        """
        SELECT
            id_fatura,
            cidade,
            estado,
            status,
            atraso_pagamento_dias,
            dias_vencido_referencia,
            aging,
            inadimplente_atual,
            pago_com_atraso
        FROM dados
        ORDER BY id_fatura
        """,
    )

    print(json.dumps(
        linhas, indent=2, ensure_ascii=False
    ))

    print("\n3. INDICADORES")
    print(json.dumps(
        resultado["indicadores"],
        indent=2,
        ensure_ascii=False,
    ))

    print("\n4. INADIMPLENCIA POR CIDADE")
    print(json.dumps(
        resultado["por_cidade"],
        indent=2,
        ensure_ascii=False,
    ))

    print("\n5. INADIMPLENCIA POR ESTADO")
    print(json.dumps(
        resultado["por_estado"],
        indent=2,
        ensure_ascii=False,
    ))

    print("\n6. RECONCILIACAO GOLD X DW")
    print("Reconciliado:", resultado["reconciliado"])

    relatorio = (
        BASE / "resultados"
        / "aula24_exemplo_diferentes_camadas.json"
    )

    relatorio.write_text(
        json.dumps(
            resultado, indent=2, ensure_ascii=False
        ),
        encoding="utf-8",
    )

    print("\nRELATORIO:", relatorio)
    print("AULA 24 EXECUTADA COM SUCESSO!")


if __name__ == "__main__":
    main()
