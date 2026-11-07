PRAGMA foreign_keys = ON;

-- Dimensoes com chaves substitutas independentes do OLTP.

CREATE TABLE dim_clientes (
    cliente_sk INTEGER PRIMARY KEY,
    cliente_id_origem INTEGER NOT NULL UNIQUE,
    nome TEXT NOT NULL
);

CREATE TABLE dim_produtos (
    produto_sk INTEGER PRIMARY KEY,
    produto_id_origem INTEGER NOT NULL UNIQUE,
    nome TEXT NOT NULL,
    categoria TEXT NOT NULL
);

CREATE TABLE dim_tempo (
    tempo_sk INTEGER PRIMARY KEY,
    data_calendario TEXT NOT NULL UNIQUE,
    ano INTEGER NOT NULL,
    mes INTEGER NOT NULL,
    dia INTEGER NOT NULL
);

-- Fato atomico: uma linha por item de pedido.
-- O numero do pedido e uma dimensao degenerada.

CREATE TABLE fato_vendas_detalhe (
    pedido_numero INTEGER NOT NULL,
    cliente_sk INTEGER NOT NULL,
    produto_sk INTEGER NOT NULL,
    tempo_sk INTEGER NOT NULL,
    quantidade INTEGER NOT NULL CHECK (quantidade > 0),
    valor_centavos INTEGER NOT NULL CHECK (valor_centavos >= 0),

    PRIMARY KEY (pedido_numero, produto_sk),

    FOREIGN KEY (cliente_sk)
        REFERENCES dim_clientes(cliente_sk),

    FOREIGN KEY (produto_sk)
        REFERENCES dim_produtos(produto_sk),

    FOREIGN KEY (tempo_sk)
        REFERENCES dim_tempo(tempo_sk)
);

-- Fato agregado: uma linha por data, cliente e produto.
-- Esta chave composta define a granularidade consolidada.

CREATE TABLE fato_vendas_resumo (
    tempo_sk INTEGER NOT NULL,
    cliente_sk INTEGER NOT NULL,
    produto_sk INTEGER NOT NULL,
    quantidade INTEGER NOT NULL CHECK (quantidade > 0),
    valor_centavos INTEGER NOT NULL CHECK (valor_centavos >= 0),
    pedidos_distintos INTEGER NOT NULL,

    PRIMARY KEY (tempo_sk, cliente_sk, produto_sk),

    FOREIGN KEY (tempo_sk)
        REFERENCES dim_tempo(tempo_sk),

    FOREIGN KEY (cliente_sk)
        REFERENCES dim_clientes(cliente_sk),

    FOREIGN KEY (produto_sk)
        REFERENCES dim_produtos(produto_sk)
);

CREATE INDEX idx_fato_detalhe_tempo
    ON fato_vendas_detalhe(tempo_sk);

CREATE INDEX idx_fato_detalhe_cliente
    ON fato_vendas_detalhe(cliente_sk);

CREATE INDEX idx_fato_resumo_produto
    ON fato_vendas_resumo(produto_sk);
