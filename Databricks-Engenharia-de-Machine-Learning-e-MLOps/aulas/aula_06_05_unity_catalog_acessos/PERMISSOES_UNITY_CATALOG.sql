-- AULA 6.5 - GERENCIAMENTO DE ACESSOS UNITY CATALOG
--
-- ARQUIVO DIDATICO. NAO EXECUTADO NO DATABRICKS.
--
-- Os objetos e principais sao exemplos hipoteticos.
-- Verifique grupos, usuarios, ownership e grants
-- existentes antes de executar qualquer comando.

-- ==================================================
-- 1. CONSULTAR PERMISSOES ATUAIS
-- ==================================================

SHOW GRANTS ON CATALOG prod;

SHOW GRANTS ON SCHEMA prod.gold;

SHOW GRANTS ON TABLE prod.gold.escoragem_propensao_compra;


-- ==================================================
-- 2. CONCEDER ACESSO DE LEITURA
-- ==================================================

-- Exemplos: executar somente apos revisao.
--
-- GRANT USE CATALOG
-- ON CATALOG prod
-- TO `grupo_leitura_prod`;
--
-- GRANT USE SCHEMA
-- ON SCHEMA prod.gold
-- TO `grupo_leitura_prod`;
--
-- GRANT SELECT
-- ON TABLE prod.gold.escoragem_propensao_compra
-- TO `grupo_leitura_prod`;


-- ==================================================
-- 3. REVOGAR MODIFICACAO DE DADOS
-- ==================================================

-- REVOKE MODIFY
-- ON TABLE prod.gold.escoragem_propensao_compra
-- FROM `grupo_leitura_prod`;


-- ==================================================
-- 4. REVOGAR CRIACAO DE TABELAS
-- ==================================================

-- REVOKE CREATE TABLE
-- ON SCHEMA prod.gold
-- FROM `grupo_leitura_prod`;


-- ==================================================
-- 5. REVOGAR LEITURA DE UMA TABELA
-- ==================================================

-- REVOKE SELECT
-- ON TABLE prod.gold.escoragem_propensao_compra
-- FROM `grupo_teste`;


-- ==================================================
-- 6. REVOGAR PRIVILEGIOS NO SCHEMA
-- ==================================================

-- REVOKE ALL PRIVILEGES
-- ON SCHEMA prod.gold
-- FROM `usuario_teste`;


-- ==================================================
-- 7. PRINCIPAL DEDICADO PARA A PIPELINE
-- ==================================================

-- Exemplo de permissao minima para escrita:
--
-- GRANT USE CATALOG
-- ON CATALOG prod
-- TO `svc_pipeline_prod`;
--
-- GRANT USE SCHEMA
-- ON SCHEMA prod.gold
-- TO `svc_pipeline_prod`;
--
-- GRANT CREATE TABLE
-- ON SCHEMA prod.gold
-- TO `svc_pipeline_prod`;
--
-- GRANT MODIFY
-- ON TABLE prod.gold.escoragem_propensao_compra
-- TO `svc_pipeline_prod`;


-- ==================================================
-- OBSERVACOES IMPORTANTES
-- ==================================================

-- 1. REVOKE em uma tabela nao remove automaticamente
--    privilegios herdados do schema ou catalogo.
--
-- 2. ALL PRIVILEGES nao inclui MANAGE.
--
-- 3. Ownership e MANAGE precisam de revisao propria.
--
-- 4. Operacoes de DROP dependem de propriedade e
--    capacidades administrativas apropriadas.
--
-- 5. Nunca revogue o acesso da propria identidade
--    da pipeline sem verificar suas dependencias.
--
-- 6. Este arquivo nao realiza nenhuma alteracao
--    enquanto permanecer apenas salvo no projeto.