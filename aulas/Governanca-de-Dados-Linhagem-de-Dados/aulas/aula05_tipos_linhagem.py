from pathlib import Path
import csv
import json
import sqlite3


BASE = Path(__file__).resolve().parent.parent
DADOS = BASE / "dados"
RESULTADOS = BASE / "resultados"

DADOS.mkdir(parents=True, exist_ok=True)
RESULTADOS.mkdir(parents=True, exist_ok=True)

BANCO = DADOS / "aula05_tipos_linhagem.sqlite3"


def titulo(texto):
    print("\n" + "=" * 65)
    print(texto)
    print("=" * 65)


def preparar_banco(conexao):
    """Cria tres fontes ficticias de informacao."""

    conexao.executescript("""
        DROP VIEW IF EXISTS vw_avaliacao_imobiliaria;
        DROP TABLE IF EXISTS precos_imoveis;
        DROP TABLE IF EXISTS transacoes_cartorio;
        DROP TABLE IF EXISTS analises_anteriores;

        CREATE TABLE precos_imoveis (
            cidade TEXT PRIMARY KEY,
            preco_m2 REAL NOT NULL
        );

        CREATE TABLE transacoes_cartorio (
            cidade TEXT PRIMARY KEY,
            negocios_mes_atual INTEGER NOT NULL
        );

        CREATE TABLE analises_anteriores (
            cidade TEXT PRIMARY KEY,
            negocios_mes_anterior INTEGER NOT NULL
        );
    """)

    conexao.executemany(
        "INSERT INTO precos_imoveis VALUES (?, ?)",
        [
            ("Salvador", 6500.0),
            ("Recife", 7200.0),
        ],
    )

    conexao.executemany(
        "INSERT INTO transacoes_cartorio VALUES (?, ?)",
        [
            ("Salvador", 120),
            ("Recife", 90),
        ],
    )

    conexao.executemany(
        "INSERT INTO analises_anteriores VALUES (?, ?)",
        [
            ("Salvador", 100),
            ("Recife", 100),
        ],
    )

    conexao.executescript("""
        CREATE VIEW vw_avaliacao_imobiliaria AS
        SELECT
            t.cidade,
            p.preco_m2,
            t.negocios_mes_atual,
            a.negocios_mes_anterior,
            CASE
                WHEN a.negocios_mes_anterior = 0 THEN NULL
                ELSE ROUND(
                    (
                        CAST(t.negocios_mes_atual AS REAL)
                        - a.negocios_mes_anterior
                    )
                    / a.negocios_mes_anterior * 100,
                    2
                )
            END AS variacao_pct
        FROM transacoes_cartorio AS t
        INNER JOIN precos_imoveis AS p
            ON p.cidade = t.cidade
        INNER JOIN analises_anteriores AS a
            ON a.cidade = t.cidade;
    """)

    conexao.commit()


def consultar(conexao):
    conexao.row_factory = sqlite3.Row

    cursor = conexao.execute("""
        SELECT *
        FROM vw_avaliacao_imobiliaria
        ORDER BY cidade
    """)

    return [dict(linha) for linha in cursor.fetchall()]


def salvar_json(caminho, conteudo):
    caminho.write_text(
        json.dumps(conteudo, indent=4, ensure_ascii=False),
        encoding="utf-8",
    )


def salvar_csv(caminho, registros):
    with caminho.open(
        "w", newline="", encoding="utf-8-sig"
    ) as arquivo:
        escritor = csv.DictWriter(
            arquivo, fieldnames=list(registros[0].keys())
        )
        escritor.writeheader()
        escritor.writerows(registros)


def main():
    titulo("ALURA - AULA 05")
    print("TIPOS DE LINHAGEM DE DADOS")

    titulo("1. CRIANDO AS ORIGENS")

    with sqlite3.connect(BANCO) as conexao:
        preparar_banco(conexao)
        resultados = consultar(conexao)

        colunas_origem = {}

        for tabela in (
            "precos_imoveis",
            "transacoes_cartorio",
            "analises_anteriores",
        ):
            colunas_origem[tabela] = {
                linha["name"]
                for linha in conexao.execute(
                    f"PRAGMA table_info({tabela})"
                )
            }

        colunas_destino = {
            linha["name"]
            for linha in conexao.execute(
                "PRAGMA table_info(vw_avaliacao_imobiliaria)"
            )
        }

    print("D1: precos_imoveis")
    print("D2: transacoes_cartorio")
    print("D3: analises_anteriores")
    print("Destino: vw_avaliacao_imobiliaria")

    # ================================================
    # LINHAGEM EM NIVEL DE TABELA
    # ================================================

    titulo("2. LINHAGEM POR TABELA")

    destino = "vw_avaliacao_imobiliaria"

    linhagem_tabelas = [
        {
            "origem": "precos_imoveis",
            "destino": destino,
            "relacao": "fornece precos por metro quadrado",
        },
        {
            "origem": "transacoes_cartorio",
            "destino": destino,
            "relacao": "fornece negocios do mes atual",
        },
        {
            "origem": "analises_anteriores",
            "destino": destino,
            "relacao": "fornece negocios do mes anterior",
        },
    ]

    for relacao in linhagem_tabelas:
        print(
            f"{relacao['origem']} -> {relacao['destino']}"
        )

    # ================================================
    # LINHAGEM EM NIVEL DE COLUNA
    # ================================================

    titulo("3. LINHAGEM POR COLUNA")

    linhagem_colunas = [
        {
            "coluna_destino": "cidade",
            "origens": [
                {"tabela": "transacoes_cartorio", "coluna": "cidade"}
            ],
            "transformacao": "SELECT",
        },
        {
            "coluna_destino": "preco_m2",
            "origens": [
                {"tabela": "precos_imoveis", "coluna": "preco_m2"}
            ],
            "transformacao": "SELECT",
        },
        {
            "coluna_destino": "negocios_mes_atual",
            "origens": [
                {
                    "tabela": "transacoes_cartorio",
                    "coluna": "negocios_mes_atual",
                }
            ],
            "transformacao": "SELECT",
        },
        {
            "coluna_destino": "negocios_mes_anterior",
            "origens": [
                {
                    "tabela": "analises_anteriores",
                    "coluna": "negocios_mes_anterior",
                }
            ],
            "transformacao": "SELECT",
        },
        {
            "coluna_destino": "variacao_pct",
            "origens": [
                {
                    "tabela": "transacoes_cartorio",
                    "coluna": "negocios_mes_atual",
                },
                {
                    "tabela": "analises_anteriores",
                    "coluna": "negocios_mes_anterior",
                },
            ],
            "transformacao": (
                "(atual - anterior) / anterior * 100; "
                "NULL se anterior = 0"
            ),
        },
    ]

    for item in linhagem_colunas:
        print("\nCOLUNA DESTINO:", item["coluna_destino"])
        print("Transformacao:", item["transformacao"])

        for origem in item["origens"]:
            print(
                f"  {origem['tabela']}.{origem['coluna']}"
            )

    titulo("4. RESULTADOS DOS CALCULOS")

    for registro in resultados:
        print(
            f"{registro['cidade']}: "
            f"{registro['negocios_mes_anterior']} -> "
            f"{registro['negocios_mes_atual']} negocios; "
            f"variacao = {registro['variacao_pct']}%"
        )

    # ================================================
    # DOCUMENTAR OS DOIS TIPOS DE LINHAGEM
    # ================================================

    titulo("5. SALVANDO ARQUIVOS")

    arquivos = {
        "tabelas": RESULTADOS / "aula05_linhagem_tabelas.json",
        "colunas": RESULTADOS / "aula05_linhagem_colunas.json",
        "csv": RESULTADOS / "aula05_resultado_imobiliario.csv",
    }

    salvar_json(
        arquivos["tabelas"],
        {
            "aula": 5,
            "tipo": "linhagem_por_tabela",
            "relacoes": linhagem_tabelas,
        },
    )

    salvar_json(
        arquivos["colunas"],
        {
            "aula": 5,
            "tipo": "linhagem_por_coluna",
            "destino": destino,
            "colunas": linhagem_colunas,
            "observacao": (
                "Exemplo didatico com dados ficticios. "
                "Chaves de cidade tambem participam dos JOINs."
            ),
        },
    )

    salvar_csv(arquivos["csv"], resultados)

    for caminho in arquivos.values():
        print("Arquivo criado:", caminho.name)

    titulo("6. TESTES AUTOMATIZADOS")

    assert len(linhagem_tabelas) == 3
    assert len(linhagem_colunas) == 5
    assert len(resultados) == 2

    # Validar todas as referencias documentadas.
    for item in linhagem_colunas:
        assert item["coluna_destino"] in colunas_destino

        for origem in item["origens"]:
            assert (
                origem["coluna"]
                in colunas_origem[origem["tabela"]]
            )

    variacao = next(
        item for item in linhagem_colunas
        if item["coluna_destino"] == "variacao_pct"
    )

    assert len(variacao["origens"]) == 2

    por_cidade = {
        item["cidade"]: item
        for item in resultados
    }

    assert por_cidade["Salvador"]["variacao_pct"] == 20.0
    assert por_cidade["Recife"]["variacao_pct"] == -10.0

    assert all(
        caminho.is_file()
        for caminho in arquivos.values()
    )

    for chave in ("tabelas", "colunas"):
        assert json.loads(
            arquivos[chave].read_text(encoding="utf-8")
        )["aula"] == 5

    titulo("RESULTADO FINAL")

    print("Tabelas de origem: 3")
    print("Tabelas de destino: 1")
    print("Relacoes entre tabelas: 3")
    print("Colunas de destino documentadas: 5")
    print("Origens da coluna variacao_pct: 2")
    print("Registros processados: 2")
    print("Arquivos gerados: 3")
    print("Todos os testes passaram.")
    print("Aula 05 executada com sucesso.")


if __name__ == "__main__":
    main()