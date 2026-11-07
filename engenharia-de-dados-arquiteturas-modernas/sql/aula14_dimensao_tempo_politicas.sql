PRAGMA foreign_keys = ON;

CREATE TABLE dim_cliente (
    cliente_sk INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo_natural TEXT NOT NULL UNIQUE,
    nome TEXT NOT NULL
);

-- CHAVE SUBSTITUTA DETERMINISTICA: AAAAMMDD.
CREATE TABLE dim_tempo (
    tempo_sk INTEGER PRIMARY KEY,
    data TEXT NOT NULL UNIQUE,
    dia INTEGER NOT NULL,
    mes INTEGER NOT NULL,
    ano INTEGER NOT NULL,
    trimestre INTEGER NOT NULL,
    semestre INTEGER NOT NULL,
    dia_semana INTEGER NOT NULL,
    fim_semana INTEGER NOT NULL CHECK (fim_semana IN (0, 1))
);

-- GRAO: UM MOVIMENTO OPERACIONAL.
CREATE TABLE fato_movimentos (
    movimento_id TEXT PRIMARY KEY,
    cliente_sk INTEGER NOT NULL,
    tempo_sk INTEGER NOT NULL,
    valor_centavos INTEGER NOT NULL CHECK (valor_centavos >= 0),

    FOREIGN KEY (cliente_sk)
        REFERENCES dim_cliente(cliente_sk),

    FOREIGN KEY (tempo_sk)
        REFERENCES dim_tempo(tempo_sk)
);

-- AUDITORIA DE REPROCESSAMENTOS.
CREATE TABLE etl_periodos (
    carga_id INTEGER PRIMARY KEY AUTOINCREMENT,
    ano INTEGER NOT NULL,
    mes INTEGER NOT NULL,
    inicio TEXT NOT NULL,
    fim TEXT NOT NULL,
    linhas_anteriores INTEGER NOT NULL,
    linhas_novas INTEGER NOT NULL,
    total_anterior_centavos INTEGER NOT NULL,
    total_novo_centavos INTEGER NOT NULL,
    executado_em TEXT NOT NULL
);

CREATE INDEX idx_fato_movimento_tempo
    ON fato_movimentos(tempo_sk);

CREATE INDEX idx_fato_movimento_cliente
    ON fato_movimentos(cliente_sk);
