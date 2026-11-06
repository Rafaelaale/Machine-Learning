import json
from pathlib import Path

from classes.metadados import MetadadosTabela


BASE_DIR = Path(__file__).resolve().parent

ARTEFATO = (
    BASE_DIR
    / "metadados"
    / "bz_data_science_previsoes_de_venda_diario.json"
)


def main():

    print("\n===== ALURA - AULA 05 =====")
    print("TRANSFERINDO METADADOS PARA OBJETOS")

    # VERIFICAR ARQUIVO
    if not ARTEFATO.exists():
        raise FileNotFoundError(
            f"Artefato nao encontrado: {ARTEFATO}"
        )

    # LER JSON
    with open(
        ARTEFATO,
        "r",
        encoding="utf-8"
    ) as file:
        info = json.load(file)

    print("\n===== LEITURA DO JSON =====")
    print("Arquivo:", ARTEFATO.name)
    print("Tipo da informacao:", type(info))

    # INSTANCIAR CLASSE
    m = MetadadosTabela()

    print("\n===== OBJETO ANTES =====")
    print(m)

    # TRANSFERIR INFORMACOES
    m.load_from_artefato(info)

    print("\n===== OBJETO APOS CARREGAMENTO =====")
    print(m)

    # EXIBIR ATRIBUTOS
    print("\n===== ATRIBUTOS EXTRAIDOS =====")
    print("Nome:", m.nome)
    print("Database:", m.database)
    print("Camada:", m.camada)
    print("Descricao:", m.descricao)
    print("Total de colunas:", len(m.colunas))

    print("\n===== COLUNAS =====")

    for coluna in m.colunas:
        print(
            f"Nome: {coluna.get('name')} | "
            f"Tipo: {coluna.get('datatype')}"
        )

    # TESTES
    assert isinstance(m, MetadadosTabela)

    assert m.nome == "previsoes_de_venda_diario"
    assert m.database == "bz_data_science"
    assert m.camada is None
    assert len(m.colunas) == 5

    print("\n===== RESULTADO =====")
    print("JSON carregado corretamente.")
    print("Metadados transferidos para o objeto.")
    print("Todos os testes passaram.")


if __name__ == "__main__":
    main()