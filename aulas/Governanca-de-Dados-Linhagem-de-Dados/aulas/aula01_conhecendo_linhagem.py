from pathlib import Path
import csv
import json


BASE = Path(__file__).resolve().parent.parent
RESULTADOS = BASE / "resultados"
RESULTADOS.mkdir(parents=True, exist_ok=True)


def titulo(texto):
    print("\n" + "=" * 65)
    print(texto)
    print("=" * 65)


# DADOS FICTICIOS PARA FINS DIDATICOS
precos_de_imoveis_por_m2 = [
    {"cidade": "Salvador", "preco_m2": 6500.00},
    {"cidade": "Recife", "preco_m2": 7200.00},
]

compras_e_vendas_de_imoveis = [
    {"cidade": "Salvador", "compras": 125, "vendas": 110},
    {"cidade": "Recife", "compras": 90, "vendas": 105},
]

analises_anteriores = [
    {"cidade": "Salvador", "classificacao_anterior": "favoravel"},
    {"cidade": "Recife", "classificacao_anterior": "neutra"},
]


def transformar_dados(precos, transacoes, analises):
    transacoes_por_cidade = {
        item["cidade"]: item for item in transacoes
    }

    analises_por_cidade = {
        item["cidade"]: item for item in analises
    }

    resultado = []

    for preco in precos:
        cidade = preco["cidade"]

        if (
            cidade not in transacoes_por_cidade
            or cidade not in analises_por_cidade
        ):
            raise ValueError(
                f"Origem incompleta para a cidade {cidade}"
            )

        transacao = transacoes_por_cidade[cidade]
        analise = analises_por_cidade[cidade]

        saldo_transacoes = (
            transacao["compras"] - transacao["vendas"]
        )

        # Regra ficticia, apenas para demonstrar
        # transformacoes e rastreabilidade.
        classificacao_didatica = (
            "favoravel"
            if saldo_transacoes > 0
            and analise["classificacao_anterior"] == "favoravel"
            else "revisar"
        )

        resultado.append({
            "cidade": cidade,
            "preco_m2": preco["preco_m2"],
            "compras": transacao["compras"],
            "vendas": transacao["vendas"],
            "saldo_transacoes": saldo_transacoes,
            "classificacao_anterior": (
                analise["classificacao_anterior"]
            ),
            "classificacao_didatica": classificacao_didatica,
        })

    return resultado


def main():
    titulo("ALURA - AULA 01")
    print("CONHECENDO A LINHAGEM DE DADOS")

    origens = [
        "precos_de_imoveis_por_m2",
        "compras_e_vendas_de_imoveis",
        "analises_anteriores",
    ]

    titulo("1. ORIGENS IDENTIFICADAS")

    for numero, origem in enumerate(origens, start=1):
        print(f"Origem {numero}: {origem}")

    titulo("2. TRANSFORMACOES")

    print("Relacionamento por cidade")
    print("Juncao de informacoes das tres origens")
    print("Calculo do saldo de transacoes")
    print("Classificacao ficticia de demonstracao")

    destino = transformar_dados(
        precos_de_imoveis_por_m2,
        compras_e_vendas_de_imoveis,
        analises_anteriores,
    )

    titulo("3. DESTINO DOS DADOS")

    for registro in destino:
        print(registro)

    titulo("4. DOCUMENTANDO A LINHAGEM")

    linhagem = {
        "aula": 1,
        "tema": "Conhecendo a linhagem de dados",
        "origens": origens,
        "transformacoes": [
            "Relacionamento pela cidade",
            "Juncao das informacoes",
            "Calculo compras menos vendas",
            "Classificacao didatica ficticia",
        ],
        "destino": "avaliacao_didatica_de_ativos.csv",
        "observacao": (
            "Dados e classificacoes ficticios. "
            "Nao representam orientacao de investimento."
        ),
    }

    arquivo_linhagem = RESULTADOS / "aula01_linhagem.json"
    arquivo_destino = (
        RESULTADOS / "aula01_avaliacao_didatica_de_ativos.csv"
    )

    arquivo_linhagem.write_text(
        json.dumps(linhagem, indent=4, ensure_ascii=False),
        encoding="utf-8",
    )

    with arquivo_destino.open(
        "w", newline="", encoding="utf-8-sig"
    ) as arquivo_csv:
        escritor = csv.DictWriter(
            arquivo_csv,
            fieldnames=list(destino[0].keys()),
        )
        escritor.writeheader()
        escritor.writerows(destino)

    titulo("5. VALIDACOES")

    assert len(origens) == 3
    assert len(destino) == 2
    assert destino[0]["cidade"] == "Salvador"
    assert destino[0]["saldo_transacoes"] == 15
    assert destino[1]["saldo_transacoes"] == -15
    assert arquivo_linhagem.is_file()
    assert arquivo_destino.is_file()

    dados_salvos = json.loads(
        arquivo_linhagem.read_text(encoding="utf-8")
    )
    assert dados_salvos["origens"] == origens

    titulo("RESULTADO FINAL")

    print("Origens identificadas: 3")
    print("Transformacoes documentadas: 4")
    print("Registros no destino: 2")
    print("Arquivos gerados: 2")
    print("Todos os testes passaram.")
    print("Aula 01 executada com sucesso.")


if __name__ == "__main__":
    main()