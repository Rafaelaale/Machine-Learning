import os
import json

from pathlib import Path

from classes.metadados import (
    MetadadosTabela,
    MetadadosColuna,
)


BASE_DIR = Path(__file__).resolve().parent
PASTA_ARTEFATOS = BASE_DIR / "artefatos"


def listar_caminhos_artefatos():
    """
    Percorre as camadas e encontra arquivos JSON.
    """

    caminhos_todos_artefatos = []

    for camada in sorted(os.listdir(PASTA_ARTEFATOS)):

        pasta_camada = PASTA_ARTEFATOS / camada

        if not pasta_camada.is_dir():
            continue

        for nome_arquivo in sorted(os.listdir(pasta_camada)):

            caminho_do_artefato = pasta_camada / nome_arquivo

            if (
                caminho_do_artefato.is_file()
                and caminho_do_artefato.suffix.lower() == ".json"
            ):
                caminhos_todos_artefatos.append(
                    caminho_do_artefato
                )

    return caminhos_todos_artefatos


def extrair_informacoes_do_artefato_json(path: str):
    """
    Abre um arquivo JSON e retorna um dicionario.
    """

    path = Path(path)

    with path.open(
        mode="r",
        encoding="utf-8"
    ) as arquivo:

        info = json.load(arquivo)

    if not isinstance(info, dict):
        raise TypeError(
            f"O artefato deve conter um objeto JSON: {path}"
        )

    return info


def criar_objetos_tabela(caminhos_todos_artefatos):
    """
    Cria um objeto MetadadosTabela por artefato.
    """

    lista_objetos_tabela = []

    for artefato in caminhos_todos_artefatos:

        infos = extrair_informacoes_do_artefato_json(
            artefato
        )

        meta_tabela = MetadadosTabela()

        meta_tabela.load_from_artefato(infos)

        meta_tabela.converte_colunas_em_objetos()

        lista_objetos_tabela.append(
            meta_tabela
        )

    return lista_objetos_tabela


def main():

    print("\n===== ALURA - AULA 08 =====")
    print("CRIANDO OBJETOS PARA TODOS OS ARTEFATOS")

    print("\n===== CAMADAS =====")

    for camada in sorted(os.listdir(PASTA_ARTEFATOS)):
        if (PASTA_ARTEFATOS / camada).is_dir():
            print(camada)

    # LISTAR TODOS OS ARTEFATOS
    caminhos_todos_artefatos = listar_caminhos_artefatos()

    print("\n===== CAMINHOS DOS ARTEFATOS =====")

    for caminho in caminhos_todos_artefatos:
        print(caminho.relative_to(BASE_DIR))

    # CRIAR OBJETOS
    lista_objetos_tabela = criar_objetos_tabela(
        caminhos_todos_artefatos
    )

    print("\n===== OBJETOS TABELA =====")

    total_colunas = 0

    for tabela in lista_objetos_tabela:

        print("\nTabela:", tabela.nome)
        print("Database:", tabela.database)
        print("Descricao:", tabela.descricao)
        print("Total de colunas:", len(tabela.colunas))

        total_colunas += len(tabela.colunas)

        for coluna in tabela.colunas:
            print(
                f"  - {coluna.nome}: "
                f"{coluna.datatype}"
            )

    # VALIDACOES
    assert len(caminhos_todos_artefatos) == 3

    assert len(lista_objetos_tabela) == 3

    assert total_colunas == 15

    assert all(
        isinstance(tabela, MetadadosTabela)
        for tabela in lista_objetos_tabela
    )

    assert all(
        isinstance(coluna, MetadadosColuna)
        for tabela in lista_objetos_tabela
        for coluna in tabela.colunas
    )

    assert all(
        len(tabela.colunas) == 5
        for tabela in lista_objetos_tabela
    )

    # VERIFICAR QUE AS TRES TABELAS FORAM LIDAS
    bancos = {
        tabela.database
        for tabela in lista_objetos_tabela
    }

    assert bancos == {
        "bz_data_science",
        "sl_data_science",
        "gd_novo_produto"
    }

    print("\n===== RESUMO FINAL =====")
    print("Arquivos JSON:", len(caminhos_todos_artefatos))
    print("Objetos tabela:", len(lista_objetos_tabela))
    print("Objetos coluna:", total_colunas)
    print("Todos os testes passaram.")
    print("Aula 08 executada com sucesso.")


if __name__ == "__main__":
    main()