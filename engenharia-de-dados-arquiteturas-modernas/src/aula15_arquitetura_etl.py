"""Aula 15 - Projeto do ETL dimensional da Minishop.

Politicas:
- Cliente: SCD2 para cidade, estado e faixa etaria.
- Nome do cliente: correcao Tipo 1 na versao atual.
- Produto e categoria: SCD1.
- Promocao: SCD1.
- Tempo: chave deterministica AAAAMMDD.

Aula de arquitetura e carga de dimensoes.
A orquestracao de fatos sera abordada posteriormente.
"""

import sqlite3
from contextlib import closing
from datetime import date, datetime, timezone
from pathlib import Path


BASE = Path(__file__).resolve().parent.parent
SCHEMA = BASE / "sql" / "aula15_arquitetura_etl.sql"
INICIO_HISTORICO = "1900-01-01"


def conectar(banco):
    conexao = sqlite3.connect(str(banco), timeout=10)
    conexao.execute("PRAGMA foreign_keys = ON")
    return conexao


def validar_data(valor):
    if not isinstance(valor, str):
        raise ValueError("Data deve ser texto ISO")

    try:
        data = date.fromisoformat(valor)
    except ValueError as erro:
        raise ValueError("Data invalida") from erro

    if data.isoformat() != valor:
        raise ValueError("Formato deve ser YYYY-MM-DD")

    return valor


def validar_texto(valor, campo):
    if not isinstance(valor, str) or not valor.strip():
        raise ValueError(f"{campo} invalido")

    return valor.strip()


def criar_dw(banco):
    """Cria o esquema sem apagar dados ja existentes."""
    banco = Path(banco)
    banco.parent.mkdir(parents=True, exist_ok=True)

    with closing(conectar(banco)) as conexao:
        conexao.executescript(
            SCHEMA.read_text(encoding="utf-8")
        )


def lookup_cliente(
    conexao,
    codigo,
    nome,
    inicio,
    cidade=None,
    estado=None,
    faixa_etaria=None,
    cod_cidade=None,
    cod_estado=None,
):
    """Atualiza Cliente com politica SCD Tipo 2.

    Atributos historicos:
    cidade, estado, faixa etaria e codigos geograficos.

    Nome: sobrescrito na versao atual (Tipo 1).

    Para uma mudanca historica, inicio deve representar
    a data efetiva conhecida dessa mudanca.
    """
    codigo = validar_texto(codigo, "Codigo do cliente")
    nome = validar_texto(nome, "Nome do cliente")
    validar_data(inicio)

    historicos = (
        cod_cidade, cidade,
        cod_estado, estado,
        faixa_etaria,
    )

    atual = conexao.execute(
        """
        SELECT
            cliente_sk,
            nome_cliente,
            cod_cidade,
            nome_cidade,
            cod_estado,
            nome_estado,
            faixa_etaria,
            valid_from
        FROM dim_cliente
        WHERE cod_cliente = ?
          AND valid_to IS NULL
        """,
        (codigo,),
    ).fetchone()

    if atual is not None:
        sk = atual[0]
        valores_atuais = tuple(atual[2:7])

        if valores_atuais == historicos:
            if atual[1] != nome:
                conexao.execute(
                    """
                    UPDATE dim_cliente
                    SET nome_cliente = ?
                    WHERE cliente_sk = ?
                    """,
                    (nome, sk),
                )
                return {
                    "sk": sk,
                    "acao": "correcao_tipo1",
                }

            return {
                "sk": sk,
                "acao": "reutilizado",
            }

        if inicio <= atual[7]:
            raise ValueError(
                "Mudanca historica exige data posterior"
            )

        conexao.execute(
            """
            UPDATE dim_cliente
            SET valid_to = ?
            WHERE cliente_sk = ?
            """,
            (inicio, sk),
        )

        acao = "nova_versao_scd2"

    else:
        anterior = conexao.execute(
            """
            SELECT COUNT(*)
            FROM dim_cliente
            WHERE cod_cliente = ?
            """,
            (codigo,),
        ).fetchone()[0]

        if anterior:
            raise ValueError(
                "Cliente historico sem versao vigente"
            )

        acao = "novo_cliente"

    nova_sk = conexao.execute(
        """
        INSERT INTO dim_cliente (
            cod_cliente, nome_cliente,
            cod_cidade, nome_cidade,
            cod_estado, nome_estado,
            faixa_etaria, valid_from, valid_to
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, NULL)
        """,
        (
            codigo, nome,
            cod_cidade, cidade,
            cod_estado, estado,
            faixa_etaria, inicio,
        ),
    ).lastrowid

    return {
        "sk": nova_sk,
        "acao": acao,
    }


def registrar_cliente(
    banco,
    codigo,
    nome,
    inicio,
    cidade=None,
    estado=None,
    faixa_etaria=None,
    cod_cidade=None,
    cod_estado=None,
):
    """API didatica para registrar mudancas conhecidas."""
    with closing(conectar(banco)) as conexao:
        with conexao:
            return lookup_cliente(
                conexao,
                codigo,
                nome,
                inicio,
                cidade=cidade,
                estado=estado,
                faixa_etaria=faixa_etaria,
                cod_cidade=cod_cidade,
                cod_estado=cod_estado,
            )


def lookup_cliente_historico(banco, codigo, data_evento):
    """Recupera SK vigente na data do fato."""
    validar_data(data_evento)

    with closing(conectar(banco)) as conexao:
        linhas = conexao.execute(
            """
            SELECT cliente_sk
            FROM dim_cliente
            WHERE cod_cliente = ?
              AND valid_from <= ?
              AND (
                  valid_to IS NULL
                  OR ? < valid_to
              )
            """,
            (codigo, data_evento, data_evento),
        ).fetchall()

    if len(linhas) != 1:
        raise ValueError(
            "Cliente sem versao historica unica"
        )

    return linhas[0][0]


def versoes_cliente(banco, codigo):
    with closing(conectar(banco)) as conexao:
        linhas = conexao.execute(
            """
            SELECT
                cliente_sk, nome_cliente,
                nome_cidade, nome_estado,
                faixa_etaria, valid_from, valid_to
            FROM dim_cliente
            WHERE cod_cliente = ?
            ORDER BY valid_from
            """,
            (codigo,),
        ).fetchall()

    return [
        {
            "sk": r[0],
            "nome": r[1],
            "cidade": r[2],
            "estado": r[3],
            "faixa_etaria": r[4],
            "valid_from": r[5],
            "valid_to": r[6],
        }
        for r in linhas
    ]


def lookup_categoria(conexao, codigo, nome):
    codigo = validar_texto(codigo, "Categoria")
    nome = validar_texto(nome, "Nome da categoria")

    conexao.execute(
        """
        INSERT INTO dim_categoria
        (cod_categoria, nome_categoria)
        VALUES (?, ?)
        ON CONFLICT(cod_categoria)
        DO UPDATE SET nome_categoria = excluded.nome_categoria
        """,
        (codigo, nome),
    )

    return conexao.execute(
        """
        SELECT categoria_sk
        FROM dim_categoria
        WHERE cod_categoria = ?
        """,
        (codigo,),
    ).fetchone()[0]


def lookup_produto(
    conexao, codigo, nome, categoria_sk
):
    """SCD1: preserva a SK quando o produto muda."""
    codigo = validar_texto(codigo, "Produto")
    nome = validar_texto(nome, "Nome do produto")

    conexao.execute(
        """
        INSERT INTO dim_produto
        (cod_produto, nome_produto, categoria_sk)
        VALUES (?, ?, ?)
        ON CONFLICT(cod_produto)
        DO UPDATE SET
            nome_produto = excluded.nome_produto,
            categoria_sk = excluded.categoria_sk
        """,
        (codigo, nome, categoria_sk),
    )

    return conexao.execute(
        """
        SELECT produto_sk
        FROM dim_produto
        WHERE cod_produto = ?
        """,
        (codigo,),
    ).fetchone()[0]


def registrar_produto(
    banco, codigo, nome, codigo_categoria, categoria
):
    with closing(conectar(banco)) as conexao:
        with conexao:
            categoria_sk = lookup_categoria(
                conexao, codigo_categoria, categoria
            )

            return lookup_produto(
                conexao, codigo, nome, categoria_sk
            )


def registrar_promocao(banco, codigo, descricao):
    """Promocao Tipo 1, sem versionamento historico."""
    codigo = validar_texto(codigo, "Promocao")
    descricao = validar_texto(
        descricao, "Descricao da promocao"
    )

    with closing(conectar(banco)) as conexao:
        with conexao:
            conexao.execute(
                """
                INSERT INTO dim_promocao
                (cod_promocao, descricao)
                VALUES (?, ?)
                ON CONFLICT(cod_promocao)
                DO UPDATE SET descricao = excluded.descricao
                """,
                (codigo, descricao),
            )

            return conexao.execute(
                """
                SELECT promocao_sk
                FROM dim_promocao
                WHERE cod_promocao = ?
                """,
                (codigo,),
            ).fetchone()[0]


def registrar_tempo(conexao, valor):
    """SCD1: um membro por dia e chave AAAAMMDD."""
    validar_data(valor)
    data = date.fromisoformat(valor)
    sk = int(data.strftime("%Y%m%d"))

    conexao.execute(
        """
        INSERT OR IGNORE INTO dim_tempo
        (tempo_sk, data, ano, mes, dia, trimestre, semestre)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            sk, valor,
            data.year, data.month, data.day,
            (data.month - 1) // 3 + 1,
            (data.month - 1) // 6 + 1,
        ),
    )

    return sk


def extrair_oltp(banco_origem):
    """Extrai catalogo e datas sem escrever no OLTP."""
    origem = Path(banco_origem).resolve()

    if not origem.is_file():
        raise FileNotFoundError(origem)

    with closing(
        sqlite3.connect(
            origem.as_uri() + "?mode=ro",
            uri=True,
        )
    ) as conexao:
        conexao.row_factory = sqlite3.Row
        conexao.execute("BEGIN")

        clientes = conexao.execute(
            """
            SELECT cliente_id, nome
            FROM clientes
            ORDER BY cliente_id
            """
        ).fetchall()

        produtos = conexao.execute(
            """
            SELECT
                p.produto_id,
                p.nome AS produto_nome,
                c.categoria_id,
                c.nome AS categoria_nome
            FROM produtos p
            JOIN categorias c
              ON c.categoria_id = p.categoria_id
            ORDER BY p.produto_id
            """
        ).fetchall()

        datas = conexao.execute(
            """
            SELECT DISTINCT substr(p.data_pedido, 1, 10)
            FROM pedidos p
            JOIN pagamentos pg
              ON pg.pedido_id = p.pedido_id
            WHERE p.estado = 'confirmado'
              AND pg.estado = 'aprovado'
            ORDER BY 1
            """
        ).fetchall()

        conexao.commit()

    return {
        "clientes": [dict(r) for r in clientes],
        "produtos": [dict(r) for r in produtos],
        "datas": [r[0] for r in datas],
    }


def carregar_dimensoes_oltp(banco_origem, banco_dw):
    """Carga dimensional inicial/atualizacoes Tipo 1.

    Como o OLTP atual nao tem dados geograficos,
    nao modifica os atributos historicos existentes.

    Alteracoes historicas devem receber uma data
    efetiva conhecida via registrar_cliente().
    """
    origem = Path(banco_origem).resolve()
    destino = Path(banco_dw).resolve()

    if origem == destino:
        raise ValueError("Origem e destino iguais")

    dados = extrair_oltp(origem)
    criar_dw(destino)

    with closing(conectar(destino)) as conexao:
        with conexao:
            for cliente in dados["clientes"]:
                codigo = str(cliente["cliente_id"])
                nome = cliente["nome"]

                atual = conexao.execute(
                    """
                    SELECT cliente_sk, nome_cliente
                    FROM dim_cliente
                    WHERE cod_cliente = ?
                      AND valid_to IS NULL
                    """,
                    (codigo,),
                ).fetchone()

                if atual is None:
                    lookup_cliente(
                        conexao,
                        codigo,
                        nome,
                        INICIO_HISTORICO,
                    )
                elif atual[1] != nome:
                    # Correcao nominal Tipo 1:
                    # preserva atributos SCD2 existentes.
                    conexao.execute(
                        """
                        UPDATE dim_cliente
                        SET nome_cliente = ?
                        WHERE cliente_sk = ?
                        """,
                        (nome, atual[0]),
                    )

            for produto in dados["produtos"]:
                categoria_sk = lookup_categoria(
                    conexao,
                    str(produto["categoria_id"]),
                    produto["categoria_nome"],
                )

                lookup_produto(
                    conexao,
                    str(produto["produto_id"]),
                    produto["produto_nome"],
                    categoria_sk,
                )

            for valor in dados["datas"]:
                registrar_tempo(conexao, valor)

            conexao.execute(
                """
                INSERT INTO auditoria_dimensoes
                (executado_em, clientes_lidos,
                 produtos_lidos, datas_lidas)
                VALUES (?, ?, ?, ?)
                """,
                (
                    datetime.now(timezone.utc).isoformat(),
                    len(dados["clientes"]),
                    len(dados["produtos"]),
                    len(dados["datas"]),
                ),
            )

    return {
        "clientes_lidos": len(dados["clientes"]),
        "produtos_lidos": len(dados["produtos"]),
        "datas_lidas": len(dados["datas"]),
    }


def contagens(banco):
    tabelas = (
        "dim_cliente",
        "dim_categoria",
        "dim_produto",
        "dim_promocao",
        "dim_tempo",
        "auditoria_dimensoes",
    )

    with closing(conectar(banco)) as conexao:
        return {
            tabela: conexao.execute(
                f"SELECT COUNT(*) FROM {tabela}"
            ).fetchone()[0]
            for tabela in tabelas
        }
