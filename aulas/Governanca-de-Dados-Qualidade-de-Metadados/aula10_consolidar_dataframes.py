import json
from pathlib import Path

import pandas as pd

from classes.metadados import (
    MetadadosTabela,
    MetadadosColuna,
)


BASE_DIR = Path(__file__).resolve().parent
PASTA_ARTEFATOS = BASE_DIR / "artefatos"
PASTA_RESULTADOS = BASE_DIR / "resultados"


def extrair_informacoes_do_artefato_json(path: Path):
    """
    Le um arquivo JSON usando UTF-8.
    """

    with Path(path).open(
        mode="r",
        encoding="utf-8"
    ) as arquivo:
        informacoes = json.load(arquivo)

    if not isinstance(informacoes, dict):
        raise TypeError(
            f"Artefato invalido: {path}"
        )

    return informacoes


def listar_artefatos():
    """
    Localiza arquivos JSON nas camadas de dados.
    """

    caminhos = []

    for camada in ("bronze", "silver", "gold"):

        pasta = PASTA_ARTEFATOS / camada

        if not pasta.is_dir():
            continue

        for arquivo in sorted(pasta.glob("*.json")):
            caminhos.append(arquivo)

    return caminhos


def criar_objetos_tabela(caminhos):
    """
    Cria os objetos tabela, calcula suas camadas
    e converte todas as colunas em objetos.
    """

    lista_objetos_tabela = []

    for artefato in caminhos:

        informacoes = (
            extrair_informacoes_do_artefato_json(
                artefato
            )
        )

        meta_tabela = MetadadosTabela()

        meta_tabela.load_from_artefato(
            informacoes
        )

        # CALCULAR A CAMADA ANTES DO DATAFRAME
        meta_tabela.calcula_camada()

        # CONVERTER COLUNAS EM OBJETOS
        meta_tabela.converte_colunas_em_objetos()

        lista_objetos_tabela.append(
            meta_tabela
        )

    return lista_objetos_tabela


def consolidar_dataframes(lista_objetos_tabela):
    """
    Converte cada tabela em DataFrame
    e concatena todas as tabelas.
    """

    todos_dfs = []

    for objeto_tabela in lista_objetos_tabela:

        df_ = objeto_tabela.converte_para_dataframe()

        todos_dfs.append(df_)

    if not todos_dfs:
        raise ValueError(
            "Nenhum DataFrame foi gerado."
        )

    df_concatenado = pd.concat(
        todos_dfs,
        ignore_index=True
    )

    return df_concatenado


def main():

    print("\n===== ALURA - AULA 10 =====")
    print("CONSOLIDANDO METADADOS COM PANDAS")

    # LOCALIZAR ARTEFATOS
    caminhos = listar_artefatos()

    print("\n===== ARTEFATOS ENCONTRADOS =====")

    for caminho in caminhos:
        print(caminho.relative_to(BASE_DIR))

    # CRIAR OBJETOS
    lista_objetos_tabela = criar_objetos_tabela(
        caminhos
    )

    print("\n===== OBJETOS TABELA =====")

    for tabela in lista_objetos_tabela:

        print(
            f"Tabela: {tabela.nome} | "
            f"Camada: {tabela.camada} | "
            f"Colunas: {len(tabela.colunas)}"
        )

    # CONSOLIDAR DATAFRAMES
    df_concatenado = consolidar_dataframes(
        lista_objetos_tabela
    )

    print("\n===== DATAFRAME CONSOLIDADO =====")

    print(
        df_concatenado.to_string(
            index=False
        )
    )

    print("\n===== PRIMEIRAS 5 LINHAS =====")

    print(
        df_concatenado.head().to_string(
            index=False
        )
    )

    print("\n===== ULTIMAS 5 LINHAS =====")

    print(
        df_concatenado.tail().to_string(
            index=False
        )
    )

    print("\n===== ULTIMAS 7 LINHAS =====")

    print(
        df_concatenado.tail(7).to_string(
            index=False
        )
    )

    # RESUMO POR CAMADA
    print("\n===== RESUMO POR CAMADA =====")

    resumo = (
        df_concatenado.groupby("camada")
        .agg(
            quantidade_colunas=(
                "nome_coluna",
                "count"
            ),
            quantidade_tabelas=(
                "nome_tabela",
                "nunique"
            )
        )
        .reset_index()
    )

    print(resumo.to_string(index=False))

    # VALIDAÇÕES
    assert len(lista_objetos_tabela) == 3

    assert len(df_concatenado) == 15

    assert len(df_concatenado.columns) == 9

    assert set(df_concatenado["camada"]) == {
        "bz",
        "sl",
        "gd"
    }

    assert df_concatenado["camada"].notna().all()

    assert df_concatenado["nome_coluna"].notna().all()

    assert all(
        isinstance(tabela, MetadadosTabela)
        for tabela in lista_objetos_tabela
    )

    assert all(
        isinstance(coluna, MetadadosColuna)
        for tabela in lista_objetos_tabela
        for coluna in tabela.colunas
    )

    # SALVAR RESULTADOS
    PASTA_RESULTADOS.mkdir(
        parents=True,
        exist_ok=True
    )

    destino = (
        PASTA_RESULTADOS
        / "metadados_consolidados.csv"
    )

    df_concatenado.to_csv(
        destino,
        index=False,
        encoding="utf-8-sig"
    )

    # VERIFICAR ARQUIVO SALVO
    df_verificacao = pd.read_csv(
        destino,
        encoding="utf-8-sig"
    )

    assert df_verificacao.shape == (15, 9)

    print("\n===== RESULTADO FINAL =====")
    print("Arquivos processados:", len(caminhos))
    print("Objetos tabela:", len(lista_objetos_tabela))
    print("Linhas:", len(df_concatenado))
    print("Colunas:", len(df_concatenado.columns))
    print("Camadas:", sorted(df_concatenado["camada"].unique()))
    print("CSV salvo:", destino)
    print("Todos os testes passaram.")
    print("Aula 10 executada com sucesso.")


if __name__ == "__main__":
    main()