PRAGMA foreign_keys = ON;

-- DIMENSAO CLIENTE: MODELO ESTRELA
CREATE TABLE dim_cliente (
    cliente_sk INTEGER PRIMARY KEY,
    cliente_id_origem INTEGER NOT NULL UNIQUE,
    nome TEXT NOT NULL,
    cidade TEXT,
    estado TEXT,
    faixa_etaria TEXT
);

-- DIMENSAO PRODUTO: MODELO SNOWFLAKE
CREATE TABLE dim_categoria (
    categoria_sk INTEGER PRIMARY KEY,
    categoria_id_origem INTEGER NOT NULL UNIQUE,
    nome TEXT NOT NULL
);

CREATE TABLE dim_produto (
    produto_sk INTEGER PRIMARY KEY,
    produto_id_origem INTEGER NOT NULL UNIQUE,
    nome TEXT NOT NULL,
    categoria_sk INTEGER NOT NULL,
    FOREIGN KEY (categoria_sk)
        REFERENCES dim_categoria(categoria_sk)
);

-- DIMENSAO TEMPO
CREATE TABLE dim_tempo (
    tempo_sk INTEGER PRIMARY KEY,
    data TEXT NOT NULL UNIQUE,
    ano INTEGER NOT NULL,
    mes INTEGER NOT NULL,
    trimestre INTEGER NOT NULL,
    semestre INTEGER NOT NULL,
    dia INTEGER NOT NULL
);

-- DIMENSOES SEM DADOS OPERACIONAIS NESTA ETAPA
CREATE TABLE dim_promocao (
    promocao_sk INTEGER PRIMARY KEY,
    descricao TEXT NOT NULL UNIQUE
);

CREATE TABLE dim_acesso (
    acesso_sk INTEGER PRIMARY KEY,
    descricao TEXT NOT NULL UNIQUE
);

-- A DIMENSAO AGING DEFINE AS FAIXAS DE NEGOCIO
CREATE TABLE dim_aging (
    aging_sk INTEGER PRIMARY KEY,
    situacao TEXT NOT NULL
        CHECK (situacao IN ('a_vencer', 'vencido')),
    faixa TEXT NOT NULL,
    dias_inicio INTEGER NOT NULL,
    dias_fim INTEGER,
    UNIQUE (situacao, faixa)
);

-- FATO 1: VENDAS
-- Grao: uma linha por produto de um pedido.
-- Pedido e uma dimensao degenerada.
CREATE TABLE fato_vendas (
    pedido_numero INTEGER NOT NULL,
    cliente_sk INTEGER NOT NULL,
    produto_sk INTEGER NOT NULL,
    tempo_sk INTEGER NOT NULL,
    promocao_sk INTEGER,
    acesso_sk INTEGER,
    quantidade INTEGER NOT NULL CHECK (quantidade > 0),
    preco_medio_centavos REAL NOT NULL
        CHECK (preco_medio_centavos >= 0),
    valor_total_centavos INTEGER NOT NULL
        CHECK (valor_total_centavos >= 0),

    PRIMARY KEY (pedido_numero, produto_sk),

    FOREIGN KEY (cliente_sk) REFERENCES dim_cliente(cliente_sk),
    FOREIGN KEY (produto_sk) REFERENCES dim_produto(produto_sk),
    FOREIGN KEY (tempo_sk) REFERENCES dim_tempo(tempo_sk),
    FOREIGN KEY (promocao_sk) REFERENCES dim_promocao(promocao_sk),
    FOREIGN KEY (acesso_sk) REFERENCES dim_acesso(acesso_sk)
);

-- FATO 2: INVENTARIO
-- Grao: produto por dia, com saidas somadas.
CREATE TABLE fato_inventario (
    produto_sk INTEGER NOT NULL,
    tempo_sk INTEGER NOT NULL,
    saida_estoque INTEGER NOT NULL CHECK (saida_estoque <= 0),

    PRIMARY KEY (produto_sk, tempo_sk),

    FOREIGN KEY (produto_sk) REFERENCES dim_produto(produto_sk),
    FOREIGN KEY (tempo_sk) REFERENCES dim_tempo(tempo_sk)
);

-- FATO 3: FINANCEIRO
-- Estrutura preparada, sem saldos ficticios.
CREATE TABLE fato_financeiro (
    cliente_sk INTEGER NOT NULL,
    aging_sk INTEGER NOT NULL,
    tempo_sk INTEGER NOT NULL,
    valor_receber_centavos INTEGER NOT NULL
        CHECK (valor_receber_centavos >= 0),
    valor_atraso_centavos INTEGER NOT NULL
        CHECK (valor_atraso_centavos >= 0),

    PRIMARY KEY (cliente_sk, aging_sk, tempo_sk),

    FOREIGN KEY (cliente_sk) REFERENCES dim_cliente(cliente_sk),
    FOREIGN KEY (aging_sk) REFERENCES dim_aging(aging_sk),
    FOREIGN KEY (tempo_sk) REFERENCES dim_tempo(tempo_sk)
);

CREATE INDEX idx_fato_vendas_tempo
    ON fato_vendas(tempo_sk);

CREATE INDEX idx_fato_vendas_cliente
    ON fato_vendas(cliente_sk);

CREATE INDEX idx_fato_inventario_tempo
    ON fato_inventario(tempo_sk);
