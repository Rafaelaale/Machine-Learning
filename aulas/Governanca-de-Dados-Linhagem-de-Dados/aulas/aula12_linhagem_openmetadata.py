from pathlib import Path
from collections import deque
import csv
import json
import sqlite3


BASE = Path(__file__).resolve().parent.parent
BANCO = BASE / "dados" / "aula04_especializacao.sqlite3"
FONTE = BASE / "resultados" / "aula06_rastreabilidade.json"
RESULTADOS = BASE / "resultados"

ALVO = "spec_clientes_ativos"
ORIGEM_PRINCIPAL = "sor_assinantes"

# Produtos adicionais apenas para demonstrar downstream.
PRODUTOS_DIDATICOS = [
    {
        "origem": ALVO,
        "destino": "relatorio_regulatorio_ficticio",
        "operacao": "geracao de relatorio simulado",
        "tipo": "relatorio",
        "simulado": True,
    },
    {
        "origem": ALVO,
        "destino": "dashboard_assinantes_ficticio",
        "operacao": "visualizacao de assinantes",
        "tipo": "dashboard",
        "simulado": True,
    },
    {
        "origem": ALVO,
        "destino": "modelo_ml_retencao_ficticio",
        "operacao": "consumo analitico ilustrativo",
        "tipo": "modelo_ml",
        "simulado": True,
    },
]


def titulo(texto):
    print("\n" + "=" * 65)
    print(texto)
    print("=" * 65)


def carregar_json(caminho):
    with caminho.open(encoding="utf-8") as arquivo:
        return json.load(arquivo)


def obter_linhagem():
    documento = carregar_json(FONTE)

    assert documento["aula"] == 6

    relacoes = []

    for item in documento["dependencias"]:
        relacoes.append({
            "origem": item["origem"],
            "destino": item["destino"],
            "operacao": item.get(
                "operacao", "transformacao documentada"
            ),
            "tipo": "tabela",
            "simulado": False,
        })

    return relacoes + PRODUTOS_DIDATICOS


def percorrer_linhagem(relacoes, inicio, direcao):
    """
    Busca em largura.

    upstream: segue dos destinos para as origens.
    downstream: segue das origens para os destinos.
    """

    if direcao not in ("upstream", "downstream"):
        raise ValueError("Direcao invalida")

    fila = deque([(inicio, 0)])
    visitados = {inicio}
    encontrados = []

    while fila:
        atual, distancia = fila.popleft()

        for item in relacoes:
            if direcao == "upstream":
                if item["destino"] != atual:
                    continue
                proximo = item["origem"]
            else:
                if item["origem"] != atual:
                    continue
                proximo = item["destino"]

            if proximo not in visitados:
                visitados.add(proximo)
                encontrados.append({
                    "ativo": proximo,
                    "distancia": distancia + 1,
                })
                fila.append((proximo, distancia + 1))

    return encontrados


def consultar_esquemas():
    """Consulta as colunas sem modificar o banco."""

    uri = BANCO.resolve().as_uri() + "?mode=ro"
    esquemas = {}

    nomes = [
        "sor_assinantes",
        "sot_clientes_tratados",
        "spec_clientes_ativos",
        "spec_ativos_mais_6_meses",
        "spec_clientes_sp",
    ]

    with sqlite3.connect(uri, uri=True) as conexao:
        for nome in nomes:
            if not conexao.execute(
                "SELECT 1 FROM sqlite_master "
                "WHERE name = ? AND type IN ('table', 'view')",
                (nome,),
            ).fetchone():
                raise ValueError(
                    f"Ativo ausente no banco: {nome}"
                )

            campos = conexao.execute(
                f"PRAGMA table_info({nome})"
            ).fetchall()

            esquemas[nome] = [
                campo[1] for campo in campos
            ]

    return esquemas


def criar_linhagem_colunas(relacoes, esquemas):
    """
    Demonstra correspondencias de nomes entre colunas.

    A coincidencia de nomes NAO prova por si so a
    transformacao SQL. Por isso, as ligacoes sao
    identificadas como candidatas a validacao.
    """

    registros = []

    for relacao in relacoes:
        origem = relacao["origem"]
        destino = relacao["destino"]

        if origem not in esquemas or destino not in esquemas:
            continue

        campos_origem = set(esquemas[origem])
        campos_destino = set(esquemas[destino])

        for coluna in sorted(
            campos_origem.intersection(campos_destino)
        ):
            registros.append({
                "tabela_origem": origem,
                "coluna_origem": coluna,
                "tabela_destino": destino,
                "coluna_destino": coluna,
                "metodo": "correspondencia_nominal",
                "validacao_sql": "PENDENTE",
            })

    return registros


def salvar_csv(caminho, registros, campos):
    with caminho.open(
        "w", newline="", encoding="utf-8-sig"
    ) as arquivo:
        escritor = csv.DictWriter(
            arquivo, fieldnames=campos
        )
        escritor.writeheader()
        escritor.writerows(registros)


def main():
    titulo("ALURA - AULA 12")
    print("LINHAGEM DE DADOS NA OPENMETADATA")

    titulo("1. CARREGANDO RELACOES DA AULA 06")

    relacoes = obter_linhagem()

    for item in relacoes:
        marca = (
            " [PRODUTO FICTICIO]"
            if item["simulado"] else ""
        )

        print(
            f"{item['origem']} -> {item['destino']}"
            f"{marca}"
        )

    titulo("2. UPSTREAM - ORIGENS DA BASE")

    origens = percorrer_linhagem(
        relacoes, ALVO, "upstream"
    )

    print("Ativo analisado:", ALVO)

    for item in origens:
        print(
            f"Origem: {item['ativo']} | "
            f"distancia: {item['distancia']}"
        )

    titulo("3. DOWNSTREAM - BASES DEPENDENTES")

    destinos = percorrer_linhagem(
        relacoes, ALVO, "downstream"
    )

    for item in destinos:
        print(
            f"Destino: {item['ativo']} | "
            f"distancia: {item['distancia']}"
        )

    titulo("4. LINHAGEM POR COLUNA")

    esquemas = consultar_esquemas()

    for tabela, colunas in esquemas.items():
        print(
            f"{tabela}: {len(colunas)} colunas"
        )

    colunas_linhagem = criar_linhagem_colunas(
        relacoes, esquemas
    )

    for item in colunas_linhagem:
        print(
            f"{item['tabela_origem']}."
            f"{item['coluna_origem']} -> "
            f"{item['tabela_destino']}."
            f"{item['coluna_destino']} "
            f"[{item['validacao_sql']}]"
        )

    print(
        "\nIMPORTANTE: correspondencias nominais "
        "devem ser verificadas no SQL para "
        "confirmar a linhagem por coluna."
    )

    titulo("5. ANALISE DE IMPACTO")

    impacto = percorrer_linhagem(
        relacoes, ORIGEM_PRINCIPAL, "downstream"
    )

    print("Falha hipotetica em:", ORIGEM_PRINCIPAL)

    for item in impacto:
        print(
            f"Pode afetar: {item['ativo']} "
            f"(nivel {item['distancia']})"
        )

    titulo("6. SALVANDO RESULTADOS")

    RESULTADOS.mkdir(parents=True, exist_ok=True)

    caminho_json = (
        RESULTADOS / "aula12_linhagem_openmetadata.json"
    )
    caminho_tabelas = (
        RESULTADOS / "aula12_linhagem_tabelas.csv"
    )
    caminho_colunas = (
        RESULTADOS / "aula12_linhagem_colunas.csv"
    )
    caminho_impacto = (
        RESULTADOS / "aula12_analise_impacto.csv"
    )

    salvar_csv(
        caminho_tabelas,
        relacoes,
        [
            "origem",
            "destino",
            "operacao",
            "tipo",
            "simulado",
        ],
    )

    salvar_csv(
        caminho_colunas,
        colunas_linhagem,
        [
            "tabela_origem",
            "coluna_origem",
            "tabela_destino",
            "coluna_destino",
            "metodo",
            "validacao_sql",
        ],
    )

    salvar_csv(
        caminho_impacto,
        impacto,
        ["ativo", "distancia"],
    )

    documento = {
        "aula": 12,
        "tema": "Linhagem de dados na OpenMetadata",
        "tipo": "laboratorio local didatico",
        "ativo_analisado": ALVO,
        "upstream": origens,
        "downstream": destinos,
        "linhagem_tabelas": relacoes,
        "esquemas_sqlite": esquemas,
        "linhagem_colunas_candidata": colunas_linhagem,
        "analise_impacto": impacto,
        "observacoes": [
            "Nao houve conexao com OpenMetadata.",
            "Produtos regulatorios, de BI e ML "
            "foram acrescentados como exemplos ficticios.",
            "O banco SQLite original nao foi modificado.",
            "Dependencias por coluna foram inferidas "
            "por igualdade de nomes e requerem "
            "confirmacao das transformacoes SQL.",
            "Dependencia nao significa impacto "
            "comprovado em um incidente real.",
        ],
    }

    caminho_json.write_text(
        json.dumps(
            documento,
            indent=4,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    for caminho in (
        caminho_json,
        caminho_tabelas,
        caminho_colunas,
        caminho_impacto,
    ):
        print("Arquivo:", caminho.name)

    titulo("7. TESTES AUTOMATIZADOS")

    assert len(relacoes) == 7
    assert len(origens) == 2
    assert len(destinos) == 5
    assert len(impacto) == 7

    assert {
        item["ativo"] for item in origens
    } == {
        "sor_assinantes",
        "sot_clientes_tratados",
    }

    assert {
        item["ativo"] for item in destinos
    } == {
        "spec_ativos_mais_6_meses",
        "spec_clientes_sp",
        "relatorio_regulatorio_ficticio",
        "dashboard_assinantes_ficticio",
        "modelo_ml_retencao_ficticio",
    }

    assert len(esquemas) == 5
    assert len(colunas_linhagem) > 0

    assert all(
        item["validacao_sql"] == "PENDENTE"
        for item in colunas_linhagem
    )

    assert all(
        caminho.is_file()
        for caminho in (
            caminho_json,
            caminho_tabelas,
            caminho_colunas,
            caminho_impacto,
        )
    )

    salvo = json.loads(
        caminho_json.read_text(encoding="utf-8")
    )

    assert salvo["aula"] == 12
    assert len(salvo["upstream"]) == 2
    assert len(salvo["downstream"]) == 5

    titulo("RESULTADO FINAL")

    print("Ativo principal:", ALVO)
    print("Origens upstream:", len(origens))
    print("Destinos downstream:", len(destinos))
    print("Relacoes entre ativos:", len(relacoes))
    print(
        "Correspondencias de colunas:",
        len(colunas_linhagem)
    )
    print(
        "Ativos em potencial impacto:",
        len(impacto)
    )
    print("Relatorios gerados: 4")
    print("Banco original preservado.")
    print("Todos os testes passaram.")
    print("Aula 12 executada com sucesso.")


if __name__ == "__main__":
    main()