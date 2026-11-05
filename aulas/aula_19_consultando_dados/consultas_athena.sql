-- AULA 19 - CONSULTAS SQL COM DUCKDB
-- Equivalente local dos exercicios Athena
-- View criada a partir do catalogo local

CREATE VIEW glue_heart AS SELECT * FROM read_parquet('F:/AWS-CIENCIA-DE-DADOS-SEGURANCA-CUSTOS/s3_local/hospital-dados/processed/glue_heart/heart_processed.parquet');

-- 01_primeiros_registros
SELECT *
FROM glue_heart
LIMIT 10;

-- 02_doenca_por_sexo
SELECT
    Sex,
    HeartDisease,
    COUNT(*) AS total_pacientes
FROM glue_heart
GROUP BY Sex, HeartDisease
ORDER BY Sex, HeartDisease;

-- 03_colesterol_por_classe
SELECT
    HeartDisease,
    ROUND(AVG(Cholesterol), 2) AS media_colesterol,
    MAX(Cholesterol) AS max_colesterol,
    COUNT(*) AS registros_validos
FROM glue_heart
WHERE Cholesterol > 0
GROUP BY HeartDisease
ORDER BY HeartDisease;

-- 04_dor_no_peito
SELECT
    ChestPainType,
    HeartDisease,
    COUNT(*) AS total_pacientes
FROM glue_heart
WHERE Cholesterol > 0
GROUP BY ChestPainType, HeartDisease
ORDER BY ChestPainType, HeartDisease;

-- 05_percentual_por_sexo
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
ORDER BY Sex;

-- 06_faixas_etarias
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
    END;

-- 07_pressao_por_classe
SELECT
    HeartDisease,
    COUNT(*) AS registros_validos,
    ROUND(AVG(RestingBP), 2) AS media_pressao,
    MIN(RestingBP) AS minima_pressao,
    MAX(RestingBP) AS maxima_pressao
FROM glue_heart
WHERE RestingBP > 0
GROUP BY HeartDisease
ORDER BY HeartDisease;

-- 08_qualidade_dados
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
FROM glue_heart;

