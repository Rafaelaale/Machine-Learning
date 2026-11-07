PRAGMA foreign_keys = ON;

-- SCD TIPO 1: UMA LINHA POR CHAVE NATURAL.
CREATE TABLE dim_clientes (
    cliente_sk INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo_natural TEXT NOT NULL UNIQUE,
    nome TEXT NOT NULL,
    saldo_centavos INTEGER NOT NULL
        CHECK (saldo_centavos >= 0)
);

CREATE TABLE dim_produtos (
    produto_sk INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo_natural TEXT NOT NULL UNIQUE,
    nome TEXT NOT NULL
);

CREATE TABLE fato_vendas (
    venda_id INTEGER PRIMARY KEY,
    cliente_sk INTEGER NOT NULL,
    produto_sk INTEGER NOT NULL,
    quantidade INTEGER NOT NULL CHECK (quantidade > 0),
    valor_centavos INTEGER NOT NULL
        CHECK (valor_centavos >= 0),

    FOREIGN KEY (cliente_sk)
        REFERENCES dim_clientes(cliente_sk),

    FOREIGN KEY (produto_sk)
        REFERENCES dim_produtos(produto_sk)
);

CREATE TABLE auditoria_lookup (
    evento_id INTEGER PRIMARY KEY AUTOINCREMENT,
    acao TEXT NOT NULL,
    tipo_entidade TEXT NOT NULL,
    codigo_natural TEXT NOT NULL
);
