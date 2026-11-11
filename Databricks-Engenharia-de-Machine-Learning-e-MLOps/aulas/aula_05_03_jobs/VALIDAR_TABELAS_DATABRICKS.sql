-- EXECUTAR NO DATABRICKS SQL EDITOR.
-- NAO EXECUTAR NO POWERSHELL.

-- A tabela de treinamento deve existir antes do Job.
SELECT COUNT(*) AS total_treino
FROM workspace.default.base_treinamento_modelo_aprimorado;

-- Maio completo: 01/05 a 31/05.
-- A data final 20260601 e exclusiva.
SELECT
    dia_prtc,
    COUNT(*) AS registros
FROM workspace.default.base_tabela_prod_aprimorada
WHERE dia_prtc >= '20260501'
  AND dia_prtc < '20260601'
GROUP BY dia_prtc
ORDER BY dia_prtc;

-- Verificacao do monitoramento.
SELECT *
FROM workspace.default.log_monitoramento_drift_aprimorado
WHERE periodo_inicio = '20260501'
  AND periodo_fim = '20260601'
ORDER BY timestamp_execucao DESC;