from pathlib import Path
from datetime import datetime, timezone
import csv
import json


BASE = Path(__file__).resolve().parent.parent
RESULTADOS = BASE / "resultados"
ARQUIVO_ORIGEM = RESULTADOS / "aula06_rastreabilidade.json"


def titulo(texto):
    print("\n" + "=" * 65)
    print(texto)
    print("=" * 65)


def carregar_linhagem():
    with ARQUIVO_ORIGEM.open(encoding="utf-8") as arquivo:
        return json.load(arquivo)


def rastrear_origens(dependencias, ativo):
    """Retorna a cadeia de origens a partir do ativo informado."""

    mapa = {
        item["destino"]: item
        for item in dependencias
    }

    caminho = []
    visitados = set()
    atual = ativo

    while atual in mapa:
        if atual in visitados:
            raise ValueError("Ciclo detectado na linhagem")

        visitados.add(atual)
        dependencia = mapa[atual]
        caminho.append(dependencia)
        atual = dependencia["origem"]

    return list(reversed(caminho))


def salvar_csv(caminho, registros):
    campos = [
        "origem",
        "destino",
        "operacao",
        "area_responsavel_exemplo",
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
    titulo("ALURA - AULA 07")
    print("ACCOUNTABILITY - PRESTACAO DE CONTAS")

    titulo("1. CARREGANDO EVIDENCIAS DA AULA 06")

    dados = carregar_linhagem()

    dependencias = dados["dependencias"]
    impacto = dados["impacto"]

    print("Cenario:", dados["cenario"])
    print("Ativo com falha:", dados["ativo_com_falha"])
    print("Dependencias documentadas:", len(dependencias))
    print("Bases afetadas:", len(impacto))

    titulo("2. RASTREANDO AS ORIGENS")

    ativo_final = "spec_clientes_sp"
    cadeia = rastrear_origens(dependencias, ativo_final)

    for item in cadeia:
        print(
            f"{item['origem']} -> {item['destino']}"
        )
        print("  Operacao:", item["operacao"])
        print(
            "  Area ilustrativa:",
            item["area_responsavel_exemplo"]
        )

    titulo("3. ANALISANDO RESPONSABILIDADES")

    responsabilidades = []

    for item in cadeia:
        responsabilidades.append({
            "ativo": item["destino"],
            "origem": item["origem"],
            "operacao": item["operacao"],
            "area_indicada": item["area_responsavel_exemplo"],
            "responsavel_formal_confirmado": False,
        })

    for item in responsabilidades:
        print(
            f"{item['ativo']}: "
            f"{item['area_indicada']} "
            "(atribuicao ilustrativa)"
        )

    titulo("4. VERIFICANDO EVIDENCIAS PARA AUDITORIA")

    verificacoes = {
        "origem_identificada": bool(cadeia),
        "transformacoes_documentadas": all(
            bool(item.get("operacao")) for item in cadeia
        ),
        "impacto_documentado": bool(impacto),
        "cenario_identificado": bool(dados.get("cenario")),
        "responsavel_formal_confirmado": False,
        "conformidade_legal_verificada": False,
        "controles_de_privacidade_auditados": False,
    }

    for nome, valor in verificacoes.items():
        print(f"{nome}: {'SIM' if valor else 'NAO'}")

    print(
        "\nNAO significa que a evidencia nao foi "
        "estabelecida neste laboratorio."
    )
    print(
        "Nao significa necessariamente que a "
        "organizacao esteja irregular."
    )

    titulo("5. GERANDO RELATORIO DE PRESTACAO DE CONTAS")

    relatorio = {
        "aula": 7,
        "tema": "Accountability",
        "tipo": "auditoria didatica de metadados",
        "gerado_em_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "fonte": ARQUIVO_ORIGEM.name,
        "ativo_final": ativo_final,
        "ativo_com_falha": dados["ativo_com_falha"],
        "origens_e_transformacoes": cadeia,
        "impacto_simulado": impacto,
        "responsabilidades": responsabilidades,
        "verificacoes": verificacoes,
        "limitacoes": [
            "Dados e responsabilidades sao ficticios.",
            "Nao foram auditados dados pessoais reais.",
            "Nao foi realizada auditoria juridica.",
            "A linhagem auxilia, mas nao garante "
            "conformidade legal.",
        ],
    }

    arquivo_json = (
        RESULTADOS / "aula07_relatorio_accountability.json"
    )

    arquivo_csv = (
        RESULTADOS / "aula07_cadeia_auditoria.csv"
    )

    arquivo_json.write_text(
        json.dumps(
            relatorio,
            ensure_ascii=False,
            indent=4,
        ),
        encoding="utf-8",
    )

    salvar_csv(arquivo_csv, cadeia)

    print("Relatorio JSON:", arquivo_json.name)
    print("Relatorio CSV:", arquivo_csv.name)

    titulo("6. TESTES AUTOMATIZADOS")

    assert dados["aula"] == 6
    assert len(dependencias) == 4
    assert len(cadeia) == 4
    assert len(impacto) == 3
    assert cadeia[0]["origem"] == "sor_assinantes"
    assert cadeia[-1]["destino"] == ativo_final

    assert verificacoes["origem_identificada"]
    assert verificacoes["transformacoes_documentadas"]
    assert verificacoes["impacto_documentado"]

    assert not verificacoes[
        "responsavel_formal_confirmado"
    ]
    assert not verificacoes[
        "conformidade_legal_verificada"
    ]

    assert arquivo_json.is_file()
    assert arquivo_csv.is_file()

    with arquivo_json.open(encoding="utf-8") as arquivo:
        salvo = json.load(arquivo)

    assert salvo["aula"] == 7
    assert len(salvo["origens_e_transformacoes"]) == 4

    titulo("RESULTADO FINAL")

    print("Aula anterior reutilizada: 06")
    print("Relacoes de linhagem auditadas: 4")
    print("Bases impactadas documentadas: 3")
    print("Verificacoes de auditoria: 7")
    print("Relatorios gerados: 2")
    print("Dados anteriores preservados.")
    print("Todos os testes passaram.")
    print("Aula 07 executada com sucesso.")


if __name__ == "__main__":
    main()