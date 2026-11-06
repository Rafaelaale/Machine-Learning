from pathlib import Path
import csv
import json
import sqlite3


BASE = Path(__file__).resolve().parent.parent
RESULTADOS = BASE / "resultados"
BANCO = BASE / "dados" / "aula04_especializacao.sqlite3"
AUDITORIA_ANTERIOR = (
    RESULTADOS / "aula07_relatorio_accountability.json"
)

ATIVO_AUDITADO = "spec_ativos_mais_6_meses"

# Permissoes ficticias para demonstrar o conceito.
PERMISSOES = {
    "engenharia_dados": {
        "sot_clientes_tratados",
        "spec_clientes_ativos",
        "spec_ativos_mais_6_meses",
    },
    "marketing": {
        "spec_ativos_mais_6_meses",
    },
    "visitante": set(),
}

# Eventos simulados. Nao representam acessos reais.
EVENTOS = [
    {
        "evento_id": "E001",
        "data_hora_utc": "2026-11-06T10:00:00Z",
        "identidade_ficticia": "usuario_teste_01",
        "grupo": "marketing",
        "ativo": ATIVO_AUDITADO,
        "operacao": "SELECT",
    },
    {
        "evento_id": "E002",
        "data_hora_utc": "2026-11-06T10:05:00Z",
        "identidade_ficticia": "usuario_teste_02",
        "grupo": "engenharia_dados",
        "ativo": ATIVO_AUDITADO,
        "operacao": "SELECT",
    },
    {
        "evento_id": "E003",
        "data_hora_utc": "2026-11-06T10:10:00Z",
        "identidade_ficticia": "usuario_teste_03",
        "grupo": "visitante",
        "ativo": ATIVO_AUDITADO,
        "operacao": "SELECT",
    },
]


def titulo(texto):
    print("\n" + "=" * 65)
    print(texto)
    print("=" * 65)


def carregar_json(caminho):
    with caminho.open(encoding="utf-8") as arquivo:
        return json.load(arquivo)


def consultar_esquema():
    """Le apenas o esquema da base original."""
    uri = BANCO.resolve().as_uri() + "?mode=ro"

    with sqlite3.connect(uri, uri=True) as conexao:
        colunas = conexao.execute(
            "PRAGMA table_info(spec_ativos_mais_6_meses)"
        ).fetchall()

    return [item[1] for item in colunas]


def registrar_evento(evento):
    """Simula avaliacao de permissao e gera log."""
    grupo = evento["grupo"]
    ativo = evento["ativo"]

    autorizado = ativo in PERMISSOES.get(grupo, set())

    return {
        **evento,
        "autorizado": autorizado,
        "resultado": (
            "ACESSO_PERMITIDO" if autorizado
            else "ACESSO_NEGADO"
        ),
        "tipo_registro": "SIMULADO",
    }


def rastrear_origens(dependencias, destino):
    """Recupera as transformacoes ate a origem."""
    por_destino = {
        item["destino"]: item
        for item in dependencias
    }

    caminho = []
    visitados = set()
    atual = destino

    while atual in por_destino:
        if atual in visitados:
            raise ValueError("Ciclo na linhagem")

        visitados.add(atual)
        etapa = por_destino[atual]
        caminho.append(etapa)
        atual = etapa["origem"]

    return list(reversed(caminho))


def salvar_csv(caminho, registros):
    with caminho.open(
        "w", newline="", encoding="utf-8-sig"
    ) as arquivo:
        escritor = csv.DictWriter(
            arquivo,
            fieldnames=list(registros[0].keys()),
        )
        escritor.writeheader()
        escritor.writerows(registros)


def main():
    titulo("ALURA - AULA 08")
    print("ACCOUNTABILITY BY DESIGN")

    titulo("1. CARREGANDO A AUDITORIA ANTERIOR")

    anterior = carregar_json(AUDITORIA_ANTERIOR)

    assert anterior["aula"] == 7

    dependencias = anterior["origens_e_transformacoes"]
    cadeia = rastrear_origens(
        dependencias, ATIVO_AUDITADO
    )

    print("Arquivo utilizado:", AUDITORIA_ANTERIOR.name)
    print("Ativo auditado:", ATIVO_AUDITADO)
    print("Transformacoes anteriores:", len(cadeia))

    titulo("2. IDENTIFICANDO DADOS UTILIZADOS")

    colunas = consultar_esquema()

    for coluna in colunas:
        print("Coluna:", coluna)

    # Classificacao ilustrativa:
    # a efetiva classificacao e a identificacao dos
    # titulares dependem de governanca organizacional.
    catalogo = {
        "ativo": ATIVO_AUDITADO,
        "origem": "sor_assinantes",
        "colunas": colunas,
        "contexto": "assinaturas de newsletter ficticias",
        "possui_dados_relacionados_a_pessoas": True,
        "identificacao_titular_por_registro": (
            "nao verificada neste laboratorio"
        ),
        "responsavel_formal": None,
        "classificacao_privacidade_validada": False,
    }

    print("Contexto:", catalogo["contexto"])
    print(
        "Responsavel formal:",
        catalogo["responsavel_formal"]
    )

    titulo("3. GRUPOS E CONTROLE DE ACESSO")

    for grupo, ativos in PERMISSOES.items():
        print(
            f"{grupo}: {len(ativos)} ativos "
            "autorizados na simulacao"
        )

    titulo("4. SIMULANDO LOGS DE ACESSO")

    logs = [registrar_evento(e) for e in EVENTOS]

    for log in logs:
        print(
            f"{log['evento_id']} | "
            f"{log['grupo']} | "
            f"{log['ativo']} | "
            f"{log['resultado']}"
        )

    titulo("5. RASTREANDO TRANSFORMACOES")

    for etapa in cadeia:
        print(
            f"{etapa['origem']} -> {etapa['destino']}"
        )
        print("  Operacao:", etapa["operacao"])

    titulo("6. EVIDENCIAS PARA AUDITORIA")

    verificacoes = {
        "dados_identificados": len(colunas) > 0,
        "origem_documentada": len(cadeia) > 0,
        "transformacoes_documentadas": all(
            etapa.get("operacao") for etapa in cadeia
        ),
        "regras_de_acesso_simuladas": bool(PERMISSOES),
        "logs_de_teste_disponiveis": bool(logs),
        "logs_reais_de_acesso_disponiveis": False,
        "responsavel_formal_confirmado": False,
        "titulares_individualmente_verificados": False,
        "conformidade_legal_auditada": False,
    }

    for nome, valor in verificacoes.items():
        print(f"{nome}: {'SIM' if valor else 'NAO'}")

    print(
        "\nOs resultados se referem somente ao "
        "escopo do laboratorio didatico."
    )

    titulo("7. SALVANDO EVIDENCIAS")

    RESULTADOS.mkdir(parents=True, exist_ok=True)

    arquivo_logs = (
        RESULTADOS / "aula08_logs_simulados.csv"
    )
    arquivo_json = (
        RESULTADOS / "aula08_relatorio_accountability_design.json"
    )

    salvar_csv(arquivo_logs, logs)

    relatorio = {
        "aula": 8,
        "tema": "Accountability by Design",
        "tipo": "demonstracao didatica",
        "fonte": AUDITORIA_ANTERIOR.name,
        "catalogo": catalogo,
        "grupos_permissoes": {
            grupo: sorted(ativos)
            for grupo, ativos in PERMISSOES.items()
        },
        "linhagem": cadeia,
        "logs": logs,
        "verificacoes": verificacoes,
        "limitacoes": [
            "Dados, identidades e acessos ficticios.",
            "Permissoes apenas simuladas em Python.",
            "Nao foram coletados logs de acesso reais.",
            "A identidade de titulares nao foi auditada.",
            "Responsaveis formais nao foram confirmados.",
            "Nenhuma conformidade legal foi certificada.",
        ],
    }

    arquivo_json.write_text(
        json.dumps(
            relatorio,
            indent=4,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print("CSV:", arquivo_logs.name)
    print("JSON:", arquivo_json.name)

    titulo("8. TESTES AUTOMATIZADOS")

    assert len(colunas) == 6
    assert len(dependencias) == 4
    assert len(cadeia) == 3

    assert cadeia[0]["origem"] == "sor_assinantes"
    assert cadeia[-1]["destino"] == ATIVO_AUDITADO

    assert len(logs) == 3

    permitidos = [
        log for log in logs
        if log["autorizado"]
    ]
    negados = [
        log for log in logs
        if not log["autorizado"]
    ]

    assert len(permitidos) == 2
    assert len(negados) == 1
    assert negados[0]["grupo"] == "visitante"

    assert verificacoes["dados_identificados"]
    assert verificacoes["transformacoes_documentadas"]

    assert not verificacoes[
        "logs_reais_de_acesso_disponiveis"
    ]
    assert not verificacoes[
        "conformidade_legal_auditada"
    ]

    assert arquivo_logs.is_file()
    assert arquivo_json.is_file()

    salvo = carregar_json(arquivo_json)
    assert salvo["aula"] == 8
    assert len(salvo["logs"]) == 3

    titulo("RESULTADO FINAL")

    print("Aula anterior reutilizada: 07")
    print("Colunas identificadas:", len(colunas))
    print("Transformacoes rastreadas:", len(cadeia))
    print("Grupos de acesso:", len(PERMISSOES))
    print("Eventos simulados:", len(logs))
    print("Acessos permitidos:", len(permitidos))
    print("Acessos negados:", len(negados))
    print("Verificacoes de auditoria:", len(verificacoes))
    print("Relatorios gerados: 2")
    print("Banco original preservado.")
    print("Todos os testes passaram.")
    print("Aula 08 executada com sucesso.")


if __name__ == "__main__":
    main()