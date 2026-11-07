PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS etl_cargas (
    carga_id INTEGER PRIMARY KEY AUTOINCREMENT,
    executado_em TEXT NOT NULL,
    tipo TEXT NOT NULL
        CHECK (tipo IN ('inicial', 'incremental')),
    origem_linhas INTEGER NOT NULL,
    novos_fatos INTEGER NOT NULL,
    novas_versoes INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_cliente (
    cliente_sk INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id_origem INTEGER NOT NULL,
    nome TEXT NOT NULL,
    versao INTEGER NOT NULL CHECK (versao >= 1),
    valido_desde TEXT NOT NULL,
    valido_ate TEXT,
    ativo INTEGER NOT NULL CHECK (ativo IN (0, 1)),
    UNIQUE (cliente_id_origem, versao)
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_cliente_ativo
    ON dim_cliente(cliente_id_origem)
    WHERE ativo = 1;

CREATE TABLE IF NOT EXISTS dim_produto (
    produto_sk INTEGER PRIMARY KEY AUTOINCREMENT,
    produto_id_origem INTEGER NOT NULL,
    nome TEXT NOT NULL,
    categoria TEXT NOT NULL,
    versao INTEGER NOT NULL CHECK (versao >= 1),
    valido_desde TEXT NOT NULL,
    valido_ate TEXT,
    ativo INTEGER NOT NULL CHECK (ativo IN (0, 1)),
    UNIQUE (produto_id_origem, versao)
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_produto_ativo
    ON dim_produto(produto_id_origem)
    WHERE ativo = 1;

CREATE TABLE IF NOT EXISTS dim_tempo (
    tempo_sk INTEGER PRIMARY KEY AUTOINCREMENT,
    data TEXT NOT NULL UNIQUE,
    ano INTEGER NOT NULL,
    mes INTEGER NOT NULL,
    dia INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS fato_vendas (
    fato_id INTEGER PRIMARY KEY AUTOINCREMENT,
    pedido_id_origem INTEGER NOT NULL,
    produto_id_origem INTEGER NOT NULL,
    cliente_sk INTEGER NOT NULL,
    produto_sk INTEGER NOT NULL,
    tempo_sk INTEGER NOT NULL,
    quantidade INTEGER NOT NULL CHECK (quantidade > 0),
    valor_centavos INTEGER NOT NULL CHECK (valor_centavos >= 0),

    UNIQUE (pedido_id_origem, produto_id_origem),

    FOREIGN KEY (cliente_sk)
        REFERENCES dim_cliente(cliente_sk),

    FOREIGN KEY (produto_sk)
        REFERENCES dim_produto(produto_sk),

    FOREIGN KEY (tempo_sk)
        REFERENCES dim_tempo(tempo_sk)
);

CREATE INDEX IF NOT EXISTS idx_fato_tempo
    ON fato_vendas(tempo_sk);

CREATE INDEX IF NOT EXISTS idx_fato_cliente
    ON fato_vendas(cliente_sk);

CREATE INDEX IF NOT EXISTS idx_fato_produto
    ON fato_vendas(produto_sk);
