-- Aula 18 - Consultas no DuckDB local
-- Arquivo Parquet da camada processed

CREATE OR REPLACE VIEW glue_heart AS
SELECT * FROM read_parquet('F:/AWS-CIENCIA-DE-DADOS-SEGURANCA-CUSTOS/s3_local/hospital-dados/processed/glue_heart/heart_processed.parquet');

-- total_registros
SELECT COUNT(*) AS total
            FROM glue_heart;

-- distribuicao_alvo
SELECT
                HeartDisease,
                COUNT(*) AS quantidade
            FROM glue_heart
            GROUP BY HeartDisease
            ORDER BY HeartDisease;

-- colesterol_zero
SELECT COUNT(*) AS quantidade
            FROM glue_heart
            WHERE Cholesterol = 0;

-- pressao_zero
SELECT COUNT(*) AS quantidade
            FROM glue_heart
            WHERE RestingBP = 0;

-- registros_iguais
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
            ) AS grupos;

