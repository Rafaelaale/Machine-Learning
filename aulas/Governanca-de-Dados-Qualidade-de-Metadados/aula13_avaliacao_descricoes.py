from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent

PASTA_RESULTADOS = BASE_DIR / "resultados"

ARQUIVO_DADOS = (
    PASTA_RESULTADOS / "metadados_consolidados.csv"
)


def titulo(texto):
    print("\n" + "=" * 65)
    print(texto)
    print("=" * 65)


def main():

    titulo("ALURA - AULA 13")
    print("DIFERENTES AVALIACOES DE METADADOS")

    # ==============================================
    # 1. CARREGAR DATAFRAME CONSOLIDADO
    # ==============================================

    df_concatenado = pd.read_csv(
        ARQUIVO_DADOS,
        encoding="utf-8-sig"
    )

    print("\nDATAFRAME CARREGADO")
    print("Registros:", len(df_concatenado))
    print("Tabelas:", df_concatenado["nome_tabela"].nunique())

    # ==============================================
    # 2. AMOSTRA REPRODUZIVEL
    # ==============================================

    titulo("1. AMOSTRA COM RANDOM_STATE=42")

    sample = df_concatenado.sample(
        n=4,
        random_state=42
    )

    print(
        sample[
            [
                "camada",
                "nome_tabela",
                "nome_coluna",
                "descricao_coluna"
            ]
        ].to_string(index=False)
    )

    # ==============================================
    # 3. FILTRAR DATAS DE REFERENCIA
    # ==============================================

    titulo("2. COLUNAS DATA_REFERENCIA")

    datas_referencia = df_concatenado[
        df_concatenado["nome_coluna"] == "data_referencia"
    ].copy()

    print(
        datas_referencia[
            [
                "camada",
                "nome_tabela",
                "nome_coluna",
                "descricao_coluna"
            ]
        ].to_string(index=False)
    )

    print("\nDIMENSAO DO RESULTADO")
    print(datas_referencia.shape)

    # ==============================================
    # 4. DESCRICOES UNICAS
    # ==============================================

    titulo("3. DESCRICOES UNICAS")

    descricoes_unicas = (
        datas_referencia["descricao_coluna"].unique()
    )

    for indice, descricao in enumerate(
        descricoes_unicas,
        start=1
    ):
        print(f"{indice}. {descricao!r}")

    print(
        "\nQuantidade de valores distintos:",
        len(descricoes_unicas)
    )

    # ==============================================
    # 5. CONTAGEM DAS DESCRICOES
    # ==============================================

    titulo("4. FREQUENCIA DAS DESCRICOES")

    frequencias = (
        datas_referencia["descricao_coluna"]
        .value_counts(dropna=False)
    )

    print(frequencias.to_string())

    # ==============================================
    # 6. COMPLETUDE DAS DESCRICOES
    # ==============================================

    titulo("5. COMPLETUDE DAS DESCRICOES")

    total_datas = len(datas_referencia)

    descricoes_preenchidas = int(
        datas_referencia["descricao_coluna"].notna().sum()
    )

    descricoes_ausentes = int(
        datas_referencia["descricao_coluna"].isna().sum()
    )

    percentual = (
        descricoes_preenchidas / total_datas * 100
        if total_datas > 0
        else 0
    )

    print("Total de colunas:", total_datas)
    print("Descricoes preenchidas:", descricoes_preenchidas)
    print("Descricoes ausentes:", descricoes_ausentes)
    print(f"Completude: {percentual:.2f}%")

    # ==============================================
    # 7. COMPARAR TODAS AS DESCRICOES
    # ==============================================

    titulo("6. DESCRICOES DAS COLUNAS")

    comparacao = df_concatenado[
        [
            "camada",
            "nome_tabela",
            "nome_coluna",
            "descricao_coluna"
        ]
    ].copy()

    print(comparacao.to_string(index=False))

    # ==============================================
    # 8. IDENTIFICAR NOMES REPETIDOS
    # ==============================================

    titulo("7. NOMES PRESENTES EM VARIAS TABELAS")

    nomes_repetidos = (
        df_concatenado.groupby("nome_coluna")
        .agg(
            quantidade_tabelas=("nome_tabela", "nunique"),
            descricoes_preenchidas=(
                "descricao_coluna",
                "count"
            )
        )
        .reset_index()
    )

    nomes_repetidos = nomes_repetidos[
        nomes_repetidos["quantidade_tabelas"] > 1
    ]

    print(nomes_repetidos.to_string(index=False))

    # ==============================================
    # 9. INSPECAO TEXTUAL PRELIMINAR
    # ==============================================

    titulo("8. INSPECAO TEXTUAL PRELIMINAR")

    comparacao["descricao_preenchida"] = (
        comparacao["descricao_coluna"].notna()
    )

    comparacao["quantidade_caracteres"] = (
        comparacao["descricao_coluna"]
        .fillna("")
        .str.len()
    )

    print(
        comparacao[
            [
                "camada",
                "nome_coluna",
                "descricao_preenchida",
                "quantidade_caracteres"
            ]
        ].to_string(index=False)
    )

    print("\nIMPORTANTE:")
    print(
        "O tamanho do texto nao comprova sua qualidade."
    )
    print(
        "Clareza, significado e contexto exigem "
        "avaliacao adicional."
    )

    # ==============================================
    # 10. SALVAR RESULTADOS
    # ==============================================

    datas_referencia.to_csv(
        PASTA_RESULTADOS
        / "aula13_datas_referencia.csv",
        index=False,
        encoding="utf-8-sig"
    )

    comparacao.to_csv(
        PASTA_RESULTADOS
        / "aula13_analise_descricoes.csv",
        index=False,
        encoding="utf-8-sig"
    )

    nomes_repetidos.to_csv(
        PASTA_RESULTADOS
        / "aula13_nomes_repetidos.csv",
        index=False,
        encoding="utf-8-sig"
    )

    # ==============================================
    # 11. VALIDAR RESULTADOS
    # ==============================================

    assert df_concatenado.shape == (15, 9)

    assert len(sample) == 4

    assert len(datas_referencia) == 3

    assert descricoes_preenchidas == 2

    assert descricoes_ausentes == 1

    assert len(descricoes_unicas) == 3

    assert "data_referencia" in (
        nomes_repetidos["nome_coluna"].values
    )

    assert (
        comparacao["descricao_preenchida"].sum()
        == 8
    )

    # ==============================================
    # RESULTADO FINAL
    # ==============================================

    titulo("RESULTADO FINAL")

    print("Registros analisados: 15")
    print("Amostra reproduzivel: 4")
    print("Colunas data_referencia: 3")
    print("Descricoes preenchidas: 2")
    print("Descricoes ausentes: 1")
    print("Arquivos CSV gerados: 3")
    print("Todos os testes passaram.")
    print("Aula 13 executada com sucesso.")


if __name__ == "__main__":
    main()