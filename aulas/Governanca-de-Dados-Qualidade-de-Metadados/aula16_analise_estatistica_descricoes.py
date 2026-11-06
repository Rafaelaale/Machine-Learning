from pathlib import Path
from collections import Counter
from itertools import combinations
from math import sqrt
import re
import unicodedata

import pandas as pd


BASE = Path(__file__).resolve().parent
RESULTADOS = BASE / "resultados"
ENTRADA = RESULTADOS / "metadados_consolidados.csv"


def titulo(texto):
    print("\n" + "=" * 65)
    print(texto)
    print("=" * 65)


def normalizar(texto):
    texto = unicodedata.normalize("NFKD", texto.lower())
    texto = "".join(
        caracter for caracter in texto
        if not unicodedata.combining(caracter)
    )
    return texto.replace("_", " ")


def tokenizar(texto):
    return re.findall(r"[a-z0-9]+", normalizar(texto))


def gerar_ngramas(texto, n=2):
    palavras = tokenizar(texto)
    return [
        " ".join(palavras[i:i+n])
        for i in range(len(palavras) - n + 1)
    ]


def similaridade_cosseno(texto_a, texto_b):
    vetor_a = Counter(tokenizar(texto_a))
    vetor_b = Counter(tokenizar(texto_b))

    if not vetor_a or not vetor_b:
        return 0.0

    produto = sum(
        valor * vetor_b.get(palavra, 0)
        for palavra, valor in vetor_a.items()
    )

    norma_a = sqrt(sum(v*v for v in vetor_a.values()))
    norma_b = sqrt(sum(v*v for v in vetor_b.values()))

    return produto / (norma_a * norma_b)


def main():
    titulo("ALURA - AULA 16")
    print("OUTRAS FORMAS DE AVALIAR DESCRICOES")

    df = pd.read_csv(ENTRADA, encoding="utf-8-sig")

    descricoes = df[
        df["descricao_coluna"].notna()
    ].copy()

    # ==============================================
    # 1. COMPRIMENTO DAS DESCRICOES
    # ==============================================

    titulo("1. COMPRIMENTO DOS TEXTOS")

    descricoes["quantidade_palavras"] = (
        descricoes["descricao_coluna"]
        .apply(lambda x: len(x.split()))
    )

    descricoes["quantidade_caracteres"] = (
        descricoes["descricao_coluna"].str.len()
    )

    print(
        descricoes[
            [
                "nome_coluna",
                "descricao_coluna",
                "quantidade_palavras",
                "quantidade_caracteres"
            ]
        ].to_string(index=False)
    )

    # ==============================================
    # 2. COMPARAR DESCRICOES DE PRODUTO_ID
    # ==============================================

    titulo("2. DESCRICOES DE PRODUTO_ID")

    produtos = descricoes[
        descricoes["nome_coluna"] == "produto_id"
    ]

    print(
        produtos[
            ["camada", "descricao_coluna"]
        ].to_string(index=False)
    )

    exemplo_didatico = (
        "Identificador único do produto proveniente "
        "do sistema interno de produtos "
        "(Source of Truth)"
    )

    print("\nEXEMPLO DIDATICO DO INSTRUTOR:")
    print(exemplo_didatico)

    print(
        "\nO exemplo nao foi adicionado aos "
        "metadados originais."
    )

    # ==============================================
    # 3. FREQUENCIA DE PALAVRAS
    # ==============================================

    titulo("3. FREQUENCIA DAS PALAVRAS")

    todas_palavras = []

    for descricao in descricoes["descricao_coluna"]:
        todas_palavras.extend(tokenizar(descricao))

    frequencias = Counter(todas_palavras)

    for palavra, quantidade in frequencias.most_common():
        print(f"{palavra}: {quantidade}")

    # ==============================================
    # 4. ESPECIFICIDADE LEXICAL EXPLORATORIA
    # ==============================================

    titulo("4. ESPECIFICIDADE LEXICAL")

    # Frequencia relativa inversa no corpus.
    # E apenas um indicador ilustrativo.
    total_palavras = len(todas_palavras)

    def especificidade(texto):
        palavras = tokenizar(texto)

        if not palavras:
            return 0.0

        return sum(
            1 - frequencias[p] / total_palavras
            for p in palavras
        ) / len(palavras)

    descricoes["indice_especificidade"] = (
        descricoes["descricao_coluna"]
        .apply(especificidade)
    )

    print(
        descricoes[
            [
                "nome_coluna",
                "descricao_coluna",
                "indice_especificidade"
            ]
        ].sort_values(
            "indice_especificidade",
            ascending=False
        ).to_string(index=False)
    )

    print(
        "\nIndice ilustrativo: nao e uma "
        "probabilidade de qualidade."
    )

    # ==============================================
    # 5. ANALISE DE BIGRAMAS
    # ==============================================

    titulo("5. BIGRAMAS DAS DESCRICOES")

    bigramas = []

    for descricao in descricoes["descricao_coluna"]:
        bigramas.extend(gerar_ngramas(descricao, 2))

    frequencia_bigramas = Counter(bigramas)

    for bigrama, quantidade in (
        frequencia_bigramas.most_common(10)
    ):
        print(f"{bigrama}: {quantidade}")

    # ==============================================
    # 6. SIMILARIDADE ENTRE DESCRICOES
    # ==============================================

    titulo("6. SIMILARIDADE DE COSSENO")

    registros = descricoes[
        [
            "camada",
            "nome_tabela",
            "nome_coluna",
            "descricao_coluna"
        ]
    ].to_dict("records")

    comparacoes = []

    for a, b in combinations(registros, 2):
        similaridade = similaridade_cosseno(
            a["descricao_coluna"],
            b["descricao_coluna"]
        )

        comparacoes.append({
            "camada_a": a["camada"],
            "tabela_a": a["nome_tabela"],
            "coluna_a": a["nome_coluna"],
            "camada_b": b["camada"],
            "tabela_b": b["nome_tabela"],
            "coluna_b": b["nome_coluna"],
            "similaridade": round(
                similaridade, 4
            )
        })

    df_similaridade = pd.DataFrame(comparacoes)

    print(
        df_similaridade.sort_values(
            "similaridade",
            ascending=False
        ).head(10).to_string(index=False)
    )

    # ==============================================
    # 7. ANALISE ENTRE CAMADAS
    # ==============================================

    titulo("7. COMPARACAO ENTRE CAMADAS")

    entre_camadas = df_similaridade[
        df_similaridade["camada_a"]
        != df_similaridade["camada_b"]
    ]

    print(
        entre_camadas.sort_values(
            "similaridade",
            ascending=False
        ).head(10).to_string(index=False)
    )

    print(
        "\nSimilaridade lexical nao comprova "
        "equivalencia semantica ou linhagem."
    )

    # ==============================================
    # 8. SALVAR RESULTADOS
    # ==============================================

    titulo("8. SALVAR RELATORIOS")

    arquivo_descritividade = (
        RESULTADOS / "aula16_descritividade.csv"
    )

    arquivo_similaridade = (
        RESULTADOS / "aula16_similaridade.csv"
    )

    arquivo_bigramas = (
        RESULTADOS / "aula16_bigramas.csv"
    )

    descricoes.to_csv(
        arquivo_descritividade,
        index=False,
        encoding="utf-8-sig"
    )

    df_similaridade.to_csv(
        arquivo_similaridade,
        index=False,
        encoding="utf-8-sig"
    )

    pd.DataFrame(
        frequencia_bigramas.items(),
        columns=["bigrama", "frequencia"]
    ).to_csv(
        arquivo_bigramas,
        index=False,
        encoding="utf-8-sig"
    )

    # ==============================================
    # 9. TESTES
    # ==============================================

    titulo("9. TESTES")

    assert df.shape == (15, 9)
    assert len(descricoes) == 8
    assert len(produtos) == 2

    assert len(df_similaridade) == 28

    assert df_similaridade[
        "similaridade"
    ].between(0, 1).all()

    assert abs(
        similaridade_cosseno(
            "Data da previsão",
            "Data da previsão"
        ) - 1
    ) < 1e-10

    assert (
        similaridade_cosseno(
            "Data da previsão",
            "Identificador do produto"
        ) >= 0
    )

    assert all(
        arquivo.exists()
        for arquivo in [
            arquivo_descritividade,
            arquivo_similaridade,
            arquivo_bigramas
        ]
    )

    # ==============================================
    # RESULTADO FINAL
    # ==============================================

    titulo("RESULTADO FINAL")

    print("Descricoes analisadas:", len(descricoes))
    print("Comparacoes realizadas:", len(df_similaridade))
    print("Relatorios CSV gerados: 3")
    print("Analise lexical concluida.")
    print("Todos os testes passaram.")
    print("Aula 16 executada com sucesso.")


if __name__ == "__main__":
    main()