from pathlib import Path
from datetime import date
import csv
import json
import sqlite3


BASE = Path(__file__).resolve().parent.parent
BANCO = BASE / "dados" / "aula04_especializacao.sqlite3"
RESULTADOS = BASE / "resultados"

DATA_REFERENCIA = date(2026, 11, 6)
LIMITE_SEIS_MESES = date(2026, 5, 6)


def titulo(texto):
    print("\n" + "=" * 65)
    print(texto)
    print("=" * 65)


def consultar(conexao, tabela):
    permitidas = {
        "sor_assinantes",
        "sot_clientes_tratados",
        "spec_clientes_ativos",
        "spec_ativos_mais_6_meses",
        "spec_clientes_sp",
    }

    if tabela not in permitidas:
        raise ValueError("Base nao autorizada")

    cursor = conexao.execute(
        f"SELECT * FROM {tabela} ORDER BY cliente_id"
    )

    return [dict(item) for item in cursor.fetchall()]


def ids(registros):
    return {item["cliente_id"] for item in registros}


def especializar(registros_ativos):
    """Recalcula as duas bases dependentes da SPEC ativa."""

    mais_seis_meses = [
        item for item in registros_ativos
        if date.fromisoformat(item["data_inicio"])
        < LIMITE_SEIS_MESES
    ]

    clientes_sp = [
        item for item in mais_seis_meses
        if item["estado"] == "SP"
    ]

    return mais_seis_meses, clientes_sp


def exportar_csv(caminho, linhas):
    campos = [
        "base",
        "quantidade_original",
        "quantidade_com_falha",
        "diferenca",
        "clientes_ausentes",
    ]

    with caminho.open(
        "w", newline="", encoding="utf-8-sig"
    ) as arquivo:
        escritor = csv.DictWriter(
            arquivo, fieldnames=campos
        )
        escritor.writeheader()
        escritor.writerows(linhas)


def main():
    titulo("ALURA - AULA 06")
    print("BENEFICIOS DA LINHAGEM DE DADOS")

    # 1. REUTILIZAR O BANCO ORIGINAL, SEM MODIFICAR
    titulo("1. CARREGANDO BASES DA AULA 04")

    assert BANCO.is_file(), "Banco da Aula 04 nao encontrado"

    # Banco aberto somente para leitura.
    uri = BANCO.resolve().as_uri() + "?mode=ro"

    with sqlite3.connect(uri, uri=True) as conexao:
        conexao.row_factory = sqlite3.Row

        sor = consultar(conexao, "sor_assinantes")
        sot = consultar(conexao, "sot_clientes_tratados")
        ativos = consultar(conexao, "spec_clientes_ativos")
        seis_meses = consultar(
            conexao, "spec_ativos_mais_6_meses"
        )
        sp = consultar(conexao, "spec_clientes_sp")

    print("SOR:", len(sor))
    print("SOT:", len(sot))
    print("SPEC ativos:", len(ativos))
    print("SPEC mais de 6 meses:", len(seis_meses))
    print("SPEC SP:", len(sp))

    # 2. SIMULAR FALHA EM UMA BASE INTERMEDIARIA
    titulo("2. SIMULANDO FALHA DE PROCESSAMENTO")

    cliente_omitido = "C001"

    ativos_com_falha = [
        item for item in ativos
        if item["cliente_id"] != cliente_omitido
    ]

    print("Base afetada: spec_clientes_ativos")
    print("Cliente omitido artificialmente:", cliente_omitido)
    print("Banco original preservado.")

    # 3. PROPAGAR A FALHA PARA BASES DEPENDENTES
    titulo("3. PROPAGACAO DA FALHA")

    seis_meses_falha, sp_falha = especializar(
        ativos_com_falha
    )

    comparacoes = [
        (
            "spec_clientes_ativos",
            ativos,
            ativos_com_falha,
        ),
        (
            "spec_ativos_mais_6_meses",
            seis_meses,
            seis_meses_falha,
        ),
        (
            "spec_clientes_sp",
            sp,
            sp_falha,
        ),
    ]

    relatorio = []

    for nome, original, afetada in comparacoes:
        ausentes = sorted(ids(original) - ids(afetada))

        relatorio.append({
            "base": nome,
            "quantidade_original": len(original),
            "quantidade_com_falha": len(afetada),
            "diferenca": len(original) - len(afetada),
            "clientes_ausentes": ",".join(ausentes),
        })

        print(
            f"{nome}: {len(original)} -> "
            f"{len(afetada)} registros; "
            f"ausentes: {ausentes}"
        )

    # 4. MAPEAR DEPENDENCIAS
    titulo("4. RASTREABILIDADE")

    linhagem = [
        {
            "origem": "sor_assinantes",
            "destino": "sot_clientes_tratados",
            "operacao": "validacao de qualidade",
            "area_responsavel_exemplo": "Engenharia de Dados",
        },
        {
            "origem": "sot_clientes_tratados",
            "destino": "spec_clientes_ativos",
            "operacao": "filtrar clientes ativos",
            "area_responsavel_exemplo": "Engenharia de Dados",
        },
        {
            "origem": "spec_clientes_ativos",
            "destino": "spec_ativos_mais_6_meses",
            "operacao": "filtrar tempo de assinatura",
            "area_responsavel_exemplo": "Marketing",
        },
        {
            "origem": "spec_ativos_mais_6_meses",
            "destino": "spec_clientes_sp",
            "operacao": "filtrar estado SP",
            "area_responsavel_exemplo": "Marketing",
        },
    ]

    for item in linhagem:
        print(
            f"{item['origem']} -> {item['destino']}"
        )

    print("\nDIAGNOSTICO:")
    print(
        "A simulacao removeu C001 da base "
        "spec_clientes_ativos."
    )
    print(
        "As duas especializacoes posteriores "
        "tambem perderam esse cliente."
    )
    print(
        "As areas responsaveis sao ilustrativas, "
        "nao atribuicoes reais."
    )

    # 5. GERAR EVIDENCIAS PARA AUDITORIA
    titulo("5. DOCUMENTANDO EVIDENCIAS")

    RESULTADOS.mkdir(parents=True, exist_ok=True)

    arquivo_csv = (
        RESULTADOS / "aula06_impacto_falha.csv"
    )

    arquivo_json = (
        RESULTADOS / "aula06_rastreabilidade.json"
    )

    exportar_csv(arquivo_csv, relatorio)

    documento = {
        "aula": 6,
        "tema": "Beneficios da linhagem de dados",
        "data_referencia": DATA_REFERENCIA.isoformat(),
        "cenario": "simulacao didatica de falha",
        "banco_origem": BANCO.name,
        "ativo_com_falha": "spec_clientes_ativos",
        "cliente_omitido": cliente_omitido,
        "dependencias": linhagem,
        "impacto": relatorio,
        "beneficios": [
            "eficiencia",
            "transparencia",
            "rastreabilidade",
            "auditoria",
            "visibilidade",
            "atribuicao de responsabilidades",
        ],
        "observacoes": [
            "O banco SQLite original nao foi modificado.",
            "A falha foi simulada apenas em memoria.",
            "O relatorio permite investigar o impacto.",
            "Responsabilidades sao exemplos didaticos.",
            "A linhagem apoia auditorias, mas nao "
            "garante conformidade por si so.",
        ],
    }

    arquivo_json.write_text(
        json.dumps(
            documento, ensure_ascii=False, indent=4
        ),
        encoding="utf-8",
    )

    print("CSV:", arquivo_csv.name)
    print("JSON:", arquivo_json.name)

    # 6. VALIDACOES
    titulo("6. TESTES AUTOMATIZADOS")

    assert len(sor) == 10
    assert len(sot) == 7
    assert len(ativos) == 5
    assert len(seis_meses) == 3
    assert len(sp) == 2

    assert len(ativos_com_falha) == 4
    assert len(seis_meses_falha) == 2
    assert len(sp_falha) == 1

    assert cliente_omitido in ids(ativos)
    assert cliente_omitido not in ids(ativos_com_falha)
    assert cliente_omitido not in ids(seis_meses_falha)
    assert cliente_omitido not in ids(sp_falha)

    # A falha propagada remove o mesmo registro
    # das tres bases dependentes.
    assert all(
        item["diferenca"] == 1
        for item in relatorio
    )

    # Confere reprocessamento sem falha.
    seis_recalculado, sp_recalculado = especializar(
        ativos
    )

    assert ids(seis_recalculado) == ids(seis_meses)
    assert ids(sp_recalculado) == ids(sp)

    # Confere encadeamento da linhagem.
    for anterior, atual in zip(linhagem, linhagem[1:]):
        assert anterior["destino"] == atual["origem"]

    assert arquivo_csv.is_file()
    assert arquivo_json.is_file()

    with arquivo_json.open(encoding="utf-8") as arquivo:
        salvo = json.load(arquivo)

    assert salvo["cliente_omitido"] == "C001"
    assert len(salvo["dependencias"]) == 4

    titulo("RESULTADO FINAL")

    print("Banco anterior reutilizado: Aula 04")
    print("Bases dependentes analisadas: 3")
    print("Falhas simuladas: 1")
    print("Bases afetadas: 3")
    print("Relacoes de linhagem: 4")
    print("Relatorios gerados: 2")
    print("Banco original preservado.")
    print("Todos os testes passaram.")
    print("Aula 06 executada com sucesso.")


if __name__ == "__main__":
    main()