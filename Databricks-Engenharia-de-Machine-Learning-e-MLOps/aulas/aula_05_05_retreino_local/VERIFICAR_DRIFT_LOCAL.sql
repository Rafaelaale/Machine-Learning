-- Consulta para o SQLite local.
-- Periodo de maio de 2026.

SELECT COUNT(*) AS total_drift
FROM log_monitoramento_drift
WHERE drift_detectado = 1
  AND periodo_inicio = '20260501'
  AND periodo_fim = '20260601';

-- Se total_drift > 0:
-- acionar re-treinamento.
-- Caso contrario, nao executar.