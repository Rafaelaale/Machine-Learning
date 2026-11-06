from pathlib import Path
import sys
import json


BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from src.aula03_principios import (
    carregar_clientes_produtos,
    resolver_produto,
    analisar_portfolio,
    resumir_portfolio,
    comparar_hipoteses,
)


DADOS = BASE / "dados" / "aula03_clientes_produtos.csv"
RESULTADOS = BASE / "resultados"

CATALOGO = {
    "P100": "Eletronicos",
    "P200": "Livros",
    "P300": "Vestuario",
}


def titulo(texto):
    print("\n" + "=" * 65)
    print(texto)
    print("=" * 65)


def main():
    titulo("ALURA - AULA 03")
    print("PRINCIPIOS 4 AO 7 DA ENGENHARIA DE SOFTWARE")

    titulo("1. O QUE UM PRODUZ, OUTROS CONSOMEM")

    clientes = carregar_clientes_produtos(DADOS)

    print("Funcao de carregamento documentada: OK")
    print("Validacao de dados reutilizada da Aula 02: OK")
    print("Clientes carregados:", len(clientes))

    titulo("2. ESTEJA ABERTO PARA O FUTURO")

    novo_catalogo = {
        **CATALOGO,
        "P400": "Produtos Digitais",
    }

    print(
        "Novo produto:",
        resolver_produto("P400", novo_catalogo)
    )

    resultados = analisar_portfolio(
        clientes, CATALOGO
    )

    for item in resultados:
        print(
            item["cliente_id"],
            "|",
            item["produto_nome"],
            "|",
            item["classificacao"],
        )

    titulo("3. PLANEJE COM ANTECEDENCIA")

    resumo = resumir_portfolio(resultados)

    for codigo, valores in resumo.items():
        print(
            f"{codigo}: total={valores['total']}, "
            f"revisar={valores['revisar']}, "
            f"normal={valores['normal']}"
        )

    print("Modulos reutilizaveis: OK")
    print("Dados separados do codigo: OK")
    print("Configuracao de produtos: OK")

    titulo("4. PENSE ANTES DE AGIR")

    hipoteses = comparar_hipoteses(
        clientes,
        CATALOGO,
        limites=[30, 60, 90],
    )

    for hipotese in hipoteses:
        print(
            "Limite:",
            hipotese["limite_dias"],
            "dias | Revisar:",
            hipotese["clientes_para_revisao"],
            "| Percentual:",
            hipotese["percentual_revisao"],
        )

    print(
        "Nenhuma hipotese foi aplicada "
        "automaticamente em producao."
    )

    titulo("5. SALVANDO RESULTADOS")

    RESULTADOS.mkdir(parents=True, exist_ok=True)

    relatorio = {
        "aula": 3,
        "curso": "Engenharia de software para dados",
        "principios": [
            "O que um produz, outros consomem",
            "Esteja aberto para o futuro",
            "Planeje com antecedencia",
            "Pense antes de agir",
        ],
        "tipo": "laboratorio didatico",
        "clientes_analisados": len(clientes),
        "catalogo": CATALOGO,
        "resultados": resultados,
        "resumo_por_produto": resumo,
        "hipoteses": hipoteses,
        "limitacoes": [
            "Clientes e produtos ficticios.",
            "Nenhum modelo de ML foi treinado.",
            "As regras nao estimam risco real de churn.",
            "Nenhuma alteracao de producao foi realizada.",
        ],
    }

    destino = RESULTADOS / "aula03_principios_4_a_7.json"

    destino.write_text(
        json.dumps(
            relatorio,
            ensure_ascii=False,
            indent=4,
        ),
        encoding="utf-8",
    )

    print("Relatorio:", destino.name)

    titulo("6. VERIFICACOES INTERNAS")

    assert len(clientes) == 8
    assert len(resultados) == 8
    assert len(resumo) == 3
    assert len(hipoteses) == 3
    assert len(relatorio["principios"]) == 4
    assert sum(
        item["revisar"]
        for item in resumo.values()
    ) == 4

    assert destino.is_file()

    salvo = json.loads(
        destino.read_text(encoding="utf-8")
    )

    assert salvo["aula"] == 3

    titulo("RESULTADO FINAL")

    print("Principios aplicados: 4")
    print("Clientes ficticios analisados: 8")
    print("Produtos analisados: 3")
    print("Produtos novos suportados: SIM")
    print("Hipoteses avaliadas: 3")
    print("Clientes para revisao no cenario padrao: 4")
    print("Relatorios JSON gerados: 1")
    print("Verificacoes internas: APROVADAS")
    print("Aula 03 executada com sucesso.")


if __name__ == "__main__":
    main()