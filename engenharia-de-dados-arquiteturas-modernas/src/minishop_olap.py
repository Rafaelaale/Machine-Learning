"""Aula 02 - Ambiente OLAP separado do OLTP Minishop.

Cria uma fotografia analitica de compras confirmadas.
Nao altera o banco de dados transacional.
"""

import os
import sqlite3
import tempfile
from contextlib import closing
from pathlib import Path
from urllib.parse import quote


SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE dim_clientes (
    cliente_id INTEGER PRIMARY KEY,
    nome TEXT NOT NULL
);

CREATE TABLE dim_produtos (
    produto_id INTEGER PRIMARY KEY,
    nome TEXT NOT NULL
);

CREATE TABLE dim_tempo (
    data TEXT PRIMARY KEY,
    ano INTEGER NOT NULL,
    mes INTEGER NOT NULL
);

CREATE TABLE fato_vendas (
    item_id INTEGER PRIMARY KEY,
    pedido_id INTEGER NOT NULL,
    cliente_id INTEGER NOT NULL,
    produto_id INTEGER NOT NULL,
    data TEXT NOT NULL,
    quantidade INTEGER NOT NULL CHECK (quantidade > 0),
    valor_centavos INTEGER NOT NULL
        CHECK (valor_centavos >= 0),
    FOREIGN KEY (cliente_id)
        REFERENCES dim_clientes(cliente_id),
    FOREIGN KEY (produto_id)
        REFERENCES dim_produtos(produto_id),
    FOREIGN KEY (data)
        REFERENCES dim_tempo(data)
);

CREATE INDEX idx_fato_data ON fato_vendas(data);
CREATE INDEX idx_fato_produto ON fato_vendas(produto_id);
"""


def conectar(caminho):
    """Abre conexao analitica com chaves estrangeiras ativas."""
    conexao = sqlite3.connect(str(caminho))
    conexao.execute("PRAGMA foreign_keys = ON")
    return conexao


def ler_vendas_confirmadas(banco_oltp):
    """Le o OLTP sem permitir escritas no banco de origem."""
    banco_oltp = Path(banco_oltp).resolve()

    if not banco_oltp.is_file():
        raise FileNotFoundError(banco_oltp)

    uri = "file:" + quote(
        banco_oltp.as_posix(), safe="/:"
    ) + "?mode=ro"

    with closing(sqlite3.connect(uri, uri=True)) as conexao:
        conexao.row_factory = sqlite3.Row

        conexao.execute("BEGIN")

        registros = conexao.execute(
            """
            SELECT
                i.id AS item_id,
                i.pedido_id,
                p.cliente_id,
                c.nome AS cliente_nome,
                i.produto_id,
                pr.nome AS produto_nome,
                substr(p.criado_em, 1, 10) AS data,
                i.quantidade,
                i.preco_unitario_centavos * i.quantidade
                    AS valor_centavos
            FROM itens_pedido AS i
            JOIN pedidos AS p
                ON p.id = i.pedido_id
            JOIN pagamentos AS pg
                ON pg.pedido_id = p.id
            JOIN clientes AS c
                ON c.id = p.cliente_id
            JOIN produtos AS pr
                ON pr.id = i.produto_id
            WHERE p.status = 'confirmado'
              AND pg.status = 'aprovado'
            ORDER BY i.id
            """
        ).fetchall()

        conexao.commit()

    return [dict(registro) for registro in registros]


def carregar_olap(banco_oltp, banco_olap):
    """Reconstrói uma fotografia do OLAP de forma atomica.

    O banco existente so e substituido apos a nova
    carga ter sido concluida com sucesso.
    """
    origem = Path(banco_oltp).resolve()
    destino = Path(banco_olap).resolve()

    if origem == destino:
        raise ValueError("OLTP e OLAP devem usar arquivos diferentes")

    vendas = ler_vendas_confirmadas(origem)

    destino.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile(
        suffix=".db",
        prefix="olap_tmp_",
        dir=destino.parent,
        delete=False,
    ) as arquivo:
        temporario = Path(arquivo.name)

    try:
        with closing(conectar(temporario)) as conexao:
            conexao.executescript(SCHEMA)

            with conexao:
                for venda in vendas:
                    data = venda["data"]

                    if not data or len(data) != 10:
                        raise ValueError(
                            "Data de venda invalida"
                        )

                    ano = int(data[:4])
                    mes = int(data[5:7])

                    if not 1 <= mes <= 12:
                        raise ValueError(
                            "Mes de venda invalido"
                        )

                    conexao.execute(
                        """
                        INSERT OR IGNORE INTO dim_clientes
                            (cliente_id, nome)
                        VALUES (?, ?)
                        """,
                        (
                            venda["cliente_id"],
                            venda["cliente_nome"],
                        ),
                    )

                    conexao.execute(
                        """
                        INSERT OR IGNORE INTO dim_produtos
                            (produto_id, nome)
                        VALUES (?, ?)
                        """,
                        (
                            venda["produto_id"],
                            venda["produto_nome"],
                        ),
                    )

                    conexao.execute(
                        """
                        INSERT OR IGNORE INTO dim_tempo
                            (data, ano, mes)
                        VALUES (?, ?, ?)
                        """,
                        (data, ano, mes),
                    )

                    conexao.execute(
                        """
                        INSERT INTO fato_vendas (
                            item_id, pedido_id, cliente_id,
                            produto_id, data, quantidade,
                            valor_centavos
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            venda["item_id"],
                            venda["pedido_id"],
                            venda["cliente_id"],
                            venda["produto_id"],
                            data,
                            venda["quantidade"],
                            venda["valor_centavos"],
                        ),
                    )

        os.replace(temporario, destino)

    finally:
        if temporario.exists():
            temporario.unlink()

    return len(vendas)


def indicadores(banco_olap):
    """Calcula faturamento, pedidos e ticket medio."""
    if not Path(banco_olap).is_file():
        raise FileNotFoundError(banco_olap)

    with closing(conectar(banco_olap)) as conexao:
        resultado = conexao.execute(
            """
            SELECT
                COALESCE(SUM(valor_centavos), 0),
                COUNT(DISTINCT pedido_id),
                COALESCE(SUM(quantidade), 0),
                COUNT(*)
            FROM fato_vendas
            """
        ).fetchone()

    faturamento, pedidos, unidades, itens = resultado

    return {
        "faturamento_centavos": faturamento,
        "pedidos": pedidos,
        "unidades_vendidas": unidades,
        "linhas_fato": itens,
        "ticket_medio_centavos": (
            round(faturamento / pedidos)
            if pedidos else 0
        ),
    }


def faturamento_por_produto(banco_olap):
    """Agrupa vendas por produto."""
    with closing(conectar(banco_olap)) as conexao:
        registros = conexao.execute(
            """
            SELECT
                p.nome,
                SUM(f.quantidade),
                SUM(f.valor_centavos)
            FROM fato_vendas AS f
            JOIN dim_produtos AS p
                ON p.produto_id = f.produto_id
            GROUP BY p.produto_id, p.nome
            ORDER BY SUM(f.valor_centavos) DESC, p.nome
            """
        ).fetchall()

    return [
        {
            "produto": nome,
            "unidades": quantidade,
            "faturamento_centavos": valor,
        }
        for nome, quantidade, valor in registros
    ]


def faturamento_mensal(banco_olap):
    """Agrega o faturamento por ano e mes."""
    with closing(conectar(banco_olap)) as conexao:
        registros = conexao.execute(
            """
            SELECT
                t.ano,
                t.mes,
                SUM(f.valor_centavos)
            FROM fato_vendas AS f
            JOIN dim_tempo AS t
                ON t.data = f.data
            GROUP BY t.ano, t.mes
            ORDER BY t.ano, t.mes
            """
        ).fetchall()

    return [
        {
            "ano": ano,
            "mes": mes,
            "faturamento_centavos": valor,
        }
        for ano, mes, valor in registros
    ]
