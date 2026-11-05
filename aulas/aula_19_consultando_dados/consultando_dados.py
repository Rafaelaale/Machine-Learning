from pathlib import Path
import hashlib
import json

import duckdb
import pandas as pd

BASE = Path(r"F:\AWS-CIENCIA-DE-DADOS-SEGURANCA-CUSTOS")
AULA = BASE / "aulas" / "aula_19_consultando_dados"
RESULTADOS = BASE / "resultados"
SAIDAS = RESULTADOS / "aula_19_consultas"

CATALOGO = RESULTADOS / "aula_17_processed_data_catalog.json"
SQL_FILE = AULA / "consultas_athena.sql"
RELATORIO = RESULTADOS / "aula_19_analises_sql.json"


def validar(condicao, mensagem):
    if not condicao:
        raise AssertionError(mensagem)
    print("APROVADO:", mensagem)


def main():
    print("===== AULA 19 - CONSULTAS SQL =====")
    print("Ferramenta: DuckDB local")
    print("AWS: nenhum servico utilizado")

    AULA.mkdir(parents=True, exist_ok=True)
    SAIDAS.mkdir(parents=True, exist_ok=True)

    print("\n===== LENDO CATALOGO DA AULA 17 =====")

    if not CATALOGO.exists():
        raise FileNotFoundError(CATALOGO)

    catalogo = json.loads(
        CATALOGO.read_text(encoding="utf-8-sig")
    )

    validar(
        catalogo["database"] == "processed_data"
        and catalogo["tabela"] == "glue_heart",
        "Catalogo processed_data.glue_heart"
    )

    arquivo = Path(catalogo["localizacao_local"])

    validar(
        arquivo.is_file(),
        "Arquivo Parquet encontrado"
    )

    hash_atual = hashlib.sha256(
        arquivo.read_bytes()
    ).hexdigest()

    validar(
        hash_atual == catalogo["sha256"],
        "Integridade do Parquet confirmada"
    )

    caminho_sql = arquivo.as_posix().replace("'", "''")

    conexao = duckdb.connect(database=":memory:")

    criacao_view = (
        "CREATE VIEW glue_heart AS "
        f"SELECT * FROM read_parquet('{caminho_sql}')"
    )

    conexao.execute(criacao_view)

    print("Tabela SQL: glue_heart")
    print("Origem:", arquivo)

    print("\n===== PREPARANDO CONSULTAS =====")

    consultas = {
        "01_primeiros_registros": """
SELECT *
FROM glue_heart
LIMIT 10
""",
        "02_doenca_por_sexo": """
SELECT
    Sex,
    HeartDisease,
    COUNT(*) AS total_pacientes
FROM glue_heart
GROUP BY Sex, HeartDisease
ORDER BY Sex, HeartDisease
""",
        "03_colesterol_por_classe": """
SELECT
    HeartDisease,
    ROUND(AVG(Cholesterol), 2) AS media_colesterol,
    MAX(Cholesterol) AS max_colesterol,
    COUNT(*) AS registros_validos
FROM glue_heart
WHERE Cholesterol > 0
GROUP BY HeartDisease
ORDER BY HeartDisease
""",
        "04_dor_no_peito": """
SELECT
    ChestPainType,
    HeartDisease,
    COUNT(*) AS total_pacientes
FROM glue_heart
WHERE Cholesterol > 0
GROUP BY ChestPainType, HeartDisease
ORDER BY ChestPainType, HeartDisease
""",
        "05_percentual_por_sexo": """
SELECT
    Sex,
    COUNT(*) AS total_grupo,
    SUM(
        CASE WHEN HeartDisease = 1
        THEN 1 ELSE 0 END
    ) AS casos_positivos,
    ROUND(
        100.0 * SUM(
            CASE WHEN HeartDisease = 1
            THEN 1 ELSE 0 END
        ) / NULLIF(COUNT(*), 0),
        2
    ) AS percentual_positivo
FROM glue_heart
GROUP BY Sex
ORDER BY Sex
""",
        "06_faixas_etarias": """
SELECT
    CASE
        WHEN Age < 40 THEN 'Abaixo de 40'
        WHEN Age < 50 THEN '40 a 49'
        WHEN Age < 60 THEN '50 a 59'
        ELSE '60 ou mais'
    END AS faixa_etaria,
    COUNT(*) AS total_pacientes,
    SUM(
        CASE WHEN HeartDisease = 1
        THEN 1 ELSE 0 END
    ) AS casos_positivos,
    ROUND(
        100.0 * AVG(
            CASE WHEN HeartDisease = 1
            THEN 1.0 ELSE 0.0 END
        ), 2
    ) AS percentual_positivo
FROM glue_heart
GROUP BY 1
ORDER BY
    CASE faixa_etaria
        WHEN 'Abaixo de 40' THEN 1
        WHEN '40 a 49' THEN 2
        WHEN '50 a 59' THEN 3
        ELSE 4
    END
""",
        "07_pressao_por_classe": """
SELECT
    HeartDisease,
    COUNT(*) AS registros_validos,
    ROUND(AVG(RestingBP), 2) AS media_pressao,
    MIN(RestingBP) AS minima_pressao,
    MAX(RestingBP) AS maxima_pressao
FROM glue_heart
WHERE RestingBP > 0
GROUP BY HeartDisease
ORDER BY HeartDisease
""",
        "08_qualidade_dados": """
SELECT
    COUNT(*) AS total_registros,
    SUM(
        CASE WHEN Cholesterol = 0
        THEN 1 ELSE 0 END
    ) AS colesterol_zero,
    SUM(
        CASE WHEN RestingBP = 0
        THEN 1 ELSE 0 END
    ) AS pressao_zero,
    COUNT(*) - COUNT(DISTINCT (
        Age, Sex, ChestPainType,
        RestingBP, Cholesterol,
        FastingBS, HeartDisease
    )) AS repeticoes_sete_colunas
FROM glue_heart
"""
    }

    texto_sql = (
        "-- AULA 19 - CONSULTAS SQL COM DUCKDB\n"
        "-- Equivalente local dos exercicios Athena\n"
        "-- View criada a partir do catalogo local\n\n"
        + criacao_view + ";\n\n"
    )

    saidas = {}

    print("\n===== EXECUTANDO CONSULTAS =====")

    for nome, consulta in consultas.items():
        print(f"\n===== {nome.upper()} =====")

        dataframe = conexao.execute(consulta).df()

        print(dataframe.to_string(index=False))

        caminho_csv = SAIDAS / f"{nome}.csv"

        dataframe.to_csv(
            caminho_csv,
            index=False,
            encoding="utf-8-sig"
        )

        saidas[nome] = json.loads(
            dataframe.to_json(orient="records")
        )

        texto_sql += (
            f"-- {nome}\n"
            + consulta.strip()
            + ";\n\n"
        )

        print("CSV:", caminho_csv)

    SQL_FILE.write_text(
        texto_sql,
        encoding="utf-8"
    )

    print("\n===== VALIDANDO RESULTADOS =====")

    total = conexao.execute(
        "SELECT COUNT(*) FROM glue_heart"
    ).fetchone()[0]

    validar(
        total == 918,
        "918 registros consultados"
    )

    validar(
        len(saidas["01_primeiros_registros"]) == 10,
        "Consulta LIMIT 10 funcionando"
    )

    validar(
        sum(
            linha["total_pacientes"]
            for linha in saidas["02_doenca_por_sexo"]
        ) == 918,
        "Distribuicao por sexo totaliza 918"
    )

    validar(
        sum(
            linha["registros_validos"]
            for linha in saidas["03_colesterol_por_classe"]
        ) == 746,
        "Analise de colesterol excluiu 172 zeros"
    )

    validar(
        sum(
            linha["total_pacientes"]
            for linha in saidas["04_dor_no_peito"]
        ) == 746,
        "Analise de dor aplicou filtro de colesterol"
    )

    validar(
        sum(
            linha["total_grupo"]
            for linha in saidas["05_percentual_por_sexo"]
        ) == 918,
        "Percentuais por sexo calculados"
    )

    validar(
        sum(
            linha["total_pacientes"]
            for linha in saidas["06_faixas_etarias"]
        ) == 918,
        "Faixas etarias cobrem todos os registros"
    )

    validar(
        sum(
            linha["registros_validos"]
            for linha in saidas["07_pressao_por_classe"]
        ) == 917,
        "Analise de pressao excluiu valor zero"
    )

    qualidade = saidas["08_qualidade_dados"][0]

    validar(
        qualidade["colesterol_zero"] == 172
        and qualidade["pressao_zero"] == 1
        and qualidade["repeticoes_sete_colunas"] == 7,
        "Qualidade dos dados consistente com Aula 18"
    )

    validar(
        SQL_FILE.is_file()
        and len(list(SAIDAS.glob("*.csv"))) == 8,
        "Arquivo SQL e oito CSVs criados"
    )

    relatorio = {
        "aula": 19,
        "ferramenta": "DuckDB",
        "tabela": "processed_data.glue_heart",
        "registros": int(total),
        "consultas_executadas": len(consultas),
        "resultados": saidas,
        "observacao": (
            "Analise descritiva de dataset historico. "
            "Associacoes nao demonstram causalidade "
            "nem fornecem estimativas clinicas individuais."
        ),
        "recursos_aws_criados": 0
    }

    RELATORIO.write_text(
        json.dumps(
            relatorio,
            indent=4,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )

    validar(
        RELATORIO.is_file(),
        "Relatorio JSON criado"
    )

    conexao.close()

    print("\n===== VALIDACAO FINAL =====")
    print("TESTES: 11/11 APROVADOS")
    print("CONSULTAS SQL: 8")
    print("REGISTROS: 918")
    print("ARQUIVO SQL:", SQL_FILE)
    print("RESULTADOS CSV:", SAIDAS)
    print("RELATORIO:", RELATORIO)
    print("CUSTO AWS: ZERO")
    print("AULA 19 - CONSULTAS CONCLUIDAS")


if __name__ == "__main__":
    main()
