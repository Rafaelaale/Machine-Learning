import json
from pathlib import Path

from classes.metadados import MetadadosTabela, MetadadosColuna

BASE = Path(__file__).resolve().parent
ARTEFATO = (
    BASE / "metadados"
    / "bz_data_science_previsoes_de_venda_diario.json"
)

def main():
    print("\n===== AULA 07 =====")
    print("CONVERTENDO COLUNAS EM OBJETOS")

    with ARTEFATO.open("r", encoding="utf-8") as arquivo:
        informacoes = json.load(arquivo)

    tabela = MetadadosTabela()
    tabela.load_from_artefato(informacoes)

    print("\nANTES:")
    print("Tabela:", tabela.nome)
    print("Quantidade:", len(tabela.colunas))
    print("Tipo:", type(tabela.colunas[0]).__name__)

    tabela.converte_colunas_em_objetos()

    print("\nDEPOIS:")
    print("Tipo:", type(tabela.colunas[0]).__name__)

    for coluna in tabela.colunas:
        print(coluna)

    assert len(tabela.colunas) == 5
    assert all(
        isinstance(coluna, MetadadosColuna)
        for coluna in tabela.colunas
    )
    assert tabela.colunas[0].nome == "data_referencia"
    assert tabela.colunas[0].descricao == "Data da previsão"

    tabela.converte_colunas_em_objetos()
    assert len(tabela.colunas) == 5

    print("\n===== RESULTADO FINAL =====")
    print("5 colunas convertidas em objetos.")
    print("Todos os testes passaram.")

if __name__ == "__main__":
    main()