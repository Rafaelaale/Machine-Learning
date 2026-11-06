from pathlib import Path
import csv
import json


BASE = Path(__file__).resolve().parent.parent
POLITICA = BASE / "metadados" / "aula10_politica_linhagem.json"
RESULTADOS = BASE / "resultados"


def titulo(texto):
    print("\n" + "=" * 65)
    print(texto)
    print("=" * 65)


def carregar_politica():
    with POLITICA.open(encoding="utf-8") as arquivo:
        return json.load(arquivo)


def catalogo_didatico():
    """
    Inventario de exemplo baseado nos ativos
    trabalhados nas aulas anteriores.

    O nivel documentado aqui representa
    a demonstracao do laboratorio, nao uma
    auditoria de metadados corporativos.
    """
    return [
        {
            "ativo": "sor_assinantes",
            "camada": "SOR",
            "origens": [],
            "nivel_documentado": "nenhum",
            "regulatorio": False,
        },
        {
            "ativo": "sot_clientes_tratados",
            "camada": "SOT",
            "origens": ["sor_assinantes"],
            "nivel_documentado": "tabela",
            "regulatorio": False,
        },
        {
            "ativo": "spec_clientes_ativos",
            "camada": "SPEC",
            "origens": ["sot_clientes_tratados"],
            "nivel_documentado": "tabela",
            "regulatorio": False,
        },
        {
            "ativo": "spec_ativos_mais_6_meses",
            "camada": "SPEC",
            "origens": ["spec_clientes_ativos"],
            "nivel_documentado": "tabela",
            "regulatorio": False,
        },
        {
            "ativo": "spec_clientes_sp",
            "camada": "SPEC",
            "origens": ["spec_ativos_mais_6_meses"],
            "nivel_documentado": "tabela",
            "regulatorio": False,
        },
        {
            "ativo": "relatorio_regulatorio_ficticio",
            "camada": "SPEC",
            "origens": ["spec_clientes_ativos"],
            "nivel_documentado": "tabela",
            "regulatorio": True,
        },
    ]


def avaliar_ativo(ativo, politica):
    camada = ativo["camada"]

    if camada not in politica["niveis"]:
        raise ValueError(f"Camada desconhecida: {camada}")

    if ativo["regulatorio"]:
        exigido = politica["nivel_para_processos_regulatorios"]
    elif camada == "SOR":
        exigido = "dispensado"
    else:
        exigido = politica["niveis"][camada]

    documentado = ativo["nivel_documentado"]

    if exigido == "dispensado":
        situacao = "DISPENSADO_NESTA_POLITICA"
    elif not ativo["origens"]:
        situacao = "PENDENTE_ORIGEM"
    elif exigido == "coluna" and documentado != "coluna":
        situacao = "PENDENTE_LINHAGEM_COLUNA"
    elif documentado in ("tabela", "coluna"):
        situacao = "ATENDE_POLITICA_DIDATICA"
    else:
        situacao = "PENDENTE_DOCUMENTACAO"

    return {
        "ativo": ativo["ativo"],
        "camada": camada,
        "regulatorio": ativo["regulatorio"],
        "origens": ",".join(ativo["origens"]),
        "nivel_exigido": exigido,
        "nivel_documentado": documentado,
        "situacao": situacao,
    }


def salvar_csv(caminho, registros):
    campos = [
        "ativo",
        "camada",
        "regulatorio",
        "origens",
        "nivel_exigido",
        "nivel_documentado",
        "situacao",
    ]

    with caminho.open(
        "w", newline="", encoding="utf-8-sig"
    ) as arquivo:
        escritor = csv.DictWriter(
            arquivo, fieldnames=campos
        )
        escritor.writeheader()
        escritor.writerows(registros)


def main():
    titulo("ALURA - AULA 10")
    print("COMO IMPLEMENTAR A LINHAGEM DE DADOS")

    titulo("1. CARREGANDO A POLITICA")

    politica = carregar_politica()

    print("Politica:", politica["nome"])
    print("Versao:", politica["versao"])
    print("Status:", politica["status"])
    print("Objetivo:", politica["objetivo"])

    titulo("2. RESPONSABILIDADES E CAPACITACAO")

    print(
        "Equipe sugerida:",
        politica["responsavel_sugerido"]
    )
    print(
        "Responsavel formal confirmado:",
        politica["responsavel_formal_confirmado"]
    )
    print(
        "Capacitacao necessaria:",
        politica["capacitacao_necessaria"]
    )

    titulo("3. NIVEIS EXIGIDOS")

    for camada, nivel in politica["niveis"].items():
        print(f"{camada}: {nivel}")

    print(
        "Processos regulatorios:",
        politica["nivel_para_processos_regulatorios"]
    )

    titulo("4. AVALIANDO ATIVOS")

    ativos = catalogo_didatico()

    resultados = [
        avaliar_ativo(ativo, politica)
        for ativo in ativos
    ]

    for item in resultados:
        print(
            f"{item['ativo']} | "
            f"exigido={item['nivel_exigido']} | "
            f"documentado={item['nivel_documentado']} | "
            f"{item['situacao']}"
        )

    titulo("5. IDENTIFICANDO PENDENCIAS")

    pendentes = [
        item for item in resultados
        if item["situacao"].startswith("PENDENTE")
    ]

    for item in pendentes:
        print("Ativo:", item["ativo"])
        print("Pendencia:", item["situacao"])
        print("Acao: detalhar as dependencias por coluna.")

    titulo("6. GERANDO RELATORIOS")

    RESULTADOS.mkdir(parents=True, exist_ok=True)

    arquivo_csv = (
        RESULTADOS / "aula10_avaliacao_politica.csv"
    )
    arquivo_json = (
        RESULTADOS / "aula10_relatorio_implantacao.json"
    )

    salvar_csv(arquivo_csv, resultados)

    relatorio = {
        "aula": 10,
        "politica": politica["nome"],
        "total_ativos": len(ativos),
        "avaliacoes": resultados,
        "pendencias": pendentes,
        "recomendacoes": [
            "Capacitar os engenheiros de dados.",
            "Formalizar os responsaveis pelas bases.",
            "Registrar a linhagem por tabela para SOT e SPEC.",
            "Detalhar a linhagem por coluna nos processos regulatorios.",
            "Revisar periodicamente a politica.",
        ],
        "limitacoes": [
            "Inventario e criterios didaticos.",
            "Responsaveis formais nao confirmados.",
            "Nenhuma conformidade legal certificada.",
            "O relatorio regulatorio e ficticio.",
        ],
    }

    arquivo_json.write_text(
        json.dumps(
            relatorio, ensure_ascii=False, indent=4
        ),
        encoding="utf-8",
    )

    print("CSV:", arquivo_csv.name)
    print("JSON:", arquivo_json.name)

    titulo("7. TESTES AUTOMATIZADOS")

    assert politica["aula"] == 10
    assert len(ativos) == 6
    assert len(resultados) == 6
    assert len(pendentes) == 1

    dispensados = [
        item for item in resultados
        if item["situacao"] == "DISPENSADO_NESTA_POLITICA"
    ]
    conformes = [
        item for item in resultados
        if item["situacao"] == "ATENDE_POLITICA_DIDATICA"
    ]

    assert len(dispensados) == 1
    assert len(conformes) == 4

    assert pendentes[0]["ativo"] == (
        "relatorio_regulatorio_ficticio"
    )
    assert pendentes[0]["nivel_exigido"] == "coluna"

    assert arquivo_csv.is_file()
    assert arquivo_json.is_file()

    with arquivo_json.open(encoding="utf-8") as arquivo:
        salvo = json.load(arquivo)

    assert salvo["aula"] == 10
    assert len(salvo["avaliacoes"]) == 6

    titulo("RESULTADO FINAL")

    print("Ativos avaliados:", len(ativos))
    print("SOR dispensadas:", len(dispensados))
    print("Ativos que atendem a politica:", len(conformes))
    print("Ativos pendentes:", len(pendentes))
    print("Relatorios gerados: 2")
    print("Bases anteriores preservadas.")
    print("Todos os testes passaram.")
    print("Aula 10 executada com sucesso.")


if __name__ == "__main__":
    main()