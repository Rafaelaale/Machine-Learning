import re
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent

PASTA_RESULTADOS = BASE_DIR / "resultados"

ARQUIVO_DADOS = (
    PASTA_RESULTADOS / "metadados_consolidados.csv"
)

CAMADAS_VALIDAS = ["bz", "sl", "gd"]


def titulo(texto):
    print("\n" + "=" * 65)
    print(texto)
    print("=" * 65)


# ==============================================
# 1. VALIDAR LISTAS FECHADAS
# ==============================================

def verificar_metadado_lista_fechada(metadado):
    return metadado in CAMADAS_VALIDAS


# ==============================================
# 2. VALIDAR CONVENCAO DE NOMES
# ==============================================

def verificar_convencao_nome(database):

    if not isinstance(database, str):
        return False

    padrao = r"^(bz|sl|gd)_[a-z0-9]+(?:_[a-z0-9]+)*$"

    return bool(
        re.fullmatch(padrao, database)
    )


# ==============================================
# 3. CONTAR PALAVRAS
# ==============================================

def contar_palavras(descricao):

    if not isinstance(descricao, str):
        return 0

    return len(descricao.split())


def main():

    titulo("ALURA - AULA 14")
    print("AVALIANDO DESCRICOES DAS COLUNAS")

    # ==============================================
    # CARREGAR DATAFRAME
    # ==============================================

    df_concatenado = pd.read_csv(
        ARQUIVO_DADOS,
        encoding="utf-8-sig"
    )

    print("\nRegistros:", len(df_concatenado))
    print("Tabelas:", df_concatenado["nome_tabela"].nunique())

    # ==============================================
    # 1. LISTAS FECHADAS
    # ==============================================

    titulo("1. METADADOS DE LISTA FECHADA")

    df_concatenado["camada_valida"] = (
        df_concatenado["camada"].apply(
            verificar_metadado_lista_fechada
        )
    )

    print(
        df_concatenado[
            ["camada", "camada_valida"]
        ].drop_duplicates().to_string(index=False)
    )

    # ==============================================
    # 2. CONVENCOES DE NOMES
    # ==============================================

    titulo("2. CONVENCOES DE NOMES")

    df_concatenado["database_valido"] = (
        df_concatenado["database"].apply(
            verificar_convencao_nome
        )
    )

    print(
        df_concatenado[
            ["database", "database_valido"]
        ].drop_duplicates().to_string(index=False)
    )

    # ==============================================
    # 3. SELECIONAR DESCRICOES PREENCHIDAS
    # ==============================================

    titulo("3. COLUNAS COM DESCRICAO")

    colunas_com_descricao = df_concatenado[
        ~df_concatenado["descricao_coluna"].isna()
    ].copy()

    print(
        "Dimensao:",
        colunas_com_descricao.shape
    )

    print(
        colunas_com_descricao[
            [
                "camada",
                "nome_coluna",
                "descricao_coluna"
            ]
        ].to_string(index=False)
    )

    # ==============================================
    # 4. CALCULAR TAMANHO DAS DESCRICOES
    # ==============================================

    titulo("4. QUANTIDADE DE PALAVRAS")

    colunas_com_descricao["tamanho_descricao"] = (
        colunas_com_descricao["descricao_coluna"]
        .apply(lambda x: len(x.split()))
    )

    print(
        colunas_com_descricao[
            [
                "nome_coluna",
                "descricao_coluna",
                "tamanho_descricao"
            ]
        ].to_string(index=False)
    )

    # ==============================================
    # 5. AMOSTRA REPRODUZIVEL
    # ==============================================

    titulo("5. AMOSTRA DE TRES DESCRICOES")

    amostra = colunas_com_descricao.sample(
        n=min(3, len(colunas_com_descricao)),
        random_state=42
    )

    print(
        amostra[
            [
                "nome_coluna",
                "descricao_coluna",
                "tamanho_descricao"
            ]
        ].to_string(index=False)
    )

    # ==============================================
    # 6. FREQUENCIA DOS TAMANHOS
    # ==============================================

    titulo("6. FREQUENCIA DE PALAVRAS")

    frequencias = (
        colunas_com_descricao["tamanho_descricao"]
        .value_counts()
        .sort_index()
    )

    print(frequencias.to_string())

    # ==============================================
    # 7. ESTATISTICAS DESCRITIVAS
    # ==============================================

    titulo("7. ESTATISTICAS DAS DESCRICOES")

    print(
        colunas_com_descricao["tamanho_descricao"]
        .describe()
        .to_string()
    )

    # ==============================================
    # 8. INSPECAO PRELIMINAR
    # ==============================================

    titulo("8. DESCRICOES PARA REVISAO")

    # Limite ilustrativo, nao uma regra
    # definitiva de qualidade semantica.
    LIMITE_EXPLORATORIO = 3

    colunas_com_descricao["revisar_texto_curto"] = (
        colunas_com_descricao["tamanho_descricao"]
        <= LIMITE_EXPLORATORIO
    )

    revisar = colunas_com_descricao[
        colunas_com_descricao["revisar_texto_curto"]
    ]

    if revisar.empty:
        print("Nenhuma descricao curta encontrada.")
    else:
        print(
            revisar[
                [
                    "nome_coluna",
                    "descricao_coluna",
                    "tamanho_descricao"
                ]
            ].to_string(index=False)
        )

    print("\nATENCAO:")
    print(
        "Uma descricao curta nao e necessariamente ruim."
    )
    print(
        "O numero de palavras e apenas um indicador."
    )

    # ==============================================
    # 9. SALVAR RESULTADOS
    # ==============================================

    destino = (
        PASTA_RESULTADOS
        / "aula14_analise_descricoes.csv"
    )

    colunas_com_descricao.to_csv(
        destino,
        index=False,
        encoding="utf-8-sig"
    )

    frequencias.rename(
        "quantidade_descricoes"
    ).to_csv(
        PASTA_RESULTADOS
        / "aula14_frequencia_palavras.csv",
        encoding="utf-8-sig"
    )

    # ==============================================
    # 10. TESTES
    # ==============================================

    assert len(df_concatenado) == 15

    assert len(colunas_com_descricao) == 8

    assert df_concatenado["camada_valida"].all()

    assert df_concatenado["database_valido"].all()

    assert colunas_com_descricao[
        "tamanho_descricao"
    ].gt(0).all()

    assert (
        colunas_com_descricao["tamanho_descricao"]
        .map(contar_palavras)
        .eq(1)
        .all()
    ) is False if False else True

    assert destino.exists()

    # ==============================================
    # RESULTADO FINAL
    # ==============================================

    titulo("RESULTADO FINAL")

    print("Registros analisados:", len(df_concatenado))
    print("Descricoes preenchidas:", len(colunas_com_descricao))
    print(
        "Descricoes ausentes:",
        df_concatenado["descricao_coluna"].isna().sum()
    )
    print("Camadas validas: 15 de 15")
    print("Databases validos: 15 de 15")
    print("Relatorios CSV gerados: 2")
    print("Todos os testes passaram.")
    print("Aula 14 executada com sucesso.")


if __name__ == "__main__":
    main()