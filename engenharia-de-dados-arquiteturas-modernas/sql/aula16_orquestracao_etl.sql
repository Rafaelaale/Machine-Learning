PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS dim_acesso (
    acesso_sk INTEGER PRIMARY KEY AUTOINCREMENT,
    canal TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS dim_aging (
    aging_sk INTEGER PRIMARY KEY AUTOINCREMENT,
    situacao TEXT NOT NULL,
    faixa TEXT NOT NULL,
    inicio_dias INTEGER NOT NULL,
    fim_dias INTEGER,
    UNIQUE(situacao, faixa)
);

CREATE TABLE IF NOT EXISTS fato_vendas (
    pedido_id_origem INTEGER NOT NULL,
    produto_id_origem INTEGER NOT NULL,
    cliente_sk INTEGER NOT NULL,
    produto_sk INTEGER NOT NULL,
    tempo_sk INTEGER NOT NULL,
    promocao_sk INTEGER,
    acesso_sk INTEGER,
    quantidade INTEGER NOT NULL CHECK(quantidade > 0),
    preco_unitario_centavos INTEGER NOT NULL,
    valor_total_centavos INTEGER NOT NULL,

    PRIMARY KEY(pedido_id_origem, produto_id_origem),

    FOREIGN KEY(cliente_sk) REFERENCES dim_cliente(cliente_sk),
    FOREIGN KEY(produto_sk) REFERENCES dim_produto(produto_sk),
    FOREIGN KEY(tempo_sk) REFERENCES dim_tempo(tempo_sk),
    FOREIGN KEY(promocao_sk) REFERENCES dim_promocao(promocao_sk),
    FOREIGN KEY(acesso_sk) REFERENCES dim_acesso(acesso_sk)
);

CREATE TABLE IF NOT EXISTS fato_inventario (
    movimento_id_origem INTEGER PRIMARY KEY,
    produto_sk INTEGER NOT NULL,
    tempo_sk INTEGER NOT NULL,
    saida_estoque INTEGER NOT NULL CHECK(saida_estoque < 0),

    FOREIGN KEY(produto_sk) REFERENCES dim_produto(produto_sk),
    FOREIGN KEY(tempo_sk) REFERENCES dim_tempo(tempo_sk)
);

CREATE TABLE IF NOT EXISTS fato_financeiro (
    cliente_sk INTEGER NOT NULL,
    aging_sk INTEGER NOT NULL,
    tempo_sk INTEGER NOT NULL,
    valor_receber_centavos INTEGER NOT NULL,
    valor_atraso_centavos INTEGER NOT NULL,

    PRIMARY KEY(cliente_sk, aging_sk, tempo_sk),

    FOREIGN KEY(cliente_sk) REFERENCES dim_cliente(cliente_sk),
    FOREIGN KEY(aging_sk) REFERENCES dim_aging(aging_sk),
    FOREIGN KEY(tempo_sk) REFERENCES dim_tempo(tempo_sk)
);

CREATE TABLE IF NOT EXISTS etl_execucoes (
    execucao_id INTEGER PRIMARY KEY AUTOINCREMENT,
    inicio TEXT NOT NULL,
    fim TEXT NOT NULL,
    executado_em TEXT NOT NULL,
    vendas_carregadas INTEGER NOT NULL,
    movimentos_carregados INTEGER NOT NULL,
    faturamento_centavos INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_a16_vendas_tempo
    ON fato_vendas(tempo_sk);

CREATE INDEX IF NOT EXISTS idx_a16_inventario_tempo
    ON fato_inventario(tempo_sk);
