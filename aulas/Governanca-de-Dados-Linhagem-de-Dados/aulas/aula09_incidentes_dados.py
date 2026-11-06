from pathlib import Path
from datetime import datetime, timezone
import csv
import json
import sqlite3


BASE = Path(__file__).resolve().parent.parent
RESULTADOS = BASE / "resultados"

BANCO = BASE / "dados" / "aula04_especializacao.sqlite3"
LINHAGEM = RESULTADOS / "aula06_rastreabilidade.json"

CLIENTE_OMITIDO = "C001"
RELATORIO = "relatorio_regulatorio_ficticio"


def titulo(texto):
    print("\n" + "=" * 65)
    print(texto)
    print("=" * 65)


def carregar_json(caminho):
    with caminho.open(encoding="utf-8") as arquivo:
        return json.load(arquivo)


def consultar_base(conexao, nome):
    tabelas_permitidas = {
        "sor_assinantes",
        "sot_clientes_tratados",
        "spec_clientes_ativos",
        "spec_ativos_mais_6_meses",
        "spec_clientes_sp",
    }

    if nome not in tabelas_permitidas:
        raise ValueError("Base nao autorizada")

    cursor = conexao.execute(
        f"SELECT cliente_id FROM {nome}"
    )

    return {item[0] for item in cursor.fetchall()}


def dependentes(grafo, origem):
    """Percorre a linhagem para encontrar destinos afetados."""

    encontrados = []
    visitados = {origem}
    fila = [origem]

    while fila:
        atual = fila.pop(0)

        for relacao in grafo:
            if relacao["origem"] != atual:
                continue

            destino = relacao["destino"]

            if destino not in visitados:
                visitados.add(destino)
                encontrados.append(destino)
                fila.append(destino)

    return encontrados


def salvar_csv(caminho, registros):
    campos = [
        "ativo",
        "registros_originais",
        "registros_simulados",
        "diferenca",
        "status",
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
    titulo("ALURA - AULA 09")
    print("INCIDENTES DE DADOS")

    # ==============================================
    # 1. CONSULTAR BASES EXISTENTES
    # ==============================================

    titulo("1. BASES E LINHAGEM ORIGINAIS")

    assert BANCO.is_file()
    assert LINHAGEM.is_file()

    dados_linhagem = carregar_json(LINHAGEM)
    relacoes = dados_linhagem["dependencias"]

    uri = BANCO.resolve().as_uri() + "?mode=ro"

    with sqlite3.connect(uri, uri=True) as conexao:
        bases = {
            nome: consultar_base(conexao, nome)
            for nome in (
                "sor_assinantes",
                "sot_clientes_tratados",
                "spec_clientes_ativos",
                "spec_ativos_mais_6_meses",
                "spec_clientes_sp",
            )
        }

    for nome, registros in bases.items():
        print(f"{nome}: {len(registros)} registros")

    # ==============================================
    # 2. DOCUMENTAR DEPENDENCIA REGULATORIA FICTICIA
    # ==============================================

    titulo("2. PROCESSO DE NEGOCIO")

    dependencia_regulatoria = {
        "origem": "spec_clientes_ativos",
        "destino": RELATORIO,
        "operacao": "geracao de relatorio regulatorio simulado",
        "area_responsavel_exemplo": "Prevencao a Lavagem de Dinheiro",
    }

    grafo = relacoes + [dependencia_regulatoria]

    print("Processo:", RELATORIO)
    print("Fonte:", dependencia_regulatoria["origem"])
    print("Tipo: simulacao didatica")
    print("Nenhum relatorio real sera enviado")

    # ==============================================
    # 3. SIMULAR INCIDENTE NA SOR
    # ==============================================

    titulo("3. SIMULANDO INCIDENTE NA ORIGEM")

    print("Origem do incidente: sor_assinantes")
    print("Registro omitido na simulacao:", CLIENTE_OMITIDO)

    assert CLIENTE_OMITIDO in bases["sor_assinantes"]

    # A omissao se propaga somente aos conjuntos
    # que originalmente continham o registro.
    simuladas = {
        nome: registros - {CLIENTE_OMITIDO}
        for nome, registros in bases.items()
    }

    relatorio_original = set(bases["spec_clientes_ativos"])
    relatorio_simulado = set(
        simuladas["spec_clientes_ativos"]
    )

    # ==============================================
    # 4. ANALISE DE IMPACTO PELA LINHAGEM
    # ==============================================

    titulo("4. RASTREANDO IMPACTOS")

    destinos_afetados = dependentes(
        grafo, "sor_assinantes"
    )

    for nome in destinos_afetados:
        print("Dependente:", nome)

    resultados = []

    for nome, originais in bases.items():
        afetados = simuladas[nome]

        resultados.append({
            "ativo": nome,
            "registros_originais": len(originais),
            "registros_simulados": len(afetados),
            "diferenca": len(originais) - len(afetados),
            "status": (
                "IMPACTADO"
                if originais != afetados
                else "SEM_ALTERACAO"
            ),
        })

    resultados.append({
        "ativo": RELATORIO,
        "registros_originais": len(relatorio_original),
        "registros_simulados": len(relatorio_simulado),
        "diferenca": (
            len(relatorio_original) - len(relatorio_simulado)
        ),
        "status": "IMPACTADO",
    })

    for item in resultados:
        print(
            f"{item['ativo']}: "
            f"{item['registros_originais']} -> "
            f"{item['registros_simulados']} "
            f"({item['status']})"
        )

    # ==============================================
    # 5. PLANO DE RESPOSTA AO INCIDENTE
    # ==============================================

    titulo("5. PLANO DE RECUPERACAO")

    plano = [
        {
            "etapa": 1,
            "acao": "Registrar o incidente e seu impacto",
            "status": "documentado no laboratorio",
        },
        {
            "etapa": 2,
            "acao": "Identificar a origem usando a linhagem",
            "status": "identificada na simulacao",
        },
        {
            "etapa": 3,
            "acao": "Acionar a equipe responsavel pela SOR",
            "status": "acao proposta, nao executada",
        },
        {
            "etapa": 4,
            "acao": "Corrigir a origem e reprocessar as bases",
            "status": "acao proposta, nao executada",
        },
        {
            "etapa": 5,
            "acao": "Revalidar os dados e o relatorio",
            "status": "acao proposta, nao executada",
        },
        {
            "etapa": 6,
            "acao": "Registrar evidencias e encerrar o incidente",
            "status": "pendente de recuperacao real",
        },
    ]

    for etapa in plano:
        print(f"{etapa['etapa']}. {etapa['acao']}")
        print("   Status:", etapa["status"])

    # ==============================================
    # 6. GERAR RELATORIOS
    # ==============================================

    titulo("6. DOCUMENTANDO INCIDENTE")

    RESULTADOS.mkdir(parents=True, exist_ok=True)

    arquivo_csv = RESULTADOS / "aula09_impacto_incidente.csv"
    arquivo_json = RESULTADOS / "aula09_incidente_dados.json"

    salvar_csv(arquivo_csv, resultados)

    documento = {
        "aula": 9,
        "tema": "Incidentes de dados",
        "tipo": "simulacao didatica",
        "registrado_em_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "origem_incidente": "sor_assinantes",
        "causa_simulada": (
            "Omissao artificial do identificador C001"
        ),
        "identificador_ficticio": CLIENTE_OMITIDO,
        "relatorio_regulatorio": {
            "nome": RELATORIO,
            "carater": "ficticio",
            "interrupcao": "simulada",
        },
        "dependencias": grafo,
        "destinos_dependentes": destinos_afetados,
        "impacto": resultados,
        "plano_recuperacao": plano,
        "ressalvas": [
            "Nenhum banco original foi modificado.",
            "Nenhum orgao regulador foi contatado.",
            "Nenhum reprocessamento real foi realizado.",
            "A causa foi definida na simulacao; "
            "nao foi descoberta em incidente real.",
            "A linhagem indica dependencias, mas nao "
            "prova sozinha a causa de incidentes reais.",
        ],
    }

    arquivo_json.write_text(
        json.dumps(
            documento,
            ensure_ascii=False,
            indent=4,
        ),
        encoding="utf-8",
    )

    print("CSV:", arquivo_csv.name)
    print("JSON:", arquivo_json.name)

    # ==============================================
    # 7. TESTES AUTOMATIZADOS
    # ==============================================

    titulo("7. TESTES AUTOMATIZADOS")

    assert dados_linhagem["aula"] == 6
    assert len(relacoes) == 4
    assert len(grafo) == 5

    assert len(bases["sor_assinantes"]) == 9
    # A SOR tem 10 registros, incluindo um cliente
    # duplicado. O conjunto de IDs distintos tem 9.

    assert len(bases["sot_clientes_tratados"]) == 7
    assert len(bases["spec_clientes_ativos"]) == 5

    assert len(relatorio_original) == 5
    assert len(relatorio_simulado) == 4

    assert len(destinos_afetados) == 5
    assert RELATORIO in destinos_afetados

    assert all(
        item["diferenca"] == 1
        for item in resultados
    )

    assert len(plano) == 6
    assert arquivo_csv.is_file()
    assert arquivo_json.is_file()

    salvo = carregar_json(arquivo_json)
    assert salvo["aula"] == 9
    assert salvo["origem_incidente"] == "sor_assinantes"
    assert len(salvo["plano_recuperacao"]) == 6

    titulo("RESULTADO FINAL")

    print("Incidentes simulados: 1")
    print("Origem identificada: sor_assinantes")
    print("Relacoes de linhagem: 5")
    print("Destinos dependentes: 5")
    print("Bases/relatorios analisados: 6")
    print("Etapas no plano de recuperacao: 6")
    print("Relatorios gerados: 2")
    print("Banco original preservado.")
    print("Todos os testes passaram.")
    print("Aula 09 executada com sucesso.")


if __name__ == "__main__":
    main()