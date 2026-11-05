from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json

import pandas as pd
import pyarrow.parquet as pq

BASE = Path(r"F:\AWS-CIENCIA-DE-DADOS-SEGURANCA-CUSTOS")

RAW = BASE / "s3_local" / "hospital-dados" / "raw"
PROCESSED = BASE / "s3_local" / "hospital-dados" / "processed"
RESULTADOS = BASE / "resultados"
AULA = BASE / "aulas" / "aula_17_visual_etl"

CATALOGO_RAW = RESULTADOS / "aula_16_raw_data_catalog.json"

DESTINO = PROCESSED / "glue_heart"
PARQUET = DESTINO / "heart_processed.parquet"

CATALOGO_PROCESSED = (
    RESULTADOS / "aula_17_processed_data_catalog.json"
)

RELATORIO = RESULTADOS / "aula_17_visual_etl.json"

COLUNAS = [
    "Age",
    "Sex",
    "ChestPainType",
    "RestingBP",
    "Cholesterol",
    "FastingBS",
    "HeartDisease"
]

REMOVIDAS = [
    "MaxHR",
    "ExerciseAngina",
    "RestingECG",
    "Oldpeak",
    "ST_Slope"
]


def sha256(caminho):
    return hashlib.sha256(
        caminho.read_bytes()
    ).hexdigest()


def validar(condicao, mensagem):
    if not condicao:
        raise AssertionError(mensagem)

    print("APROVADO:", mensagem)


def main():
    print("===== AULA 17 - AWS GLUE STUDIO LOCAL =====")
    print("Modo: ETL LOCAL - SEM AWS")

    DESTINO.mkdir(parents=True, exist_ok=True)
    RESULTADOS.mkdir(parents=True, exist_ok=True)

    print("\n===== CONSULTANDO DATA CATALOG =====")

    if not CATALOGO_RAW.is_file():
        raise FileNotFoundError(
            "Execute primeiro a Aula 16."
        )

    catalogo_raw = json.loads(
        CATALOGO_RAW.read_text(encoding="utf-8-sig")
    )

    validar(
        catalogo_raw["database"] == "raw-data",
        "Database raw-data encontrado"
    )

    tabela = catalogo_raw["tabelas"]["heart"]
    origem = Path(tabela["localizacao_local"])

    validar(
        origem.is_file(),
        "Fonte do catalogo encontrada"
    )

    validar(
        sha256(origem) == tabela["sha256"],
        "Arquivo bruto corresponde ao catalogo"
    )

    print("Tabela de origem: raw-data.heart")
    print("Fonte:", origem)

    print("\n===== EXTRACT - EXTRAINDO DADOS =====")

    df = pd.read_csv(origem)

    print("Registros originais:", len(df))
    print("Colunas originais:", len(df.columns))

    validar(
        df.shape == (918, 12),
        "Dataset original: 918 linhas e 12 colunas"
    )

    print("\n===== TRANSFORM - DROP DUPLICATES =====")

    duplicatas = int(df.duplicated().sum())

    df_sem_duplicatas = df.drop_duplicates().copy()

    print("Duplicatas removidas:", duplicatas)
    print("Registros restantes:", len(df_sem_duplicatas))

    print("\n===== TRANSFORM - CHANGE SCHEMA =====")

    validar(
        set(COLUNAS).issubset(df_sem_duplicatas.columns),
        "Todas as colunas selecionadas existem"
    )

    df_transformado = df_sem_duplicatas[COLUNAS].copy()

    print("Colunas mantidas:")
    for coluna in COLUNAS:
        print(" -", coluna)

    print("Colunas removidas:")
    for coluna in REMOVIDAS:
        print(" -", coluna)

    print("\n===== VALIDANDO TRANSFORMACAO =====")

    validar(
        len(df_transformado.columns) == 7,
        "Exatamente 7 colunas mantidas"
    )

    validar(
        len(df_transformado) == 918,
        "918 registros preservados"
    )

    validar(
        df_sem_duplicatas.duplicated().sum() == 0,
        "Duplicatas originais removidas corretamente"
    )

    duplicatas_projetadas = int(
        df_transformado.duplicated().sum()
    )

    print(
        "Linhas iguais apos selecionar 7 colunas:",
        duplicatas_projetadas
    )

    print(
        "Essas linhas serao preservadas, seguindo "
        "a ordem do fluxo ETL da Alura."
    )

    print("\n===== LOAD - SALVANDO PARQUET =====")

    df_transformado.to_parquet(
        PARQUET,
        engine="pyarrow",
        compression="snappy",
        index=False
    )

    print("Destino:", PARQUET)

    validar(
        PARQUET.is_file(),
        "Arquivo Parquet criado"
    )

    metadata = pq.read_metadata(PARQUET)
    codecs = {
        metadata.row_group(grupo)
        .column(coluna)
        .compression
        for grupo in range(metadata.num_row_groups)
        for coluna in range(metadata.num_columns)
    }

    validar(
        codecs == {"SNAPPY"},
        "Compressao Snappy confirmada"
    )

    print("\n===== VALIDANDO LEITURA DO PARQUET =====")

    df_recarregado = pd.read_parquet(PARQUET)

    pd.testing.assert_frame_equal(
        df_transformado.reset_index(drop=True),
        df_recarregado.reset_index(drop=True)
    )

    validar(
        df_recarregado.shape == (918, 7),
        "Parquet recarregado: 918 linhas e 7 colunas"
    )

    print("\n===== CATALOGANDO CAMADA PROCESSED =====")

    esquema = [
        {
            "nome": coluna,
            "tipo": str(df_recarregado[coluna].dtype),
            "nulos": int(df_recarregado[coluna].isna().sum())
        }
        for coluna in df_recarregado.columns
    ]

    catalogo = {
        "database": "processed_data",
        "tabela": "glue_heart",
        "formato": "parquet",
        "compressao": "snappy",
        "localizacao_local": str(PARQUET),
        "s3_uri_ilustrativa": (
            "s3://aws-alura-ds22-local/"
            "processed/glue_heart/heart_processed.parquet"
        ),
        "registros": len(df_recarregado),
        "colunas": esquema,
        "sha256": sha256(PARQUET),
        "catalogo_aws_real": False
    }

    CATALOGO_PROCESSED.write_text(
        json.dumps(
            catalogo,
            indent=4,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )

    print("Database: processed_data")
    print("Tabela: glue_heart")
    print("Formato: PARQUET")
    print("Compressao: SNAPPY")
    print("Colunas catalogadas:", len(esquema))

    print("\n===== RESUMO DE QUALIDADE =====")

    colesterol_zero = int(
        (df_recarregado["Cholesterol"] == 0).sum()
    )

    pressao_zero = int(
        (df_recarregado["RestingBP"] == 0).sum()
    )

    print("Colesterol igual a zero:", colesterol_zero)
    print("Pressao igual a zero:", pressao_zero)

    print(
        "Observacao: o ETL preserva esses valores, "
        "pois a aula nao solicita imputacao."
    )

    fluxo = {
        "job": "glue_alura",
        "modo": "simulacao_local",
        "nodes": [
            {
                "nome": "Data Catalog",
                "tipo": "source",
                "database": "raw-data",
                "table": "heart"
            },
            {
                "nome": "Drop Duplicates",
                "tipo": "transform"
            },
            {
                "nome": "Change Schema",
                "tipo": "transform",
                "manter": COLUNAS,
                "remover": REMOVIDAS
            },
            {
                "nome": "Parquet Snappy",
                "tipo": "target",
                "database": "processed_data",
                "table": "glue_heart"
            }
        ]
    }

    caminho_fluxo = AULA / "visual_etl_config.json"

    caminho_fluxo.write_text(
        json.dumps(fluxo, indent=4, ensure_ascii=False),
        encoding="utf-8"
    )

    relatorio = {
        "aula": 17,
        "job": "glue_alura",
        "executado_em_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "registros_origem": len(df),
        "duplicatas_removidas": duplicatas,
        "registros_destino": len(df_recarregado),
        "colunas_origem": len(df.columns),
        "colunas_destino": len(df_recarregado.columns),
        "colunas_mantidas": COLUNAS,
        "colunas_removidas": REMOVIDAS,
        "colesterol_zero_preservado": colesterol_zero,
        "pressao_zero_preservada": pressao_zero,
        "formato": "parquet",
        "compressao": "snappy",
        "database_destino": "processed_data",
        "tabela_destino": "glue_heart",
        "arquivo_destino": str(PARQUET),
        "parquet_sha256": sha256(PARQUET),
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
        CATALOGO_PROCESSED.is_file()
        and RELATORIO.is_file()
        and caminho_fluxo.is_file(),
        "Catalogo, relatorio e configuracao salvos"
    )

    print("\n===== VALIDACAO FINAL =====")
    print("TESTES: 12/12 APROVADOS")
    print("PARQUET:", PARQUET)
    print("CATALOGO:", CATALOGO_PROCESSED)
    print("RELATORIO:", RELATORIO)
    print("FLUXO:", caminho_fluxo)
    print("CUSTO AWS: ZERO")
    print("AULA 17 - VISUAL ETL CONCLUIDO")


if __name__ == "__main__":
    main()

