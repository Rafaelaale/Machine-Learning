-- Aula 02 - Consultas analiticas Minishop
-- Executar sobre minishop_olap.db

-- 1. Faturamento total
SELECT SUM(valor_centavos) / 100.0 AS faturamento_reais
FROM fato_vendas;

-- 2. Quantidade de pedidos
SELECT COUNT(DISTINCT pedido_id) AS pedidos
FROM fato_vendas;

-- 3. Ticket medio
SELECT
    ROUND(
        SUM(valor_centavos) * 1.0
        / NULLIF(COUNT(DISTINCT pedido_id), 0)
        / 100,
        2
    ) AS ticket_medio_reais
FROM fato_vendas;

-- 4. Faturamento por produto
SELECT
    p.nome,
    SUM(f.quantidade) AS unidades,
    SUM(f.valor_centavos) / 100.0 AS receita_reais
FROM fato_vendas AS f
JOIN dim_produtos AS p
    ON p.produto_id = f.produto_id
GROUP BY p.produto_id, p.nome
ORDER BY receita_reais DESC;

-- 5. Evolucao mensal de vendas
SELECT
    t.ano,
    t.mes,
    COUNT(DISTINCT f.pedido_id) AS pedidos,
    SUM(f.valor_centavos) / 100.0 AS receita_reais
FROM fato_vendas AS f
JOIN dim_tempo AS t
    ON t.data = f.data
GROUP BY t.ano, t.mes
ORDER BY t.ano, t.mes;
