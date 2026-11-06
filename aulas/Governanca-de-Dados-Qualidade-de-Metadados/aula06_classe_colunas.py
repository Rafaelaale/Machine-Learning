import json
from pathlib import Path

from classes.metadados import (
    MetadadosTabela,
    MetadadosColuna
)

BASE_DIR = Path(__file__).resolve().parent

ARTEFATO = (
    BASE_DIR
    / "metadados"
    / "bz_data_science_previsoes_de_venda_diario.json"
)


def main():

    print("\n===== ALURA - AULA 06 =====")
    print("CRIANDO A CLASSE DE COLUNAS")

    # LER JSON COM UTF-8
    with open(
        ARTEFATO,
        "r",
        encoding="utf-8"
    ) as file:
        info = json.load(file)

    # CRIAR OBJETO TABELA
    meta_tabela = MetadadosTabela()

    meta_tabela.load_from_artefato(info)

    print("\n===== TABELA =====")
    print("Nome:", meta_tabela.nome)
    print("Database:", meta_tabela.database)
    print("Total de colunas:", len(meta_tabela.colunas))

    # CRIAR OBJETO COLUNA
    meta_coluna = MetadadosColuna()

    print("\n===== COLUNA ANTES =====")
    print(meta_coluna)

    # SELECIONAR PRIMEIRA COLUNA
    primeira_coluna = meta_tabela.colunas[0]

    print("\nDICIONARIO ORIGINAL:")
    print(primeira_coluna)

    # TRANSFERIR DADOS PARA OBJETO
    meta_coluna.load_from_tabela(
        primeira_coluna
    )

    print("\n===== COLUNA APOS CARREGAMENTO =====")
    print(meta_coluna)

    print("\n===== ATRIBUTOS =====")
    print("Nome:", meta_coluna.nome)
    print("Datatype:", meta_coluna.datatype)
    print("Descricao:", meta_coluna.descricao)
    print("Privacidade:", meta_coluna.privacidade)
    print("Confidencialidade:", meta_coluna.confidencialidade)

    # TESTES
    assert isinstance(meta_coluna, MetadadosColuna)
    assert meta_coluna.nome == "data_referencia"
    assert meta_coluna.datatype == "date"
    assert meta_coluna.descricao == "Data da previsão"
    assert meta_coluna.privacidade == "dado impessoal"
    assert meta_coluna.confidencialidade is None

    print("\n===== RESULTADO =====")
    print("Objeto MetadadosColuna criado.")
    print("Informacoes do JSON transferidas.")
    print("Codificacao UTF-8 validada.")
    print("Todos os testes passaram.")


if __name__ == "__main__":
    main()