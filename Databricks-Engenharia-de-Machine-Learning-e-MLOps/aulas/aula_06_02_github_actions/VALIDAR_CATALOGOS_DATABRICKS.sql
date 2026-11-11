-- Consultas equivalentes as apresentadas pela Alura.
-- Executar SOMENTE no Databricks SQL Editor,
-- caso os catalogos remotos sejam criados.

SELECT *
FROM stage.default.usuarios_bronze;

SELECT *
FROM prod.default.usuarios_bronze;

-- Nesta adaptacao os catalogos foram simulados
-- como tabelas isoladas dentro de um banco SQLite.