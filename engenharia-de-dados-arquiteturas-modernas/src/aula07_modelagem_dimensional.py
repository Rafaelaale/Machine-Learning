"""Aula 07 - Estrela, Snowflake e hierarquia pai-filho.

Le o DW da Aula 06 somente para leitura e gera
um banco separado para os modelos fisicos.
"""

import os
import sqlite3
import tempfile
from contextlib import closing
from pathlib import Path


BASE = Path(__file__).resolve().parent.parent
SCHEMA = BASE / "sql" / "aula07_star_snowflake.sql"


def conectar(caminho):
    conexao = sqlite3.connect(str(caminho), timeout=10)
    conexao.execute("PRAGMA foreign_keys = ON")
    return conexao


def extrair_ultimo_lote(dw):
    """Extrai uma fotografia confirmada do Data Warehouse."""
    origem = Path(dw).resolve()

    if not origem.is_file():
        raise FileNotFoundError(origem)

    with closing(
        sqlite3.connect(origem.as_uri() + "?mode=ro", uri=True)
    ) as conexao:
        conexao.row_factory = sqlite3.Row
        conexao.execute("BEGIN")

        lote = conexao.execute(
            "SELECT MAX(lote_id) FROM lotes_carga"
        ).fetchone()[0]

        if lote is None:
            raise ValueError("Data Warehouse sem lotes")

        registros = conexao.execute(
            """
            SELECT
                f.pedido_id,
                f.produto_id,
                f.cliente_id,
                f.data AS data_venda,
                f.quantidade,
                f.valor_centavos,
                p.nome AS produto_nome,
                p.categoria,
                c.nome AS cliente_nome
            FROM fato_vendas AS f
            JOIN dim_produtos AS p
              ON p.lote_id = f.lote_id
             AND p.produto_id = f.produto_id
            JOIN dim_clientes AS c
              ON c.lote_id = f.lote_id
             AND c.cliente_id = f.cliente_id
            WHERE f.lote_id = ?
            ORDER BY f.pedido_id, f.produto_id
            """,
            (lote,),
        ).fetchall()

        conexao.commit()

    return lote, [dict(r) for r in registros]


def gerar_modelos(dw, destino):
    """Constroi modelos separados, preservando a origem.

    Monta o novo arquivo antes de substituir a saida
    especifica da Aula 07.
    """
    dw = Path(dw).resolve()
    destino = Path(destino).resolve()

    if dw == destino:
        raise ValueError("Origem e destino devem ser diferentes")

    if destino.suffix.lower() != ".db":
        raise ValueError("Destino deve ser um arquivo .db")

    lote, vendas = extrair_ultimo_lote(dw)

    destino.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile(
        suffix=".db",
        prefix="aula07_",
        dir=destino.parent,
        delete=False,
    ) as arquivo:
        temporario = Path(arquivo.name)

    try:
        with closing(conectar(temporario)) as conexao:
            conexao.executescript(
                SCHEMA.read_text(encoding="utf-8")
            )

            with conexao:
                categorias = sorted({
                    v["categoria"] for v in vendas
                })
                codigos = {
                    nome: numero
                    for numero, nome in enumerate(
                        categorias, start=1
                    )
                }

                for nome, codigo in codigos.items():
                    conexao.execute(
                        """
                        INSERT INTO snow_dim_categorias
                        VALUES (?, ?)
                        """,
                        (codigo, nome),
                    )

                for v in vendas:
                    conexao.execute(
                        """
                        INSERT OR IGNORE INTO estrela_dim_clientes
                        VALUES (?, ?)
                        """,
                        (v["cliente_id"], v["cliente_nome"]),
                    )
                    conexao.execute(
                        """
                        INSERT OR IGNORE INTO snow_dim_clientes
                        VALUES (?, ?)
                        """,
                        (v["cliente_id"], v["cliente_nome"]),
                    )

                    conexao.execute(
                        """
                        INSERT OR IGNORE INTO estrela_dim_produtos
                        VALUES (?, ?, ?)
                        """,
                        (
                            v["produto_id"],
                            v["produto_nome"],
                            v["categoria"],
                        ),
                    )
                    conexao.execute(
                        """
                        INSERT OR IGNORE INTO snow_dim_produtos
                        VALUES (?, ?, ?)
                        """,
                        (
                            v["produto_id"],
                            v["produto_nome"],
                            codigos[v["categoria"]],
                        ),
                    )

                    fatos = (
                        v["pedido_id"],
                        v["produto_id"],
                        v["cliente_id"],
                        v["data_venda"],
                        v["quantidade"],
                        v["valor_centavos"],
                    )

                    conexao.execute(
                        """
                        INSERT INTO estrela_fato_vendas
                        VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        fatos,
                    )
                    conexao.execute(
                        """
                        INSERT INTO snow_fato_vendas
                        VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        fatos,
                    )

                # Exemplos didaticos, sem vinculo com clientes.
                exemplos = [
                    (1, "Brasil", "pais", None),
                    (2, "Bahia", "estado", 1),
                    (3, "Salvador", "cidade", 2),
                    (4, "Monaco", "pais", None),
                    (5, "Monaco", "cidade", 4),
                ]

                conexao.executemany(
                    """
                    INSERT INTO geo_nos
                    (no_id, nome, tipo, pai_id)
                    VALUES (?, ?, ?, ?)
                    """,
                    exemplos,
                )

        os.replace(temporario, destino)

    finally:
        if temporario.exists():
            temporario.unlink()

    return {
        "lote_origem": lote,
        "linhas_importadas": len(vendas),
        "categorias": len({
            v["categoria"] for v in vendas
        }),
    }


def indicadores(banco, modelo):
    """Executa a mesma agregacao em cada modelo."""
    if modelo not in {"estrela", "snowflake"}:
        raise ValueError("Modelo desconhecido")

    tabela = {
        "estrela": "estrela_fato_vendas",
        "snowflake": "snow_fato_vendas",
    }[modelo]

    with closing(conectar(banco)) as conexao:
        resultado = conexao.execute(
            f"""
            SELECT COUNT(DISTINCT pedido_id),
                   COUNT(*),
                   COALESCE(SUM(quantidade), 0),
                   COALESCE(SUM(valor_centavos), 0)
            FROM {tabela}
            """
        ).fetchone()

    return {
        "modelo": modelo,
        "pedidos": resultado[0],
        "linhas": resultado[1],
        "unidades": resultado[2],
        "faturamento_centavos": resultado[3],
    }


def vendas_por_categoria(banco, modelo):
    """Compara o JOIN simples com o JOIN normalizado."""
    consultas = {
        "estrela": """
            SELECT p.categoria,
                   SUM(f.valor_centavos)
            FROM estrela_fato_vendas AS f
            JOIN estrela_dim_produtos AS p
              ON p.produto_id = f.produto_id
            GROUP BY p.categoria
            ORDER BY p.categoria
        """,
        "snowflake": """
            SELECT c.categoria_nome,
                   SUM(f.valor_centavos)
            FROM snow_fato_vendas AS f
            JOIN snow_dim_produtos AS p
              ON p.produto_id = f.produto_id
            JOIN snow_dim_categorias AS c
              ON c.categoria_id = p.categoria_id
            GROUP BY c.categoria_nome
            ORDER BY c.categoria_nome
        """,
    }

    if modelo not in consultas:
        raise ValueError("Modelo desconhecido")

    with closing(conectar(banco)) as conexao:
        linhas = conexao.execute(
            consultas[modelo]
        ).fetchall()

    return [
        {"categoria": nome, "faturamento_centavos": valor}
        for nome, valor in linhas
    ]


def consultar_hierarquia(banco, cidade):
    """Recupera a hierarquia com uma CTE recursiva.

    Os identificadores visitados impedem loops na consulta.
    """
    consulta = """
        WITH RECURSIVE arvore(
            no_id, nome, tipo, caminho, visitados
        ) AS (
            SELECT
                no_id,
                nome,
                tipo,
                nome,
                printf('/%d/', no_id)
            FROM geo_nos
            WHERE pai_id IS NULL

            UNION ALL

            SELECT
                filho.no_id,
                filho.nome,
                filho.tipo,
                arvore.caminho || ' > ' || filho.nome,
                arvore.visitados || filho.no_id || '/'
            FROM geo_nos AS filho
            JOIN arvore
              ON filho.pai_id = arvore.no_id
            WHERE instr(
                arvore.visitados,
                printf('/%d/', filho.no_id)
            ) = 0
        )
        SELECT caminho
        FROM arvore
        WHERE nome = ? AND tipo = 'cidade'
        ORDER BY caminho
    """

    with closing(conectar(banco)) as conexao:
        resultados = conexao.execute(
            consulta, (cidade,)
        ).fetchall()

    return [r[0] for r in resultados]


def comparar_modelos(banco):
    """Verifica a equivalencia das agregacoes."""
    estrela = indicadores(banco, "estrela")
    snowflake = indicadores(banco, "snowflake")

    categorias_estrela = vendas_por_categoria(
        banco, "estrela"
    )
    categorias_snowflake = vendas_por_categoria(
        banco, "snowflake"
    )

    return {
        "estrela": estrela,
        "snowflake": snowflake,
        "categorias_estrela": categorias_estrela,
        "categorias_snowflake": categorias_snowflake,
        "equivalentes": (
            estrela["pedidos"] == snowflake["pedidos"]
            and estrela["linhas"] == snowflake["linhas"]
            and estrela["unidades"] == snowflake["unidades"]
            and estrela["faturamento_centavos"]
            == snowflake["faturamento_centavos"]
            and categorias_estrela == categorias_snowflake
        ),
    }
