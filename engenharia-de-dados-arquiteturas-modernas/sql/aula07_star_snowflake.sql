PRAGMA foreign_keys = ON;

-- MODELO ESTRELA
-- Categoria repetida na dimensao de produto.

CREATE TABLE estrela_dim_produtos (
    produto_id INTEGER PRIMARY KEY,
    produto_nome TEXT NOT NULL,
    categoria TEXT NOT NULL
);

CREATE TABLE estrela_dim_clientes (
    cliente_id INTEGER PRIMARY KEY,
    cliente_nome TEXT NOT NULL
);

CREATE TABLE estrela_fato_vendas (
    pedido_id INTEGER NOT NULL,
    produto_id INTEGER NOT NULL,
    cliente_id INTEGER NOT NULL,
    data_venda TEXT NOT NULL,
    quantidade INTEGER NOT NULL CHECK (quantidade > 0),
    valor_centavos INTEGER NOT NULL CHECK (valor_centavos >= 0),
    PRIMARY KEY (pedido_id, produto_id),
    FOREIGN KEY (produto_id)
        REFERENCES estrela_dim_produtos(produto_id),
    FOREIGN KEY (cliente_id)
        REFERENCES estrela_dim_clientes(cliente_id)
);

-- MODELO SNOWFLAKE
-- Categoria normalizada em sua propria tabela.

CREATE TABLE snow_dim_categorias (
    categoria_id INTEGER PRIMARY KEY,
    categoria_nome TEXT NOT NULL UNIQUE
);

CREATE TABLE snow_dim_produtos (
    produto_id INTEGER PRIMARY KEY,
    produto_nome TEXT NOT NULL,
    categoria_id INTEGER NOT NULL,
    FOREIGN KEY (categoria_id)
        REFERENCES snow_dim_categorias(categoria_id)
);

CREATE TABLE snow_dim_clientes (
    cliente_id INTEGER PRIMARY KEY,
    cliente_nome TEXT NOT NULL
);

CREATE TABLE snow_fato_vendas (
    pedido_id INTEGER NOT NULL,
    produto_id INTEGER NOT NULL,
    cliente_id INTEGER NOT NULL,
    data_venda TEXT NOT NULL,
    quantidade INTEGER NOT NULL CHECK (quantidade > 0),
    valor_centavos INTEGER NOT NULL CHECK (valor_centavos >= 0),
    PRIMARY KEY (pedido_id, produto_id),
    FOREIGN KEY (produto_id)
        REFERENCES snow_dim_produtos(produto_id),
    FOREIGN KEY (cliente_id)
        REFERENCES snow_dim_clientes(cliente_id)
);

-- HIERARQUIA PAI-FILHO
-- Pode conter niveis regulares e irregulares.

CREATE TABLE geo_nos (
    no_id INTEGER PRIMARY KEY,
    nome TEXT NOT NULL,
    tipo TEXT NOT NULL CHECK (
        tipo IN ('pais', 'estado', 'cidade')
    ),
    pai_id INTEGER,
    FOREIGN KEY (pai_id) REFERENCES geo_nos(no_id),
    CHECK (pai_id IS NULL OR pai_id <> no_id)
);

CREATE INDEX idx_geo_pai ON geo_nos(pai_id);
CREATE INDEX idx_estrela_data
    ON estrela_fato_vendas(data_venda);
CREATE INDEX idx_snow_data
    ON snow_fato_vendas(data_venda);
