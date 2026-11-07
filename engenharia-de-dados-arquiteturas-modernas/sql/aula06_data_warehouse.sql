PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS lotes_carga (
    lote_id INTEGER PRIMARY KEY,
    carregado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    assinatura TEXT NOT NULL UNIQUE,
    quantidade_linhas INTEGER NOT NULL,
    total_centavos INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_clientes (
    lote_id INTEGER NOT NULL,
    cliente_id INTEGER NOT NULL,
    nome TEXT NOT NULL,
    PRIMARY KEY (lote_id, cliente_id),
    FOREIGN KEY (lote_id)
        REFERENCES lotes_carga(lote_id)
);

CREATE TABLE IF NOT EXISTS dim_produtos (
    lote_id INTEGER NOT NULL,
    produto_id INTEGER NOT NULL,
    nome TEXT NOT NULL,
    categoria TEXT NOT NULL,
    PRIMARY KEY (lote_id, produto_id),
    FOREIGN KEY (lote_id)
        REFERENCES lotes_carga(lote_id)
);

CREATE TABLE IF NOT EXISTS dim_tempo (
    data TEXT PRIMARY KEY,
    ano INTEGER NOT NULL,
    mes INTEGER NOT NULL,
    dia INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS fato_vendas (
    lote_id INTEGER NOT NULL,
    pedido_id INTEGER NOT NULL,
    produto_id INTEGER NOT NULL,
    cliente_id INTEGER NOT NULL,
    data TEXT NOT NULL,
    quantidade INTEGER NOT NULL CHECK (quantidade > 0),
    valor_centavos INTEGER NOT NULL CHECK (valor_centavos >= 0),

    PRIMARY KEY (lote_id, pedido_id, produto_id),

    FOREIGN KEY (lote_id)
        REFERENCES lotes_carga(lote_id),

    FOREIGN KEY (lote_id, cliente_id)
        REFERENCES dim_clientes(lote_id, cliente_id),

    FOREIGN KEY (lote_id, produto_id)
        REFERENCES dim_produtos(lote_id, produto_id),

    FOREIGN KEY (data)
        REFERENCES dim_tempo(data)
);

CREATE INDEX IF NOT EXISTS idx_dw_vendas_data
    ON fato_vendas(data);

CREATE INDEX IF NOT EXISTS idx_dw_vendas_cliente
    ON fato_vendas(lote_id, cliente_id);
