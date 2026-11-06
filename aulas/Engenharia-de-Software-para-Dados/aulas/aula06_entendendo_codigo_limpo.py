from pathlib import Path
import sys
import json

import pandas as pd


BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from src.aula06_codigo_limpo import (
    preencher_valores_ausentes,
    calcular_tempo_do_pedido,
    normalizar_valor_da_compra,
    preprocessar_pedidos,
)


DADOS = BASE / "dados" / "aula06_pedidos_ficticios.csv"
RESULTADOS = BASE / "resultados"
ANO_REFERENCIA = 2026


def titulo(mensagem):
    print("\n" + "=" * 65)
    print(mensagem)
    print("=" * 65)


def main():
    titulo("ALURA - AULA 06")
    print("ENTENDENDO CODIGO LIMPO")

    titulo("1. CARREGANDO DADOS")

    df_original = pd.read_csv(DADOS)

    copia_original = df_original.copy(deep=True)

    print("Registros:", len(df_original))
    print("Colunas:", list(df_original.columns))
    print("Nulos antes:")
    print(df_original.isna().sum().to_string())

    titulo("2. FUNCOES PEQUENAS E DESCRITIVAS")

    df_preenchido = preencher_valores_ausentes(
        df_original
    )

    df_com_tempo = calcular_tempo_do_pedido(
        df_preenchido,
        ano_referencia=ANO_REFERENCIA,
    )

    df_normalizado = normalizar_valor_da_compra(
        df_com_tempo
    )

    print("Preenchimento de ausentes: OK")
    print("Calculo da idade do pedido: OK")
    print("Normalizacao min-max: OK")

    titulo("3. PIPELINE DE PRE-PROCESSAMENTO")

    df_processado = preprocessar_pedidos(
        df_original,
        ano_referencia=ANO_REFERENCIA,
    )

    pd.testing.assert_frame_equal(
        df_processado, df_normalizado
    )

    print(df_processado.to_string(index=False))

    titulo("4. PRESERVANDO O DATAFRAME ORIGINAL")

    pd.testing.assert_frame_equal(
        df_original, copia_original
    )

    print("Original preservado: SIM")
    print("Pipeline produz o mesmo resultado: SIM")

    titulo("5. GERANDO RELATORIOS")

    RESULTADOS.mkdir(parents=True, exist_ok=True)

    arquivo_csv = (
        RESULTADOS / "aula06_pedidos_processados.csv"
    )

    arquivo_json = (
        RESULTADOS / "aula06_relatorio_codigo_limpo.json"
    )

    df_processado.to_csv(
        arquivo_csv, index=False, encoding="utf-8-sig"
    )

    relatorio = {
        "aula": 6,
        "tema": "Entendendo codigo limpo",
        "referencia": "PEP 8 e principios de Clean Code",
        "registros": len(df_processado),
        "colunas": list(df_processado.columns),
        "ano_referencia": ANO_REFERENCIA,
        "nulos_antes": {
            coluna: int(valor)
            for coluna, valor in df_original.isna().sum().items()
        },
        "nulos_depois": {
            coluna: int(valor)
            for coluna, valor in df_processado.isna().sum().items()
        },
        "funcoes": [
            "validar_colunas",
            "preencher_valores_ausentes",
            "calcular_tempo_do_pedido",
            "normalizar_valor_da_compra",
            "preprocessar_pedidos",
        ],
        "principios": [
            "KISS",
            "funcoes com responsabilidade clara",
            "nomes descritivos",
            "docstrings",
            "type hints",
            "tratamento de casos extremos",
            "preservacao do DataFrame original",
        ],
        "limitacoes": [
            "Dados de pedidos totalmente ficticios.",
            "Nao foi treinado modelo de churn.",
            "Normalizacao ajustada apenas para a demonstracao.",
            "Em ML, ajustar o escalonamento somente no treino.",
        ],
    }

    arquivo_json.write_text(
        json.dumps(
            relatorio,
            ensure_ascii=False,
            indent=4,
        ),
        encoding="utf-8",
    )

    print("CSV:", arquivo_csv.name)
    print("JSON:", arquivo_json.name)

    titulo("6. VERIFICACOES INTERNAS")

    assert len(df_original) == 6
    assert len(df_processado) == 6

    assert df_processado["quantidade_pedida"].isna().sum() == 0
    assert df_processado["categoria"].isna().sum() == 0

    assert "tempo_pedido_anos" in df_processado.columns
    assert "valor_compra_normalizado" in df_processado.columns

    assert (
        df_processado["valor_compra_normalizado"]
        .between(0, 1).all()
    )

    assert arquivo_csv.is_file()
    assert arquivo_json.is_file()

    salvo = json.loads(
        arquivo_json.read_text(encoding="utf-8")
    )

    assert salvo["aula"] == 6

    titulo("RESULTADO FINAL")

    print("Pedidos processados:", len(df_processado))
    print("Funcoes de processamento: 5")
    print("Valores ausentes tratados: 4")
    print("Ano de referencia:", ANO_REFERENCIA)
    print("DataFrame original preservado: SIM")
    print("Relatorios gerados: 2")
    print("Verificacoes internas: APROVADAS")
    print("Aula 06 executada com sucesso.")


if __name__ == "__main__":
    main()