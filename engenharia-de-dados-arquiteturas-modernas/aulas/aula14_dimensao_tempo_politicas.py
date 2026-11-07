"""Aula 14 - Reprocessamento de fevereiro e dimensao Tempo."""

import json
import sys
from pathlib import Path


BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from src.aula14_dimensao_tempo_politicas import (
    preparar_banco,
    registrar_cliente,
    reprocessar_periodo,
    consultar_resumo,
    valores_por_mes,
    serie_diaria,
    importar_periodo_oltp,
)


def main():
    banco = (
        BASE / "dados" / "processed"
        / "minishop_politicas_aula14.db"
    )

    preparar_banco(banco)

    for codigo, nome in [
        ("02342", "Cliente 2"),
        ("40032", "Cliente 3"),
        ("56700", "Cliente 8"),
    ]:
        registrar_cliente(banco, codigo, nome)

    janeiro = [
        {
            "movimento_id": "JAN-1",
            "cliente": "40032",
            "data": "2025-01-10",
            "valor_centavos": 2000,
        },
    ]

    fevereiro_original = [
        {
            "movimento_id": "FEV-1",
            "cliente": "02342",
            "data": "2025-02-01",
            "valor_centavos": 1000,
        },
        {
            "movimento_id": "FEV-2",
            "cliente": "40032",
            "data": "2025-02-10",
            "valor_centavos": 800,
        },
    ]

    fevereiro_corrigido = [
        {
            "movimento_id": "FEV-1",
            "cliente": "02342",
            "data": "2025-02-01",
            "valor_centavos": 1500,
        },
        {
            "movimento_id": "FEV-3",
            "cliente": "56700",
            "data": "2025-02-20",
            "valor_centavos": 1400,
        },
    ]

    print("===== AULA 14 - DIMENSAO TEMPO E CARGAS =====")

    print("\n1. CARREGANDO JANEIRO")
    reprocessar_periodo(
        banco, 2025, 1, janeiro, lote_completo=True
    )

    print("\n2. CARREGANDO FEVEREIRO ORIGINAL")
    original = reprocessar_periodo(
        banco, 2025, 2,
        fevereiro_original,
        lote_completo=True,
    )
    print(json.dumps(original, indent=2))

    print("\n3. REPROCESSANDO FEVEREIRO COMPLETO")
    corrigido = reprocessar_periodo(
        banco, 2025, 2,
        fevereiro_corrigido,
        lote_completo=True,
    )
    print(json.dumps(corrigido, indent=2))

    print("\n4. FATURAMENTO POR MES")
    mensal = valores_por_mes(banco)
    print(json.dumps(mensal, indent=2))

    print("\n5. CALENDARIO CONTINUO")
    resumo = consultar_resumo(banco)
    print(json.dumps(resumo, indent=2))

    serie = serie_diaria(banco)
    sem_vendas = sum(
        linha["valor_centavos"] == 0
        for linha in serie
    )
    print("Dias sem vendas:", sem_vendas)

    if mensal.get("2025-01") != 2000:
        raise RuntimeError("Janeiro foi alterado")

    if mensal.get("2025-02") != 2900:
        raise RuntimeError("Fevereiro incorreto")

    if resumo["total_centavos"] != 4900:
        raise RuntimeError("Faturamento inconsistente")

    print("\n6. EXTRAINDO OLTP DA MINISHOP")

    origem = (
        BASE / "dados" / "processed"
        / "minishop_modelo_logico_aula05.db"
    )

    if not origem.is_file():
        raise FileNotFoundError(origem)

    # Descobre automaticamente os meses das vendas
    # confirmadas, sem presumir o calendario do computador.
    from contextlib import closing
    import sqlite3

    with closing(
        sqlite3.connect(
            origem.resolve().as_uri() + "?mode=ro",
            uri=True,
        )
    ) as conexao:
        meses = conexao.execute(
            """
            SELECT DISTINCT substr(data_pedido, 1, 7)
            FROM pedidos
            WHERE estado = 'confirmado'
            ORDER BY 1
            """
        ).fetchall()

    banco_real = (
        BASE / "dados" / "processed"
        / "minishop_politicas_aula14_oltp.db"
    )

    importacoes = []

    for (periodo,) in meses:
        ano, mes = map(int, periodo.split("-"))

        importacoes.append(
            importar_periodo_oltp(
                origem, banco_real, ano, mes
            )
        )

    print(json.dumps(importacoes, indent=2))

    print("\n7. SALVANDO RELATORIO")

    relatorio = {
        "aula": 14,
        "tema": "Dimensao Tempo e politicas de carga",
        "fevereiro_original": original,
        "fevereiro_reprocessado": corrigido,
        "mensal": mensal,
        "resumo": resumo,
        "dias_sem_vendas": sem_vendas,
        "extracao_oltp": importacoes,
        "limites": [
            "Cada reprocessamento exige um lote completo",
            "A origem OLTP e acessada somente para leitura",
            "A dimensao Tempo usa SK deterministica AAAAMMDD",
            "Alteracoes anteriores ao inicio de uma vigencia SCD2 exigem lookup temporal",
            "Em producao, uma fotografia completa exige corte consistente da fonte",
        ],
    }

    arquivo = (
        BASE / "resultados"
        / "aula14_dimensao_tempo_politicas.json"
    )

    arquivo.write_text(
        json.dumps(
            relatorio, indent=2, ensure_ascii=False
        ),
        encoding="utf-8",
    )

    print("Relatorio:", arquivo)
    print("AULA 14 EXECUTADA COM SUCESSO!")


if __name__ == "__main__":
    main()
