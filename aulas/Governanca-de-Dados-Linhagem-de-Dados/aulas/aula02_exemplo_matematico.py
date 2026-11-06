from pathlib import Path
import sqlite3
import csv
import json


BASE = Path(__file__).resolve().parent.parent
DADOS = BASE / "dados"
RESULTADOS = BASE / "resultados"

DADOS.mkdir(exist_ok=True)
RESULTADOS.mkdir(exist_ok=True)

BANCO = DADOS / "aula02_linhagem.sqlite3"


def titulo(texto):
    print("\n" + "=" * 65)
    print(texto)
    print("=" * 65)


def criar_banco(conexao):
    """Cria tres origens de dados ficticios."""

    conexao.executescript("""
    DROP VIEW IF EXISTS vw_avaliacao_ativos;
    DROP TABLE IF EXISTS precos_imoveis;
    DROP TABLE IF EXISTS transacoes_cartorio;
    DROP TABLE IF EXISTS analises_anteriores;

    CREATE TABLE precos_imoveis (
        cidade TEXT PRIMARY KEY,
        preco_m2 REAL NOT NULL
    );

    CREATE TABLE transacoes_cartorio (
        cidade TEXT NOT NULL,
        tipo TEXT NOT NULL,
        quantidade INTEGER NOT NULL
    );

    CREATE TABLE analises_anteriores (
        cidade TEXT PRIMARY KEY,
        classificacao_anterior TEXT NOT NULL
    );
    """)

    conexao.executemany(
        "INSERT INTO precos_imoveis VALUES (?, ?)",
        [
            ("Salvador", 6500.00),
            ("Recife", 7200.00),
        ],
    )

    conexao.executemany(
        "INSERT INTO transacoes_cartorio VALUES (?, ?, ?)",
        [
            ("Salvador", "compra", 125),
            ("Salvador", "venda", 110),
            ("Recife", "compra", 90),
            ("Recife", "venda", 105),
        ],
    )

    conexao.executemany(
        "INSERT INTO analises_anteriores VALUES (?, ?)",
        [
            ("Salvador", "favoravel"),
            ("Recife", "neutra"),
        ],
    )

    conexao.commit()


def criar_view(conexao):
    """Aplica transformacoes sobre as origens D1, D2 e D3."""

    conexao.executescript("""
    CREATE VIEW vw_avaliacao_ativos AS
    WITH
    Q1 AS (
        SELECT cidade, preco_m2
        FROM precos_imoveis
    ),
    Q2 AS (
        SELECT
            cidade,
            SUM(
                CASE WHEN tipo = 'compra'
                THEN quantidade ELSE 0 END
            ) AS compras,
            SUM(
                CASE WHEN tipo = 'venda'
                THEN quantidade ELSE 0 END
            ) AS vendas
        FROM transacoes_cartorio
        GROUP BY cidade
    ),
    Q3 AS (
        SELECT cidade, classificacao_anterior
        FROM analises_anteriores
    )
    SELECT
        Q1.cidade,
        Q1.preco_m2,
        Q2.compras,
        Q2.vendas,
        (Q2.compras - Q2.vendas) AS saldo_transacoes,
        Q3.classificacao_anterior,
        CASE
            WHEN Q2.compras > Q2.vendas
            AND Q3.classificacao_anterior = 'favoravel'
            THEN 'favoravel'
            ELSE 'revisar'
        END AS classificacao_didatica
    FROM Q1
    INNER JOIN Q2 ON Q1.cidade = Q2.cidade
    INNER JOIN Q3 ON Q1.cidade = Q3.cidade;
    """)

    conexao.commit()


def consultar_view(conexao):
    conexao.row_factory = sqlite3.Row

    cursor = conexao.execute("""
        SELECT *
        FROM vw_avaliacao_ativos
        ORDER BY cidade
    """)

    return [dict(linha) for linha in cursor.fetchall()]


def salvar_csv(registros, destino):
    with destino.open(
        "w", newline="", encoding="utf-8-sig"
    ) as arquivo:
        escritor = csv.DictWriter(
            arquivo,
            fieldnames=list(registros[0].keys()),
        )
        escritor.writeheader()
        escritor.writerows(registros)


def main():
    titulo("ALURA - AULA 02")
    print("EXEMPLO MATEMATICO DA LINHAGEM DE DADOS")

    titulo("1. EQUACOES")

    print("V = Q(D)")
    print("V = Q1(D1) + Q2(D2) + Q3(D3)")
    print(
        "O sinal + representa a combinacao conceitual "
        "das transformacoes."
    )

    titulo("2. ORIGENS")

    origens = {
        "D1": "precos_imoveis",
        "D2": "transacoes_cartorio",
        "D3": "analises_anteriores",
    }

    for identificador, nome in origens.items():
        print(f"{identificador}: {nome}")

    titulo("3. CRIANDO BASE E TRANSFORMACOES SQL")

    with sqlite3.connect(BANCO) as conexao:
        criar_banco(conexao)
        criar_view(conexao)

        destino = consultar_view(conexao)

        views = conexao.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type = 'view'
        """).fetchall()

    print("Banco SQLite:", BANCO.name)
    print("VIEW SQL:", views[0][0])
    print("SELECT: OK")
    print("JOIN: OK")
    print("GROUP BY: OK")
    print("ORDER BY: OK")

    titulo("4. BASE RESULTANTE V")

    for linha in destino:
        print(linha)

    titulo("5. DOCUMENTANDO LINHAGEM MATEMATICA")

    linhagem = {
        "aula": 2,
        "equacao_simples": "V = Q(D)",
        "equacao_multiplas_origens": (
            "V = Q1(D1) + Q2(D2) + Q3(D3)"
        ),
        "origens": origens,
        "transformacoes": {
            "Q1": "SELECT dos precos por m2",
            "Q2": "GROUP BY e SUM de compras e vendas",
            "Q3": "SELECT das analises anteriores",
            "combinacao": [
                "INNER JOIN pela cidade",
                "Calculo do saldo das transacoes",
                "Classificacao didatica ficticia",
            ],
        },
        "destino": "vw_avaliacao_ativos",
        "observacao": (
            "Exercicio didatico com dados ficticios. "
            "Nao constitui recomendacao de investimento."
        ),
    }

    arquivo_json = (
        RESULTADOS / "aula02_linhagem_matematica.json"
    )

    arquivo_csv = (
        RESULTADOS / "aula02_avaliacao_ativos.csv"
    )

    arquivo_json.write_text(
        json.dumps(
            linhagem,
            ensure_ascii=False,
            indent=4
        ),
        encoding="utf-8",
    )

    salvar_csv(destino, arquivo_csv)

    titulo("6. TESTES AUTOMATIZADOS")

    assert len(origens) == 3
    assert len(destino) == 2

    por_cidade = {
        linha["cidade"]: linha
        for linha in destino
    }

    assert por_cidade["Salvador"]["saldo_transacoes"] == 15
    assert por_cidade["Recife"]["saldo_transacoes"] == -15

    assert (
        por_cidade["Salvador"]["classificacao_didatica"]
        == "favoravel"
    )

    assert (
        por_cidade["Recife"]["classificacao_didatica"]
        == "revisar"
    )

    assert BANCO.exists()
    assert arquivo_json.exists()
    assert arquivo_csv.exists()

    with arquivo_json.open(encoding="utf-8") as arquivo:
        salvo = json.load(arquivo)

    assert salvo["origens"] == origens
    assert salvo["destino"] == "vw_avaliacao_ativos"

    titulo("RESULTADO FINAL")

    print("Origens de dados: 3")
    print("Transformacoes Q: 3")
    print("Visoes SQL: 1")
    print("Registros resultantes: 2")
    print("Arquivos criados: 3")
    print("Todos os testes passaram.")
    print("Aula 02 executada com sucesso.")


if __name__ == "__main__":
    main()