from pathlib import Path
import hashlib
import json

import duckdb
import pandas as pd

BASE = Path(r"F:\AWS-CIENCIA-DE-DADOS-SEGURANCA-CUSTOS")
AULA = BASE / "aulas" / "aula_18_introducao_athena"
RESULTADOS = BASE / "resultados"

CATALOGO = RESULTADOS / "aula_17_processed_data_catalog.json"
RELATORIO = RESULTADOS / "aula_18_athena.json"
ARQUIVO_SQL = AULA / "consultas_athena_local.sql"

testes = 0


def validar(condicao, descricao):
    global testes

    if not condicao:
        raise AssertionError(descricao)

    testes += 1
    print("APROVADO:", descricao)


def main():
    print("===== AULA 18 - AMAZON ATHENA =====")
    print("Alternativa local: DuckDB")
    print("Custo AWS: ZERO")

    print("\n===== LENDO GLUE DATA CATALOG LOCAL =====")

    validar(CATALOGO.is_file(), "Catalogo encontrado")

    catalogo = json.loads(
        CATALOGO.read_text(encoding="utf-8-sig")
    )

    validar(
        catalogo["database"] == "processed_data"
        and catalogo["tabela"] == "glue_heart",
        "Database e tabela corretos"
    )

    parquet = Path(catalogo["localizacao_local"])

    validar(parquet.is_file(), "Arquivo Parquet encontrado")

    hash_atual = hashlib.sha256(parquet.read_bytes()).hexdigest()

    validar(
        hash_atual == catalogo["sha256"],
        "Integridade do Parquet confirmada"
    )

    print("Database: processed_data")
    print("Tabela: glue_heart")
    print("Arquivo:", parquet)

    print("\n===== CONECTANDO AO DUCKDB =====")

    con = duckdb.connect(database=":memory:")

    # O caminho vem do nosso catalogo local validado.
    caminho_sql = parquet.as_posix().replace("'", "''")

    con.execute(
        "CREATE VIEW glue_heart AS "
        f"SELECT * FROM read_parquet('{caminho_sql}')"
    )

    print("View SQL criada: glue_heart")

    consultas = {
        "total_registros": """
            SELECT COUNT(*) AS total
            FROM glue_heart
        """,
        "distribuicao_alvo": """
            SELECT
                HeartDisease,
                COUNT(*) AS quantidade
            FROM glue_heart
            GROUP BY HeartDisease
            ORDER BY HeartDisease
        """,
        "colesterol_zero": """
            SELECT COUNT(*) AS quantidade
            FROM glue_heart
            WHERE Cholesterol = 0
        """,
        "pressao_zero": """
            SELECT COUNT(*) AS quantidade
            FROM glue_heart
            WHERE RestingBP = 0
        """,
        "registros_iguais": """
            SELECT
                COALESCE(SUM(quantidade - 1), 0)
                    AS repeticoes
            FROM (
                SELECT
                    Age,
                    Sex,
                    ChestPainType,
                    RestingBP,
                    Cholesterol,
                    FastingBS,
                    HeartDisease,
                    COUNT(*) AS quantidade
                FROM glue_heart
                GROUP BY ALL
                HAVING COUNT(*) > 1
            ) AS grupos
        """
    }

    saidas = {}

    print("\n===== EXECUTANDO CONSULTAS SQL =====")

    for nome, sql in consultas.items():
        print(f"\n--- {nome} ---")

        df = con.execute(sql).df()

        print(df.to_string(index=False))

        saidas[nome] = df.to_dict(orient="records")

    total = int(saidas["total_registros"][0]["total"])

    validar(total == 918, "918 registros consultados")

    distribuicao = {
        int(item["HeartDisease"]): int(item["quantidade"])
        for item in saidas["distribuicao_alvo"]
    }

    validar(
        distribuicao == {0: 410, 1: 508},
        "Distribuicao das classes confirmada"
    )

    zeros_colesterol = int(
        saidas["colesterol_zero"][0]["quantidade"]
    )

    zeros_pressao = int(
        saidas["pressao_zero"][0]["quantidade"]
    )

    validar(
        zeros_colesterol == 172 and zeros_pressao == 1,
        "Valores zero confirmados"
    )

    repeticoes = int(
        saidas["registros_iguais"][0]["repeticoes"]
    )

    print("\nRegistros repetidos nas 7 colunas:", repeticoes)

    print("\n===== SALVANDO CONSULTAS SQL =====")

    texto_sql = (
        "-- Aula 18 - Consultas no DuckDB local\n"
        "-- Arquivo Parquet da camada processed\n\n"
        "CREATE OR REPLACE VIEW glue_heart AS\n"
        f"SELECT * FROM read_parquet('{caminho_sql}');\n\n"
    )

    for nome, sql in consultas.items():
        texto_sql += (
            f"-- {nome}\n"
            + sql.strip()
            + ";\n\n"
        )

    ARQUIVO_SQL.write_text(
        texto_sql,
        encoding="utf-8"
    )

    print("SQL salvo:", ARQUIVO_SQL)

    relatorio = {
        "aula": 18,
        "ferramenta": "DuckDB",
        "servico_aws_real": False,
        "database_catalogado": "processed_data",
        "tabela": "glue_heart",
        "formato": "parquet",
        "registros": total,
        "colunas": len(con.execute(
            "DESCRIBE glue_heart"
        ).fetchall()),
        "distribuicao_alvo": distribuicao,
        "colesterol_zero": zeros_colesterol,
        "pressao_zero": zeros_pressao,
        "repeticoes_apos_selecao": repeticoes,
        "recursos_aws_criados": 0
    }

    RELATORIO.write_text(
        json.dumps(relatorio, indent=4, ensure_ascii=False),
        encoding="utf-8"
    )

    validar(
        ARQUIVO_SQL.is_file() and RELATORIO.is_file(),
        "Arquivos SQL e relatorio criados"
    )

    con.close()

    print("\n===== VALIDACAO FINAL =====")
    print(f"TESTES: {testes}/{testes} APROVADOS")
    print("REGISTROS:", total)
    print("COLUNAS:", relatorio["colunas"])
    print("SQL:", ARQUIVO_SQL)
    print("RELATORIO:", RELATORIO)
    print("CUSTO AWS: ZERO")
    print("AULA 18 - INTRODUCAO AO ATHENA CONCLUIDA")


if __name__ == "__main__":
    main()
