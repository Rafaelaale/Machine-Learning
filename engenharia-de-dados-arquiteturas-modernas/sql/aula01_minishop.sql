PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS clientes (
    id INTEGER PRIMARY KEY,
    nome TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS produtos (
    id INTEGER PRIMARY KEY,
    nome TEXT NOT NULL,
    preco_centavos INTEGER NOT NULL
        CHECK (preco_centavos >= 0)
);

CREATE TABLE IF NOT EXISTS inventario (
    produto_id INTEGER PRIMARY KEY,
    quantidade INTEGER NOT NULL
        CHECK (quantidade >= 0),
    FOREIGN KEY (produto_id) REFERENCES produtos(id)
);

CREATE TABLE IF NOT EXISTS pedidos (
    id INTEGER PRIMARY KEY,
    cliente_id INTEGER NOT NULL,
    criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    total_centavos INTEGER NOT NULL DEFAULT 0
        CHECK (total_centavos >= 0),
    status TEXT NOT NULL DEFAULT 'pendente'
        CHECK (status IN ('pendente', 'confirmado')),
    FOREIGN KEY (cliente_id) REFERENCES clientes(id)
);

CREATE TABLE IF NOT EXISTS itens_pedido (
    id INTEGER PRIMARY KEY,
    pedido_id INTEGER NOT NULL,
    produto_id INTEGER NOT NULL,
    quantidade INTEGER NOT NULL CHECK (quantidade > 0),
    preco_unitario_centavos INTEGER NOT NULL
        CHECK (preco_unitario_centavos >= 0),
    FOREIGN KEY (pedido_id) REFERENCES pedidos(id),
    FOREIGN KEY (produto_id) REFERENCES produtos(id)
);

CREATE TABLE IF NOT EXISTS pagamentos (
    id INTEGER PRIMARY KEY,
    pedido_id INTEGER NOT NULL UNIQUE,
    valor_centavos INTEGER NOT NULL
        CHECK (valor_centavos >= 0),
    status TEXT NOT NULL
        CHECK (status IN ('aprovado', 'recusado')),
    FOREIGN KEY (pedido_id) REFERENCES pedidos(id)
);

CREATE INDEX IF NOT EXISTS idx_pedidos_cliente
    ON pedidos(cliente_id);

CREATE INDEX IF NOT EXISTS idx_itens_pedido
    ON itens_pedido(pedido_id);
