from pathlib import Path
from collections import Counter
import csv
import json
import sqlite3


BASE = Path(__file__).resolve().parent.parent
BANCO = BASE / "dados" / "aula04_especializacao.sqlite3"
RESULTADOS = BASE / "resultados"
TABELA = "sor_assinantes"


def titulo(texto):
    print("\n" + "=" * 65)
    print(texto)
    print("=" * 65)


def salvar_csv(caminho, registros, campos):
    with caminho.open(
        "w", newline="", encoding="utf-8-sig"
    ) as arquivo:
        escritor = csv.DictWriter(
            arquivo, fieldnames=campos
        )
        escritor.writeheader()
        escritor.writerows(registros)


def criar_perfil(registros, esquema):
    total = len(registros)
    perfil = []

    for campo in esquema:
        nome = campo["name"]
        valores = [linha[nome] for linha in registros]

        preenchidos = [
            valor for valor in valores
            if valor is not None
        ]

        frequencias = Counter(preenchidos)
        distintos = len(frequencias)

        # Percentuais com denominadores explicitados.
        nulos = total - len(preenchidos)
        ocorrencias_unicas = sum(
            quantidade for quantidade in frequencias.values()
            if quantidade == 1
        )

        perfil.append({
            "coluna": nome,
            "tipo": campo["type"],
            "total_registros": total,
            "nulos": nulos,
            "nulos_pct": round(
                100 * nulos / total, 2
            ) if total else 0.0,
            "valores_distintos": distintos,
            "distintos_pct_nao_nulos": round(
                100 * distintos / len(preenchidos), 2
            ) if preenchidos else 0.0,
            "ocorrencias_unicas_pct_nao_nulos": round(
                100 * ocorrencias_unicas / len(preenchidos), 2
            ) if preenchidos else 0.0,
        })

    return perfil


def mascarar_amostra(registros):
    amostra = []

    for linha in registros[:5]:
        item = linha.copy()

        # Valores ficticios, mas mascarados para demonstrar
        # uma pratica de minimizacao da exposicao.
        for campo in ("nome", "email", "cliente_id"):
            if item[campo] is not None:
                item[campo] = "***MASCARADO***"

        amostra.append(item)

    return amostra


def main():
    titulo("ALURA - AULA 11")
    print("FUNCIONALIDADES DA OPENMETADATA")

    titulo("1. EXPLORANDO O SCHEMA")

    assert BANCO.is_file(), "Banco da Aula 04 ausente"

    # Banco existente aberto somente para leitura.
    uri = BANCO.resolve().as_uri() + "?mode=ro"

    with sqlite3.connect(uri, uri=True) as conexao:
        conexao.row_factory = sqlite3.Row

        esquema = [
            dict(linha) for linha in conexao.execute(
                "PRAGMA table_info(sor_assinantes)"
            )
        ]

        registros = [
            dict(linha) for linha in conexao.execute(
                "SELECT * FROM sor_assinantes ORDER BY registro_id"
            )
        ]

    for coluna in esquema:
        print(
            f"{coluna['name']}: {coluna['type']}"
        )

    print("Total de colunas:", len(esquema))
    print("Total de registros:", len(registros))

    titulo("2. PROFILER - QUALIDADE DAS COLUNAS")

    perfil = criar_perfil(registros, esquema)

    for item in perfil:
        print(
            f"{item['coluna']}: "
            f"nulos={item['nulos']} "
            f"({item['nulos_pct']}%), "
            f"distintos={item['valores_distintos']}, "
            f"distintos%={item['distintos_pct_nao_nulos']}%"
        )

    titulo("3. SAMPLE DATA - DADOS MASCARADOS")

    amostra = mascarar_amostra(registros)

    for item in amostra:
        print(item)

    titulo("4. QUERIES E LINHAGEM")

    consultas = [
        "SELECT * FROM sor_assinantes",
        "SELECT COUNT(*) FROM sor_assinantes",
        "SELECT status, COUNT(*) FROM sor_assinantes GROUP BY status",
    ]

    for consulta in consultas:
        print("SQL:", consulta)

    linhagem = [
        {
            "origem": "sor_assinantes",
            "destino": "sot_clientes_tratados",
            "transformacao": "tratamento de qualidade"
        },
        {
            "origem": "sot_clientes_tratados",
            "destino": "spec_clientes_ativos",
            "transformacao": "filtro de clientes ativos"
        }
    ]

    for etapa in linhagem:
        print(
            etapa["origem"], "->", etapa["destino"]
        )

    titulo("5. CATALOGO DE METADADOS")

    descricoes = {
        "registro_id": "Identificador do registro bruto",
        "cliente_id": "Identificador do cliente ficticio",
        "nome": "Nome do assinante",
        "email": "Email do assinante",
        "estado": "Unidade federativa cadastrada",
        "data_inicio": "Data de inicio da assinatura",
        "status": "Situacao da assinatura",
    }

    colunas_catalogo = []

    for campo in esquema:
        nome = campo["name"]

        colunas_catalogo.append({
            "nome": nome,
            "tipo": campo["type"],
            "descricao": descricoes.get(nome),
            "tags_didaticas": (
                ["DadoPessoal"]
                if nome in ("nome", "email")
                else ["Identificador"]
                if nome == "cliente_id"
                else []
            ),
        })

    catalogo = {
        "aula": 11,
        "ferramenta_estudada": "OpenMetadata",
        "tipo_laboratorio": "simulacao local em SQLite",
        "base": TABELA,
        "tecnologia": "SQLite",
        "quantidade_registros": len(registros),
        "colunas": colunas_catalogo,
        "linhagem_ilustrativa": linhagem,
        "consultas_exemplo": consultas,
        "observacoes": [
            "Catalogo gerado localmente, sem API do OpenMetadata.",
            "Dados de clientes inteiramente ficticios.",
            "Tags de exemplo, sem classificacao juridica validada.",
            "Mascaramento aplicado somente na amostra exportada.",
            "Estatisticas calculadas sobre os registros ficticios.",
        ]
    }

    titulo("6. SALVANDO RESULTADOS")

    RESULTADOS.mkdir(parents=True, exist_ok=True)

    arquivo_catalogo = (
        RESULTADOS / "aula11_catalogo_metadados.json"
    )

    arquivo_perfil = (
        RESULTADOS / "aula11_perfil_colunas.csv"
    )

    arquivo_amostra = (
        RESULTADOS / "aula11_amostra_mascarada.csv"
    )

    arquivo_catalogo.write_text(
        json.dumps(
            catalogo, indent=4, ensure_ascii=False
        ),
        encoding="utf-8"
    )

    salvar_csv(
        arquivo_perfil,
        perfil,
        list(perfil[0].keys())
    )

    salvar_csv(
        arquivo_amostra,
        amostra,
        list(amostra[0].keys())
    )

    for caminho in (
        arquivo_catalogo,
        arquivo_perfil,
        arquivo_amostra
    ):
        print("Arquivo:", caminho.name)

    titulo("7. TESTES AUTOMATIZADOS")

    assert len(registros) == 10
    assert len(esquema) == 7
    assert len(perfil) == 7
    assert len(amostra) == 5
    assert len(linhagem) == 2

    por_coluna = {
        item["coluna"]: item for item in perfil
    }

    assert por_coluna["nome"]["nulos"] == 1
    assert por_coluna["email"]["nulos"] == 1
    assert por_coluna["cliente_id"]["valores_distintos"] == 9
    assert por_coluna["registro_id"]["valores_distintos"] == 10

    assert all(
        item["nome"] == "***MASCARADO***"
        for item in amostra
        if item["nome"] is not None
    )

    assert all(
        item["email"] == "***MASCARADO***"
        for item in amostra
        if item["email"] is not None
    )

    assert all(
        caminho.is_file()
        for caminho in (
            arquivo_catalogo,
            arquivo_perfil,
            arquivo_amostra
        )
    )

    salvo = json.loads(
        arquivo_catalogo.read_text(encoding="utf-8")
    )

    assert salvo["aula"] == 11
    assert len(salvo["colunas"]) == 7

    titulo("RESULTADO FINAL")

    print("Tabela analisada:", TABELA)
    print("Registros analisados:", len(registros))
    print("Colunas catalogadas:", len(esquema))
    print("Amostras mascaradas:", len(amostra))
    print("Relacoes de linhagem:", len(linhagem))
    print("Arquivos gerados: 3")
    print("Banco original preservado.")
    print("Todos os testes passaram.")
    print("Aula 11 executada com sucesso.")


if __name__ == "__main__":
    main()