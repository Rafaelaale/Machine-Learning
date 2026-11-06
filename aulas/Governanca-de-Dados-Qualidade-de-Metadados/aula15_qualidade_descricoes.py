from pathlib import Path

import pandas as pd


BASE = Path(__file__).resolve().parent
RESULTADOS = BASE / "resultados"
ENTRADA = RESULTADOS / "metadados_consolidados.csv"


def titulo(texto):
    print("\n" + "=" * 65)
    print(texto)
    print("=" * 65)


def main():
    titulo("ALURA - AULA 15")
    print("BOAS DESCRICOES X DESCRICOES ESPETACULARES")

    # 1. CARREGAR DADOS
    df = pd.read_csv(
        ENTRADA,
        encoding="utf-8-sig"
    )

    # 2. SELECIONAR DESCRICOES EXISTENTES
    colunas_com_descricao = df[
        df["descricao_coluna"].notna()
    ].copy()

    colunas_com_descricao["tamanho_descricao"] = (
        colunas_com_descricao["descricao_coluna"]
        .apply(lambda texto: len(texto.split()))
    )

    titulo("1. DESCRICOES DISPONIVEIS")

    print(
        colunas_com_descricao[
            [
                "camada",
                "nome_coluna",
                "descricao_coluna",
                "tamanho_descricao"
            ]
        ].to_string(index=False)
    )

    # 3. DESCRICOES CURTAS
    descricoes_curtas = colunas_com_descricao[
        colunas_com_descricao["tamanho_descricao"] < 4
    ].copy()

    titulo("2. DESCRICOES COM MENOS DE 4 PALAVRAS")

    if descricoes_curtas.empty:
        print("Nenhuma descricao encontrada.")
    else:
        print(
            descricoes_curtas[
                [
                    "nome_tabela",
                    "nome_coluna",
                    "descricao_coluna",
                    "tamanho_descricao"
                ]
            ].to_string(index=False)
        )

    # 4. DESCRICOES LONGAS
    descricoes_longas = colunas_com_descricao[
        colunas_com_descricao["tamanho_descricao"] > 5
    ].copy()

    titulo("3. DESCRICOES COM MAIS DE 5 PALAVRAS")

    if descricoes_longas.empty:
        print(
            "Nenhuma descricao com mais de "
            "5 palavras foi encontrada."
        )
    else:
        print(
            descricoes_longas[
                [
                    "nome_coluna",
                    "descricao_coluna",
                    "tamanho_descricao"
                ]
            ].to_string(index=False)
        )

    # 5. AMOSTRAS REPRODUZIVEIS
    titulo("4. AMOSTRA DAS DESCRICOES CURTAS")

    amostra_curtas = descricoes_curtas.sample(
        n=min(4, len(descricoes_curtas)),
        random_state=42
    )

    print(
        amostra_curtas[
            [
                "nome_coluna",
                "descricao_coluna"
            ]
        ].to_string(index=False)
    )

    titulo("5. AMOSTRA DAS DESCRICOES LONGAS")

    if not descricoes_longas.empty:
        amostra_longas = descricoes_longas.sample(
            n=min(4, len(descricoes_longas)),
            random_state=42
        )
        print(amostra_longas.to_string(index=False))
    else:
        print("Amostra vazia: nao ha descricoes longas.")

    # 6. INVESTIGAR PRODUTO_ID
    titulo("6. COMPARACAO - PRODUTO_ID")

    produtos = colunas_com_descricao[
        colunas_com_descricao["nome_coluna"] == "produto_id"
    ].copy()

    print(
        produtos[
            [
                "camada",
                "nome_tabela",
                "descricao_coluna",
                "tamanho_descricao"
            ]
        ].to_string(index=False)
    )

    # 7. COMPARAR TAMANHO E CONTEXTO
    titulo("7. INSPECAO DE QUALIDADE SEMANTICA")

    analise = df[
        [
            "camada",
            "database",
            "nome_tabela",
            "nome_coluna",
            "descricao_coluna"
        ]
    ].copy()

    analise["quantidade_palavras"] = (
        analise["descricao_coluna"]
        .fillna("")
        .apply(lambda texto: len(texto.split()))
    )

    analise["descricao_preenchida"] = (
        analise["descricao_coluna"].notna()
    )

    analise["revisao_sugerida"] = (
        analise["quantidade_palavras"]
        .apply(
            lambda quantidade:
                "Verificar ausencia"
                if quantidade == 0
                else "Revisar contexto"
                if quantidade < 4
                else "Validar com Data Owner"
        )
    )

    # Nao atribuir qualidade automaticamente.
    analise["qualidade_semantica_validada"] = False

    print(
        analise[
            [
                "camada",
                "nome_coluna",
                "quantidade_palavras",
                "revisao_sugerida"
            ]
        ].to_string(index=False)
    )

    # 8. SALVAR RELATORIOS
    titulo("8. SALVANDO RELATORIOS")

    caminhos = {
        "descricoes_curtas":
            RESULTADOS / "aula15_descricoes_curtas.csv",
        "descricoes_longas":
            RESULTADOS / "aula15_descricoes_longas.csv",
        "revisao_semantica":
            RESULTADOS / "aula15_revisao_semantica.csv",
    }

    descricoes_curtas.to_csv(
        caminhos["descricoes_curtas"],
        index=False,
        encoding="utf-8-sig"
    )

    descricoes_longas.to_csv(
        caminhos["descricoes_longas"],
        index=False,
        encoding="utf-8-sig"
    )

    analise.to_csv(
        caminhos["revisao_semantica"],
        index=False,
        encoding="utf-8-sig"
    )

    for nome, caminho in caminhos.items():
        print(f"{nome}: {caminho.name}")

    # 9. VALIDACOES
    titulo("9. TESTES")

    assert df.shape == (15, 9)
    assert len(colunas_com_descricao) == 8
    assert len(descricoes_curtas) == 3
    assert len(descricoes_longas) == 0
    assert len(produtos) == 2

    assert (
        analise["descricao_preenchida"].sum()
        == 8
    )

    assert not analise[
        "qualidade_semantica_validada"
    ].any()

    assert all(
        caminho.is_file()
        for caminho in caminhos.values()
    )

    titulo("RESULTADO FINAL")

    print("Registros analisados:", len(df))
    print("Descricoes preenchidas:", len(colunas_com_descricao))
    print("Descricoes curtas:", len(descricoes_curtas))
    print("Descricoes longas:", len(descricoes_longas))
    print("Descricoes ausentes:", df["descricao_coluna"].isna().sum())
    print("Relatorios CSV: 3")
    print("Avaliacao semantica requer validacao do Data Owner.")
    print("Todos os testes passaram.")
    print("Aula 15 executada com sucesso.")


if __name__ == "__main__":
    main()