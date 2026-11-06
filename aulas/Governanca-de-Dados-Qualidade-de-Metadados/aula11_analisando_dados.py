from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent

PASTA_RESULTADOS = BASE_DIR / "resultados"

ARQUIVO_CSV = (
    PASTA_RESULTADOS / "metadados_consolidados.csv"
)


def exibir_titulo(titulo):
    print("\n" + "=" * 65)
    print(titulo)
    print("=" * 65)


def main():

    exibir_titulo("ALURA - AULA 11 - ANALISANDO OS DADOS")

    # ==============================================
    # 1. CARREGAR METADADOS
    # ==============================================

    df_concatenado = pd.read_csv(
        ARQUIVO_CSV,
        encoding="utf-8-sig"
    )

    print("\nDATAFRAME CARREGADO")
    print("Linhas:", len(df_concatenado))
    print("Colunas:", len(df_concatenado.columns))
    print("Tabelas:", df_concatenado["nome_tabela"].nunique())

    # ==============================================
    # 2. AGRUPAR METADADOS POR TABELA
    # ==============================================

    exibir_titulo("1. GROUPBY - METADADOS POR TABELA")

    agrupamento = df_concatenado.groupby(
        by=["database", "nome_tabela"]
    ).count()

    print(agrupamento.to_string())

    # ==============================================
    # 3. TIPOS DE DADOS
    # ==============================================

    exibir_titulo("2. TIPOS DE DADOS")

    print(
        df_concatenado["datatype_coluna"]
        .value_counts(dropna=False)
        .to_string()
    )

    # ==============================================
    # 4. CLASSIFICACAO DE PRIVACIDADE
    # ==============================================

    exibir_titulo("3. PRIVACIDADE")

    print(
        df_concatenado["privacidade_coluna"]
        .value_counts(dropna=False)
        .to_string()
    )

    # ==============================================
    # 5. CLASSIFICACAO DE CONFIDENCIALIDADE
    # ==============================================

    exibir_titulo("4. CONFIDENCIALIDADE")

    print(
        df_concatenado["confidencialidade_coluna"]
        .value_counts(dropna=False)
        .to_string()
    )

    # ==============================================
    # 6. FILTRAR DADOS CONFIDENCIAIS
    # ==============================================

    exibir_titulo("5. COLUNAS CONFIDENCIAIS")

    confidenciais = df_concatenado[
        df_concatenado["confidencialidade_coluna"]
        == "confidencial"
    ]

    print(
        confidenciais[
            [
                "nome_tabela",
                "nome_coluna",
                "confidencialidade_coluna"
            ]
        ].to_string(index=False)
    )

    # ==============================================
    # 7. FILTRAR DADOS RESTRITOS
    # ==============================================

    exibir_titulo("6. COLUNAS RESTRITAS")

    restritos = df_concatenado[
        df_concatenado["confidencialidade_coluna"]
        == "restrito"
    ]

    print(
        restritos[
            [
                "nome_tabela",
                "nome_coluna",
                "confidencialidade_coluna"
            ]
        ].to_string(index=False)
    )

    # ==============================================
    # 8. AMOSTRA DE METADADOS
    # ==============================================

    exibir_titulo("7. AMOSTRA DE 3 REGISTROS")

    amostra = df_concatenado.sample(
        n=min(3, len(df_concatenado)),
        random_state=42
    )

    print(
        amostra[
            [
                "nome_tabela",
                "nome_coluna",
                "descricao_coluna"
            ]
        ].to_string(index=False)
    )

    # ==============================================
    # 9. IDENTIFICAR DADOS AUSENTES
    # ==============================================

    exibir_titulo("8. VALORES NULOS")

    valores_nulos = df_concatenado.isna().sum()

    print(valores_nulos.to_string())

    # ==============================================
    # 10. CALCULAR COMPLETUDE
    # ==============================================

    exibir_titulo("9. COMPLETUDE DOS METADADOS")

    total = len(df_concatenado)

    relatorio = pd.DataFrame({
        "campo": df_concatenado.columns,
        "total_registros": total,
        "preenchidos": df_concatenado.notna().sum().values,
        "ausentes": df_concatenado.isna().sum().values,
        "percentual_preenchido": (
            df_concatenado.notna().mean().values * 100
        ).round(2)
    })

    print(relatorio.to_string(index=False))

    # ==============================================
    # 11. ANALISAR AUSENCIAS POR CAMADA
    # ==============================================

    exibir_titulo("10. AUSENCIAS POR CAMADA")

    campos = [
        "descricao_coluna",
        "privacidade_coluna",
        "confidencialidade_coluna"
    ]

    ausencias_camada = (
        df_concatenado.groupby("camada")[campos]
        .agg(lambda coluna: coluna.isna().sum())
    )

    print(ausencias_camada.to_string())

    # ==============================================
    # 12. COLUNAS SEM DESCRICAO
    # ==============================================

    exibir_titulo("11. COLUNAS SEM DESCRICAO")

    sem_descricao = df_concatenado[
        df_concatenado["descricao_coluna"].isna()
    ]

    print(
        sem_descricao[
            ["camada", "nome_tabela", "nome_coluna"]
        ].to_string(index=False)
    )

    # ==============================================
    # 13. SALVAR RELATORIOS
    # ==============================================

    relatorio.to_csv(
        PASTA_RESULTADOS / "aula11_completude_metadados.csv",
        index=False,
        encoding="utf-8-sig"
    )

    ausencias_camada.to_csv(
        PASTA_RESULTADOS / "aula11_ausencias_por_camada.csv",
        encoding="utf-8-sig"
    )

    # ==============================================
    # 14. TESTES
    # ==============================================

    assert df_concatenado.shape == (15, 9)

    assert df_concatenado["nome_tabela"].nunique() == 3

    assert set(df_concatenado["camada"]) == {
        "bz", "sl", "gd"
    }

    assert len(confidenciais) == 1
    assert len(restritos) == 1

    assert (
        confidenciais.iloc[0]["nome_coluna"]
        == "modelo_utilizado"
    )

    assert (
        restritos.iloc[0]["nome_coluna"]
        == "versao_modelo"
    )

    assert len(sem_descricao) == 7

    assert relatorio["ausentes"].ge(0).all()

    # ==============================================
    # RESULTADO FINAL
    # ==============================================

    exibir_titulo("RESULTADO FINAL")

    print("Tabelas analisadas: 3")
    print("Colunas analisadas: 15")
    print("Colunas sem descricao:", len(sem_descricao))
    print("Colunas confidenciais:", len(confidenciais))
    print("Colunas restritas:", len(restritos))
    print("Relatorios CSV: 2")
    print("Todos os testes passaram.")
    print("Aula 11 executada com sucesso.")


if __name__ == "__main__":
    main()