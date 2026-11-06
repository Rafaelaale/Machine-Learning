import json
from pathlib import Path

import pandas as pd

from classes.metadados import (
    MetadadosTabela,
    MetadadosColuna,
)


BASE_DIR = Path(__file__).resolve().parent

ARTEFATO = (
    BASE_DIR
    / "artefatos"
    / "bronze"
    / "bz_data_science_previsoes_de_venda_diario.json"
)


def main():

    print("\n===== ALURA - AULA 09 =====")
    print("CRIANDO UM DATAFRAME COM METADADOS")

    # LER O ARTEFATO
    with ARTEFATO.open(
        "r",
        encoding="utf-8"
    ) as arquivo:
        informacoes = json.load(arquivo)

    # CRIAR OBJETO TABELA
    meta_tabela = MetadadosTabela()

    meta_tabela.load_from_artefato(
        informacoes
    )

    # CONVERTER AS COLUNAS EM OBJETOS
    meta_tabela.converte_colunas_em_objetos()

    print("\n===== OBJETO TABELA =====")
    print("Nome:", meta_tabela.nome)
    print("Database:", meta_tabela.database)
    print("Colunas:", len(meta_tabela.colunas))

    # CONVERTER PARA DATAFRAME
    dataframe = meta_tabela.converte_para_dataframe()

    print("\n===== DATAFRAME =====")
    print(dataframe.to_string(index=False))

    print("\n===== INFORMACOES =====")
    print("Tipo:", type(dataframe))
    print("Linhas:", len(dataframe))
    print("Colunas:", len(dataframe.columns))

    print("\n===== CAMPOS DO DATAFRAME =====")
    for coluna in dataframe.columns:
        print("-", coluna)

    # CALCULAR CAMADA SEPARADAMENTE
    # A integração automatica fica para a proxima aula.
    meta_tabela.calcula_camada()

    print("\n===== CAMADA IDENTIFICADA =====")
    print("Database:", meta_tabela.database)
    print("Prefixo:", meta_tabela.camada)

    # VALIDACOES
    assert isinstance(dataframe, pd.DataFrame)

    assert len(dataframe) == 5

    assert len(dataframe.columns) == 9

    assert (
        dataframe["nome_coluna"].iloc[0]
        == "data_referencia"
    )

    assert (
        dataframe["datatype_coluna"].iloc[0]
        == "date"
    )

    assert (
        dataframe["descricao_coluna"].iloc[0]
        == "Data da previsão"
    )

    assert meta_tabela.camada == "bz"

    assert all(
        isinstance(coluna, MetadadosColuna)
        for coluna in meta_tabela.colunas
    )

    print("\n===== RESULTADO FINAL =====")
    print("DataFrame criado com sucesso.")
    print("5 linhas e 9 colunas.")
    print("Metadados preservados.")
    print("Todos os testes passaram.")


if __name__ == "__main__":
    main()