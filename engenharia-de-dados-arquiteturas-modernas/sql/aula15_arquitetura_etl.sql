PRAGMA foreign_keys = ON;

-- CLIENTE: SCD TIPO 2.
-- O mesmo codigo natural pode ter varias SKs historicas.
-- valid_from incluso; valid_to exclusivo.
CREATE TABLE IF NOT EXISTS dim_cliente (
    cliente_sk INTEGER PRIMARY KEY AUTOINCREMENT,
    cod_cliente TEXT NOT NULL,
    nome_cliente TEXT NOT NULL,
    cod_cidade TEXT,
    nome_cidade TEXT,
    cod_estado TEXT,
    nome_estado TEXT,
    faixa_etaria TEXT,
    valid_from TEXT NOT NULL,
    valid_to TEXT,
    CHECK (valid_to IS NULL OR valid_to > valid_from),
    UNIQUE (cod_cliente, valid_from)
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_cliente_atual
    ON dim_cliente(cod_cliente)
    WHERE valid_to IS NULL;

CREATE INDEX IF NOT EXISTS idx_cliente_vigencia
    ON dim_cliente(cod_cliente, valid_from, valid_to);

-- CATEGORIA E PRODUTO: SNOWFLAKE, SCD TIPO 1.
CREATE TABLE IF NOT EXISTS dim_categoria (
    categoria_sk INTEGER PRIMARY KEY AUTOINCREMENT,
    cod_categoria TEXT NOT NULL UNIQUE,
    nome_categoria TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_produto (
    produto_sk INTEGER PRIMARY KEY AUTOINCREMENT,
    cod_produto TEXT NOT NULL UNIQUE,
    nome_produto TEXT NOT NULL,
    categoria_sk INTEGER NOT NULL,
    FOREIGN KEY (categoria_sk)
        REFERENCES dim_categoria(categoria_sk)
);

-- PROMOCAO: SCD TIPO 1.
CREATE TABLE IF NOT EXISTS dim_promocao (
    promocao_sk INTEGER PRIMARY KEY AUTOINCREMENT,
    cod_promocao TEXT NOT NULL UNIQUE,
    descricao TEXT NOT NULL
);

-- TEMPO: CHAVE DETERMINISTICA AAAAMMDD.
CREATE TABLE IF NOT EXISTS dim_tempo (
    tempo_sk INTEGER PRIMARY KEY,
    data TEXT NOT NULL UNIQUE,
    ano INTEGER NOT NULL,
    mes INTEGER NOT NULL,
    dia INTEGER NOT NULL,
    trimestre INTEGER NOT NULL,
    semestre INTEGER NOT NULL
);

-- CONTROLE DE EXECUCOES DA CARGA DIMENSIONAL.
CREATE TABLE IF NOT EXISTS auditoria_dimensoes (
    carga_id INTEGER PRIMARY KEY AUTOINCREMENT,
    executado_em TEXT NOT NULL,
    clientes_lidos INTEGER NOT NULL,
    produtos_lidos INTEGER NOT NULL,
    datas_lidas INTEGER NOT NULL
);
