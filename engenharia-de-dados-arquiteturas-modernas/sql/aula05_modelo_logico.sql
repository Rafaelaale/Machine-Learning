PRAGMA foreign_keys = ON;

CREATE TABLE clientes (
    cliente_id INTEGER PRIMARY KEY,
    nome TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE
);

CREATE TABLE categorias (
    categoria_id INTEGER PRIMARY KEY,
    nome TEXT NOT NULL UNIQUE
);

CREATE TABLE produtos (
    produto_id INTEGER PRIMARY KEY,
    categoria_id INTEGER NOT NULL,
    nome TEXT NOT NULL,
    preco_centavos INTEGER NOT NULL
        CHECK (preco_centavos >= 0),
    FOREIGN KEY (categoria_id)
        REFERENCES categorias(categoria_id)
);

CREATE TABLE estoque (
    estoque_id INTEGER PRIMARY KEY,
    produto_id INTEGER NOT NULL UNIQUE,
    quantidade INTEGER NOT NULL CHECK (quantidade >= 0),
    FOREIGN KEY (produto_id)
        REFERENCES produtos(produto_id)
);

CREATE TABLE pedidos (
    pedido_id INTEGER PRIMARY KEY,
    cliente_id INTEGER NOT NULL,
    data_pedido TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    estado TEXT NOT NULL DEFAULT 'pendente'
        CHECK (estado IN ('pendente', 'confirmado')),
    valor_centavos INTEGER NOT NULL DEFAULT 0
        CHECK (valor_centavos >= 0),
    FOREIGN KEY (cliente_id)
        REFERENCES clientes(cliente_id)
);

-- A chave primaria dos itens tem DUAS colunas.
CREATE TABLE itens_pedido (
    pedido_id INTEGER NOT NULL,
    produto_id INTEGER NOT NULL,
    quantidade INTEGER NOT NULL CHECK (quantidade > 0),
    preco_unitario_centavos INTEGER NOT NULL
        CHECK (preco_unitario_centavos >= 0),
    PRIMARY KEY (pedido_id, produto_id),
    FOREIGN KEY (pedido_id)
        REFERENCES pedidos(pedido_id),
    FOREIGN KEY (produto_id)
        REFERENCES produtos(produto_id)
);

-- O UNIQUE garante no maximo uma fatura por pedido.
CREATE TABLE faturas (
    fatura_id INTEGER PRIMARY KEY,
    pedido_id INTEGER NOT NULL UNIQUE,
    valor_centavos INTEGER NOT NULL
        CHECK (valor_centavos >= 0),
    estado TEXT NOT NULL DEFAULT 'emitida',
    FOREIGN KEY (pedido_id)
        REFERENCES pedidos(pedido_id)
);

CREATE TABLE pagamentos (
    pagamento_id INTEGER PRIMARY KEY,
    pedido_id INTEGER NOT NULL UNIQUE,
    valor_centavos INTEGER NOT NULL
        CHECK (valor_centavos >= 0),
    estado TEXT NOT NULL
        CHECK (estado IN ('aprovado', 'recusado')),
    FOREIGN KEY (pedido_id)
        REFERENCES pedidos(pedido_id)
);

-- Movimento relacionado ao estoque e ao item vendido.
CREATE TABLE movimentos_estoque (
    movimento_id INTEGER PRIMARY KEY,
    estoque_id INTEGER NOT NULL,
    pedido_id INTEGER NOT NULL,
    produto_id INTEGER NOT NULL,
    tipo TEXT NOT NULL CHECK (tipo IN ('saida')),
    quantidade INTEGER NOT NULL CHECK (quantidade > 0),
    UNIQUE (pedido_id, produto_id),
    FOREIGN KEY (estoque_id)
        REFERENCES estoque(estoque_id),
    FOREIGN KEY (pedido_id, produto_id)
        REFERENCES itens_pedido(pedido_id, produto_id)
);

CREATE INDEX idx_pedidos_cliente
    ON pedidos(cliente_id);

CREATE INDEX idx_produtos_categoria
    ON produtos(categoria_id);

CREATE INDEX idx_movimentos_estoque
    ON movimentos_estoque(estoque_id);
