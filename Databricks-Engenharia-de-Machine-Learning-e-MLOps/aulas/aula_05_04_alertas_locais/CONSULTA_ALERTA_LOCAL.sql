-- Consulta equivalente no SQLite local.
SELECT COUNT(*) AS total_drift
FROM log_monitoramento_drift
WHERE drift_detectado = 1
  AND periodo_inicio = '20260501'
  AND periodo_fim = '20260601';