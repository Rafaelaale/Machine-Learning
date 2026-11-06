from pathlib import Path
import csv
import json
import sqlite3


BASE = Path(__file__).resolve().parent.parent
DADOS = BASE / "dados"
RESULTADOS = BASE / "resultados"

DADOS.mkdir(exist_ok=True)
RESULTADOS.mkdir(exist_ok=True)

BANCO = DADOS / "aula03_newsletter.sqlite3"


def titulo(texto):
    print("\n" + "=" * 65)
    print(texto)
    print("=" * 65)


def criar_origem(conexao):
    """Cria base ficticia de assinantes da newsletter."""

    conexao.executescript("""
        DROP VIEW IF EXISTS vw_clientes_ativos;
        DROP VIEW IF EXISTS vw_clientes_inativos;
        DROP VIEW IF EXISTS vw_clientes_cancelamento_1_a_3_meses;
        DROP TABLE IF EXISTS assinantes_cadastrados;

        CREATE TABLE assinantes_cadastrados (
            cliente_id TEXT PRIMARY KEY,
            data_inicio TEXT NOT NULL,
            data_cancelamento TEXT,
            status TEXT NOT NULL
                CHECK (status IN ('ativo', 'inativo')),
            CHECK (
                (status = 'ativo' AND data_cancelamento IS NULL)
                OR
                (status = 'inativo' AND data_cancelamento IS NOT NULL)
            )
        );
    """)

    # Dados ficticios: nenhum cliente real.
    registros = [
        ("C001", "2026-01-10", None, "ativo"),
        ("C002", "2026-02-15", None, "ativo"),
        ("C003", "2026-03-05", None, "ativo"),
        ("C004", "2026-01-10", "2026-02-10", "inativo"),
        ("C005", "2026-01-15", "2026-04-15", "inativo"),
        ("C006", "2026-01-12", "2026-05-12", "inativo"),
        ("C007", "2026-02-01", "2026-02-20", "inativo"),
        ("C008", "2026-01-20", "2026-07-20", "inativo"),
    ]

    conexao.executemany(
        """
        INSERT INTO assinantes_cadastrados
        (cliente_id, data_inicio, data_cancelamento, status)
        VALUES (?, ?, ?, ?)
        """,
        registros,
    )

    conexao.commit()


def criar_bases_derivadas(conexao):
    """Documenta tres transformacoes por meio de VIEWs."""

    conexao.executescript("""
        CREATE VIEW vw_clientes_ativos AS
        SELECT
            cliente_id,
            data_inicio,
            status
        FROM assinantes_cadastrados
        WHERE status = 'ativo';

        CREATE VIEW vw_clientes_inativos AS
        SELECT
            cliente_id,
            data_inicio,
            data_cancelamento,
            status
        FROM assinantes_cadastrados
        WHERE status = 'inativo';

        CREATE VIEW vw_clientes_cancelamento_1_a_3_meses AS
        WITH duracoes AS (
            SELECT
                cliente_id,
                data_inicio,
                data_cancelamento,
                status,
                (
                    (
                        CAST(strftime('%Y', data_cancelamento) AS INTEGER)
                        - CAST(strftime('%Y', data_inicio) AS INTEGER)
                    ) * 12
                    +
                    (
                        CAST(strftime('%m', data_cancelamento) AS INTEGER)
                        - CAST(strftime('%m', data_inicio) AS INTEGER)
                    )
                    -
                    CASE
                        WHEN CAST(
                            strftime('%d', data_cancelamento) AS INTEGER
                        ) < CAST(
                            strftime('%d', data_inicio) AS INTEGER
                        )
                        THEN 1
                        ELSE 0
                    END
                ) AS meses_completos
            FROM assinantes_cadastrados
            WHERE status = 'inativo'
              AND date(data_cancelamento) >= date(data_inicio)
        )
        SELECT
            cliente_id,
            data_inicio,
            data_cancelamento,
            meses_completos
        FROM duracoes
        WHERE meses_completos BETWEEN 1 AND 3;
    """)

    conexao.commit()


def consultar(conexao, nome_view):
    nomes_permitidos = {
        "vw_clientes_ativos",
        "vw_clientes_inativos",
        "vw_clientes_cancelamento_1_a_3_meses",
    }

    if nome_view not in nomes_permitidos:
        raise ValueError("VIEW nao permitida")

    cursor = conexao.execute(
        f"SELECT * FROM {nome_view} ORDER BY cliente_id"
    )

    return [dict(linha) for linha in cursor.fetchall()]


def exportar_csv(caminho, registros, colunas):
    with caminho.open(
        "w", newline="", encoding="utf-8-sig"
    ) as arquivo:
        escritor = csv.DictWriter(
            arquivo, fieldnames=colunas
        )
        escritor.writeheader()
        escritor.writerows(registros)


def main():
    titulo("ALURA - AULA 03")
    print("COMO NASCEM NOVAS BASES")

    titulo("1. NECESSIDADE DE NEGOCIO")

    print("Empresa: avaliacao de ativos financeiros")
    print("Produto: newsletter mensal")
    print("Solicitante: equipe de marketing")
    print("Objetivo: identificar ex-assinantes de 1 a 3 meses")

    titulo("2. ORIGEM DOS DADOS")

    origem = "assinantes_cadastrados"

    print("Base original:", origem)
    print("Conteudo: clientes e historico de assinatura")
    print("Dados: ficticios")

    with sqlite3.connect(BANCO) as conexao:
        conexao.row_factory = sqlite3.Row

        criar_origem(conexao)
        criar_bases_derivadas(conexao)

        total_origem = conexao.execute(
            "SELECT COUNT(*) FROM assinantes_cadastrados"
        ).fetchone()[0]

        titulo("3. TRANSFORMACOES")

        destinos = {
            "clientes_ativos": "vw_clientes_ativos",
            "clientes_inativos": "vw_clientes_inativos",
            "cancelamento_1_a_3_meses":
                "vw_clientes_cancelamento_1_a_3_meses",
        }

        bases = {}

        for identificador, nome_view in destinos.items():
            registros = consultar(conexao, nome_view)
            bases[identificador] = registros

            print(f"\nBASE: {identificador}")
            print(f"VIEW: {nome_view}")
            print(f"Quantidade de registros: {len(registros)}")

            for registro in registros:
                print(registro)

    titulo("4. EXPORTANDO NOVAS BASES")

    arquivos_csv = {
        "clientes_ativos":
            RESULTADOS / "aula03_clientes_ativos.csv",
        "clientes_inativos":
            RESULTADOS / "aula03_clientes_inativos.csv",
        "cancelamento_1_a_3_meses":
            RESULTADOS / "aula03_cancelamento_1_a_3_meses.csv",
    }

    colunas = {
        "clientes_ativos": [
            "cliente_id", "data_inicio", "status"
        ],
        "clientes_inativos": [
            "cliente_id", "data_inicio",
            "data_cancelamento", "status"
        ],
        "cancelamento_1_a_3_meses": [
            "cliente_id", "data_inicio",
            "data_cancelamento", "meses_completos"
        ],
    }

    for identificador, caminho in arquivos_csv.items():
        exportar_csv(
            caminho,
            bases[identificador],
            colunas[identificador],
        )
        print(f"Arquivo criado: {caminho.name}")

    titulo("5. DOCUMENTANDO A LINHAGEM")

    linhagem = {
        "aula": 3,
        "titulo": "Como nascem novas bases",
        "origem": {
            "nome": origem,
            "tipo": "tabela SQLite",
            "registros": total_origem,
        },
        "transformacoes": [
            {
                "nome": "filtrar_ativos",
                "criterio": "status = ativo",
                "destino": destinos["clientes_ativos"],
            },
            {
                "nome": "filtrar_inativos",
                "criterio": "status = inativo",
                "destino": destinos["clientes_inativos"],
            },
            {
                "nome": "filtrar_cancelamentos_curtos",
                "criterio": (
                    "assinantes cancelados apos "
                    "1 a 3 meses completos de calendario"
                ),
                "destino": destinos["cancelamento_1_a_3_meses"],
            },
        ],
        "observacoes": [
            "Dados inteiramente ficticios.",
            "Meses completos definidos por diferenca de "
            "ano e mes, ajustada pelo dia do mes.",
            "As tres bases derivadas sao VIEWs SQL, "
            "exportadas tambem para CSV.",
            "A aula nao define uma regra operacional "
            "para calculo do periodo; a utilizada aqui "
            "e uma escolha didatica.",
        ],
    }

    arquivo_json = RESULTADOS / "aula03_linhagem_newsletter.json"

    arquivo_json.write_text(
        json.dumps(
            linhagem,
            indent=4,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print("Linhagem:", arquivo_json.name)

    titulo("6. TESTES AUTOMATIZADOS")

    assert total_origem == 8
    assert len(bases["clientes_ativos"]) == 3
    assert len(bases["clientes_inativos"]) == 5
    assert len(bases["cancelamento_1_a_3_meses"]) == 2

    ids_curta_duracao = {
        item["cliente_id"]
        for item in bases["cancelamento_1_a_3_meses"]
    }

    assert ids_curta_duracao == {"C004", "C005"}

    assert sorted(
        item["meses_completos"]
        for item in bases["cancelamento_1_a_3_meses"]
    ) == [1, 3]

    ids_ativos = {
        item["cliente_id"]
        for item in bases["clientes_ativos"]
    }

    ids_inativos = {
        item["cliente_id"]
        for item in bases["clientes_inativos"]
    }

    assert not ids_ativos.intersection(ids_inativos)
    assert len(ids_ativos.union(ids_inativos)) == total_origem

    assert all(
        caminho.is_file()
        for caminho in arquivos_csv.values()
    )

    assert arquivo_json.is_file()
    assert BANCO.is_file()

    linhagem_salva = json.loads(
        arquivo_json.read_text(encoding="utf-8")
    )

    assert len(linhagem_salva["transformacoes"]) == 3

    titulo("RESULTADO FINAL")

    print("Bases de origem: 1")
    print("Novas bases derivadas: 3")
    print("Clientes cadastrados: 8")
    print("Clientes ativos: 3")
    print("Clientes inativos: 5")
    print("Cancelamentos entre 1 e 3 meses: 2")
    print("Arquivos CSV: 3")
    print("Arquivo JSON de linhagem: 1")
    print("Banco SQLite: 1")
    print("Todos os testes passaram.")
    print("Aula 03 executada com sucesso.")


if __name__ == "__main__":
    main()