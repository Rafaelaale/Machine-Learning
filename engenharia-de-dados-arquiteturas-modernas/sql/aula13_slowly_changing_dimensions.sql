PRAGMA foreign_keys = ON;

-- SCD TIPO 1: conserva uma linha por cliente.
CREATE TABLE IF NOT EXISTS cliente_scd1 (
    cliente_sk INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo_natural TEXT NOT NULL UNIQUE,
    cidade TEXT NOT NULL
);

-- SCD TIPO 2: permite varias versoes por codigo natural.
-- Inicio incluso; fim exclusivo. NULL = sem fim definido.
CREATE TABLE IF NOT EXISTS cliente_scd2 (
    cliente_sk INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo_natural TEXT NOT NULL,
    cidade TEXT NOT NULL,
    inicio TEXT NOT NULL,
    fim TEXT,
    atual INTEGER NOT NULL CHECK (atual IN (0, 1)),
    UNIQUE (codigo_natural, inicio),
    CHECK (fim IS NULL OR fim > inicio),
    CHECK (
        (atual = 1 AND fim IS NULL)
        OR (atual = 0 AND fim IS NOT NULL)
    )
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_scd2_atual
    ON cliente_scd2(codigo_natural)
    WHERE atual = 1;

CREATE INDEX IF NOT EXISTS idx_scd2_vigencia
    ON cliente_scd2(codigo_natural, inicio, fim);

-- Fatos SCD1: historico associado ao atributo sobrescrito.
CREATE TABLE IF NOT EXISTS vendas_scd1 (
    evento_id TEXT PRIMARY KEY,
    cliente_sk INTEGER NOT NULL,
    data_venda TEXT NOT NULL,
    valor_centavos INTEGER NOT NULL CHECK (valor_centavos >= 0),
    FOREIGN KEY (cliente_sk) REFERENCES cliente_scd1(cliente_sk)
);

-- Fatos SCD2: SK escolhida pela vigencia da data da venda.
CREATE TABLE IF NOT EXISTS vendas_scd2 (
    evento_id TEXT PRIMARY KEY,
    cliente_sk INTEGER NOT NULL,
    data_venda TEXT NOT NULL,
    valor_centavos INTEGER NOT NULL CHECK (valor_centavos >= 0),
    FOREIGN KEY (cliente_sk) REFERENCES cliente_scd2(cliente_sk)
);
