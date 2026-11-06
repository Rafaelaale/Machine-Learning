"""Laboratorio da Aula 09 com a base oficial da Alura."""

import json
import sys
from datetime import date, timedelta
from pathlib import Path

import pandas as pd


BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from src.aula09_paradigmas import (
    ClienteChurn,
    adicionar_risco,
    resumir_riscos,
)


ARQUIVO = (
    BASE / "material_alura"
    / "projeto-CHURN"
    / "Churn-antes"
    / "dados_corretos2.csv"
)

REFERENCIA = date(2026, 11, 6)


def main():
    print("=" * 60)
    print("AULA 09 - PROGRAMACAO ORIENTADA A OBJETOS E FUNCIONAL")
    print("=" * 60)

    base_original = pd.read_csv(ARQUIVO, low_memory=False)
    copia_original = base_original.copy(deep=True)

    print("\n1. BASE OFICIAL")
    print("Registros originais:", len(base_original))

    print("\n2. PROGRAMACAO FUNCIONAL")
    classificados = adicionar_risco(base_original)
    resumo = resumir_riscos(base_original)

    print("Registros validos:", resumo["total_clientes"])
    print("Clientes em risco pela regra:", resumo["clientes_em_risco"])
    print("Percentual em risco:", resumo["percentual_risco"])

    print("\n3. PROGRAMACAO ORIENTADA A OBJETOS")

    if classificados.empty:
        raise ValueError("Nenhum registro valido disponivel")

    registro = classificados.iloc[0]
    dias_inativos = int(registro["days_since_last_purchase"])

    cliente = ClienteChurn(
        cliente_id=f"ALURA-{classificados.index[0]}",
        ultima_atividade=(
            REFERENCIA - timedelta(days=dias_inativos)
        ),
        produto_id=None,
        valor_total_compras=float(registro["total_spent"]),
        frequencia_compras=int(registro["num_orders"]),
        tempo_desde_primeira_compra=None,
        status_churn=bool(int(registro["churn"])),
    )

    print("Cliente:", cliente.cliente_id)
    print("Dias de inatividade:", cliente.calcular_tempo_inatividade(
        REFERENCIA
    ))
    print("Churn observado:", cliente.status_churn)
    print("Risco estimado por regra:", cliente.prever_churn(
        REFERENCIA
    ))
    print("Alerta:", cliente.notificar_cliente(REFERENCIA))

    print("\n4. INTEGRIDADE DOS DADOS")
    pd.testing.assert_frame_equal(
        base_original,
        copia_original,
    )
    print("DataFrame original preservado: SIM")

    print("\n5. RELATORIO")
    destino = BASE / "resultados" / "aula09_paradigmas.json"

    relatorio = {
        "aula": 9,
        "tema": "POO e programacao funcional",
        "fonte": "CSV oficial da Alura",
        "referencia": REFERENCIA.isoformat(),
        "resultado": resumo,
        "observacoes": [
            "Classificacao baseada em regra didatica.",
            "Nenhum modelo de ML foi treinado nesta aula.",
            "Nenhuma notificacao real foi enviada.",
            "Produto e primeira compra desconhecidos na entidade.",
            "A base original foi preservada.",
        ],
    }

    destino.write_text(
        json.dumps(relatorio, indent=4, ensure_ascii=False),
        encoding="utf-8",
    )

    print("Relatorio salvo:", destino.name)
    print("\nAULA 09 EXECUTADA COM SUCESSO!")


if __name__ == "__main__":
    main()
