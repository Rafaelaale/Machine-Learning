-- Referencia da aula Databricks.
-- Executar somente no SQL Editor do Databricks,
-- caso o projeto seja publicado futuramente.

SELECT COUNT(*) AS total_drift
FROM workspace.default.log_monitoramento_drift_aprimorado
WHERE drift_detectado = TRUE
  AND periodo_inicio = '20260501'
  AND periodo_fim = '20260601';

-- Condicao do alerta: total_drift > 0.
-- A data final e exclusiva no processamento.