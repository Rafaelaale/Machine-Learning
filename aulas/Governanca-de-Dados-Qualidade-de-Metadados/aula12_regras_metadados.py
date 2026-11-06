import json
import re

from pathlib import Path

import pandas as pd


BASE = Path(__file__).resolve().parent

ARQUIVO_DADOS = (
    BASE / "resultados" / "metadados_consolidados.csv"
)

ARQUIVO_REGRAS = (
    BASE / "regras" / "regras_metadados.json"
)

ARQUIVO_RESULTADO = (
    BASE / "resultados" / "aula12_inspecao_regras.csv"
)


def mostrar_titulo(titulo):
    print("\n" + "=" * 60)
    print(titulo)
    print("=" * 60)


def main():

    mostrar_titulo("ALURA - AULA 12")
    print("AVALIANDO REGRAS DE METADADOS")

    # CARREGAR DATAFRAME
    df = pd.read_csv(
        ARQUIVO_DADOS,
        encoding="utf-8-sig"
    )

    # CARREGAR REGRAS
    with ARQUIVO_REGRAS.open(
        "r",
        encoding="utf-8"
    ) as arquivo:
        regras = json.load(arquivo)

    print("\nRegistros analisados:", len(df))
    print("Tabelas:", df["nome_tabela"].nunique())

    # ==============================================
    # 1. CATEGORIAS DE CAMADA
    # ==============================================

    mostrar_titulo("1. CAMADAS")

    print("Valores permitidos:")
    print(regras["camadas_validas"])

    print("\nValores encontrados:")
    print(df["camada"].value_counts().to_string())

    # ==============================================
    # 2. PRIVACIDADE
    # ==============================================

    mostrar_titulo("2. PRIVACIDADE")

    print("Valores permitidos:")
    print(regras["privacidade_valida"])

    print("\nValores encontrados:")
    print(
        df["privacidade_coluna"]
        .value_counts(dropna=False)
        .to_string()
    )

    # ==============================================
    # 3. CONFIDENCIALIDADE
    # ==============================================

    mostrar_titulo("3. CONFIDENCIALIDADE")

    print("Valores permitidos:")
    print(regras["confidencialidade_valida"])

    print("\nValores encontrados:")
    print(
        df["confidencialidade_coluna"]
        .value_counts(dropna=False)
        .to_string()
    )

    # ==============================================
    # 4. CONVENCAO DOS BANCOS
    # ==============================================

    mostrar_titulo("4. NOMES DOS BANCOS")

    padrao = re.compile(
        regras["padrao_database"]
    )

    bancos = df[
        ["database", "camada"]
    ].drop_duplicates()

    for _, item in bancos.iterrows():

        database = item["database"]
        camada = item["camada"]

        formato_valido = bool(
            padrao.fullmatch(database)
        )

        prefixo_coerente = (
            database.startswith(f"{camada}_")
        )

        print(
            f"{database} | "
            f"Formato: {formato_valido} | "
            f"Camada coerente: {prefixo_coerente}"
        )

    # ==============================================
    # 5. INSPECAO PRELIMINAR
    # ==============================================

    mostrar_titulo("5. INSPECAO PRELIMINAR")

    inspecao = df[
        [
            "camada",
            "database",
            "nome_tabela",
            "nome_coluna"
        ]
    ].copy()

    inspecao["camada_valida"] = (
        df["camada"].isin(
            regras["camadas_validas"]
        )
    )

    inspecao["database_formato_valido"] = (
        df["database"].apply(
            lambda valor: bool(
                padrao.fullmatch(valor)
            )
            if isinstance(valor, str)
            else False
        )
    )

    inspecao["database_camada_coerente"] = [
        isinstance(database, str)
        and isinstance(camada, str)
        and database.startswith(f"{camada}_")
        for database, camada in zip(
            df["database"],
            df["camada"]
        )
    ]

    inspecao["privacidade_preenchida"] = (
        df["privacidade_coluna"].notna()
    )

    inspecao["privacidade_valida"] = (
        df["privacidade_coluna"].isin(
            regras["privacidade_valida"]
        )
    )

    inspecao["confidencialidade_preenchida"] = (
        df["confidencialidade_coluna"].notna()
    )

    inspecao["confidencialidade_valida"] = (
        df["confidencialidade_coluna"].isin(
            regras["confidencialidade_valida"]
        )
    )

    inspecao["descricao_preenchida"] = (
        df["descricao_coluna"].notna()
    )

    print(
        inspecao[
            [
                "camada",
                "nome_coluna",
                "camada_valida",
                "database_formato_valido",
                "privacidade_preenchida",
                "confidencialidade_preenchida"
            ]
        ].to_string(index=False)
    )

    # ==============================================
    # 6. RESUMO
    # ==============================================

    mostrar_titulo("6. RESUMO DAS REGRAS")

    print(
        "Camadas validas:",
        int(inspecao["camada_valida"].sum()),
        "de",
        len(inspecao)
    )

    print(
        "Databases com formato valido:",
        int(inspecao["database_formato_valido"].sum()),
        "de",
        len(inspecao)
    )

    print(
        "Databases coerentes com a camada:",
        int(inspecao["database_camada_coerente"].sum()),
        "de",
        len(inspecao)
    )

    print(
        "Privacidade preenchida:",
        int(inspecao["privacidade_preenchida"].sum()),
        "de",
        len(inspecao)
    )

    print(
        "Confidencialidade preenchida:",
        int(inspecao["confidencialidade_preenchida"].sum()),
        "de",
        len(inspecao)
    )

    print(
        "Descricao preenchida:",
        int(inspecao["descricao_preenchida"].sum()),
        "de",
        len(inspecao)
    )

    # ==============================================
    # 7. SALVAR RELATORIO
    # ==============================================

    inspecao.to_csv(
        ARQUIVO_RESULTADO,
        index=False,
        encoding="utf-8-sig"
    )

    # ==============================================
    # 8. TESTES
    # ==============================================

    assert df.shape == (15, 9)
    assert inspecao["camada_valida"].all()
    assert inspecao["database_formato_valido"].all()
    assert inspecao["database_camada_coerente"].all()

    assert (
        inspecao["privacidade_preenchida"].sum()
        == 2
    )

    assert (
        inspecao["confidencialidade_preenchida"].sum()
        == 2
    )

    assert (
        inspecao["descricao_preenchida"].sum()
        == 8
    )

    assert (
        inspecao["privacidade_valida"].sum()
        == 2
    )

    assert (
        inspecao["confidencialidade_valida"].sum()
        == 2
    )

    assert ARQUIVO_RESULTADO.exists()

    mostrar_titulo("RESULTADO FINAL")

    print("Regras de governanca definidas.")
    print("Categorias de metadados analisadas.")
    print("Convencoes de nomes verificadas.")
    print("Relatorio de inspecao salvo.")
    print("Todos os testes passaram.")
    print("Aula 12 executada com sucesso.")


if __name__ == "__main__":
    main()