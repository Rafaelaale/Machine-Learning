"""Aula 12 - Lookup, Surrogate Keys e SCD Tipo 1.

Dados didaticos baseados nos cenarios do video.
Ambiente separado do ETL SCD2 da Aula 11.
"""

import sqlite3
from contextlib import closing
from pathlib import Path


BASE = Path(__file__).resolve().parent.parent
SCHEMA = BASE / "sql" / "aula12_lookup_surrogate_keys.sql"


CLIENTES_INICIAIS = [
    {"codigo": "23400", "nome": "Cliente 1", "saldo": 10000},
    {"codigo": "02342", "nome": "Cliente 2", "saldo": 20000},
    {"codigo": "34500", "nome": "Cliente 3", "saldo": 5000},
]

CLIENTES_ATUALIZADOS = [
    {"codigo": "23400", "nome": "Cliente 1", "saldo": 30000},
    {"codigo": "02342", "nome": "Cliente 2A", "saldo": 20000},
    {"codigo": "34500", "nome": "Cliente 3", "saldo": 5000},
    {"codigo": "56700", "nome": "Cliente 8", "saldo": 1000},
]

PRODUTOS_EXEMPLO = [
    {"codigo": "PROD-01", "nome": "Teclado"},
    {"codigo": "PROD-02", "nome": "Mouse"},
]

VENDAS_EXEMPLO = [
    {
        "venda_id": 1, "cliente": "23400",
        "produto": "PROD-01", "quantidade": 2,
        "valor_centavos": 30000,
    },
    {
        "venda_id": 2, "cliente": "02342",
        "produto": "PROD-02", "quantidade": 1,
        "valor_centavos": 8000,
    },
    {
        "venda_id": 3, "cliente": "56700",
        "produto": "PROD-01", "quantidade": 1,
        "valor_centavos": 15000,
    },
]


def conectar(banco):
    conexao = sqlite3.connect(str(banco), timeout=10)
    conexao.execute("PRAGMA foreign_keys = ON")
    return conexao


def criar_banco(banco):
    """Cria um banco novo, sem substituir arquivo existente."""
    banco = Path(banco)
    if banco.exists():
        raise FileExistsError(banco)

    banco.parent.mkdir(parents=True, exist_ok=True)

    try:
        with closing(conectar(banco)) as conexao:
            conexao.executescript(
                SCHEMA.read_text(encoding="utf-8")
            )
    except Exception:
        if banco.exists():
            banco.unlink()
        raise


def validar_cliente(cliente):
    codigo = cliente["codigo"]
    nome = cliente["nome"]
    saldo = cliente["saldo"]

    if not isinstance(codigo, str) or not codigo.strip():
        raise ValueError("Codigo natural invalido")

    if not isinstance(nome, str) or not nome.strip():
        raise ValueError("Nome invalido")

    if type(saldo) is not int or saldo < 0:
        raise ValueError("Saldo invalido")


def lookup_cliente(conexao, cliente):
    """SCD1: manter SK e atualizar atributos quando mudarem."""
    validar_cliente(cliente)

    codigo = cliente["codigo"]
    nome = cliente["nome"].strip()
    saldo = cliente["saldo"]

    atual = conexao.execute(
        """
        SELECT cliente_sk, nome, saldo_centavos
        FROM dim_clientes
        WHERE codigo_natural = ?
        """,
        (codigo,),
    ).fetchone()

    if atual is None:
        sk = conexao.execute(
            """
            INSERT INTO dim_clientes
                (codigo_natural, nome, saldo_centavos)
            VALUES (?, ?, ?)
            """,
            (codigo, nome, saldo),
        ).lastrowid
        acao = "inserido"

    else:
        sk = atual[0]

        if (atual[1], atual[2]) != (nome, saldo):
            conexao.execute(
                """
                UPDATE dim_clientes
                SET nome = ?, saldo_centavos = ?
                WHERE cliente_sk = ?
                """,
                (nome, saldo, sk),
            )
            acao = "atualizado"
        else:
            acao = "inalterado"

    conexao.execute(
        """
        INSERT INTO auditoria_lookup
            (acao, tipo_entidade, codigo_natural)
        VALUES (?, 'cliente', ?)
        """,
        (acao, codigo),
    )

    return {"cliente_sk": sk, "acao": acao}


def carregar_clientes(banco, clientes):
    """Carrega a dimensao inteira em uma transacao."""
    codigos = [c["codigo"] for c in clientes]

    if len(codigos) != len(set(codigos)):
        raise ValueError("Codigos duplicados na fonte")

    for cliente in clientes:
        validar_cliente(cliente)

    with closing(conectar(banco)) as conexao:
        with conexao:
            resultados = [
                lookup_cliente(conexao, cliente)
                for cliente in clientes
            ]

    return {
        "inseridos": sum(
            r["acao"] == "inserido" for r in resultados
        ),
        "atualizados": sum(
            r["acao"] == "atualizado" for r in resultados
        ),
        "inalterados": sum(
            r["acao"] == "inalterado" for r in resultados
        ),
    }


def carregar_produtos(banco, produtos):
    """Cria ou atualiza produtos preservando as SKs."""
    codigos = [p["codigo"] for p in produtos]

    if len(codigos) != len(set(codigos)):
        raise ValueError("Produtos duplicados na fonte")

    for p in produtos:
        if (
            not isinstance(p["codigo"], str)
            or not p["codigo"].strip()
            or not isinstance(p["nome"], str)
            or not p["nome"].strip()
        ):
            raise ValueError("Produto invalido")

    with closing(conectar(banco)) as conexao:
        with conexao:
            for p in produtos:
                conexao.execute(
                    """
                    INSERT INTO dim_produtos
                        (codigo_natural, nome)
                    VALUES (?, ?)
                    ON CONFLICT(codigo_natural)
                    DO UPDATE SET nome = excluded.nome
                    """,
                    (p["codigo"], p["nome"].strip()),
                )


def obter_sk(conexao, tabela, codigo):
    """Lookup de fato: codigo natural para chave substituta."""
    permitidas = {
        "dim_clientes": "cliente_sk",
        "dim_produtos": "produto_sk",
    }

    if tabela not in permitidas:
        raise ValueError("Tabela nao permitida")

    coluna = permitidas[tabela]

    resultado = conexao.execute(
        f"""
        SELECT {coluna}
        FROM {tabela}
        WHERE codigo_natural = ?
        """,
        (codigo,),
    ).fetchone()

    if resultado is None:
        raise ValueError(
            f"Lookup sem correspondencia: {tabela}/{codigo}"
        )

    return resultado[0]


def carregar_fatos(banco, vendas):
    """Converte codigos naturais em SKs e insere os fatos."""
    ids = [v["venda_id"] for v in vendas]

    if len(ids) != len(set(ids)):
        raise ValueError("Vendas duplicadas na fonte")

    for venda in vendas:
        if (
            type(venda["venda_id"]) is not int
            or venda["venda_id"] <= 0
            or type(venda["quantidade"]) is not int
            or venda["quantidade"] <= 0
            or type(venda["valor_centavos"]) is not int
            or venda["valor_centavos"] < 0
        ):
            raise ValueError("Medidas ou identificador invalidos")

    inseridos = 0

    with closing(conectar(banco)) as conexao:
        with conexao:
            for venda in vendas:
                cliente_sk = obter_sk(
                    conexao, "dim_clientes", venda["cliente"]
                )
                produto_sk = obter_sk(
                    conexao, "dim_produtos", venda["produto"]
                )

                existente = conexao.execute(
                    """
                    SELECT cliente_sk, produto_sk,
                           quantidade, valor_centavos
                    FROM fato_vendas
                    WHERE venda_id = ?
                    """,
                    (venda["venda_id"],),
                ).fetchone()

                dados = (
                    cliente_sk, produto_sk,
                    venda["quantidade"],
                    venda["valor_centavos"],
                )

                if existente is not None:
                    if tuple(existente) != dados:
                        raise ValueError(
                            "Fato alterado: requer reprocessamento"
                        )
                    continue

                conexao.execute(
                    """
                    INSERT INTO fato_vendas
                        (venda_id, cliente_sk, produto_sk,
                         quantidade, valor_centavos)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (venda["venda_id"], *dados),
                )
                inseridos += 1

    return {"novos_fatos": inseridos}


def listar_clientes(banco):
    with closing(conectar(banco)) as conexao:
        linhas = conexao.execute(
            """
            SELECT cliente_sk, codigo_natural,
                   nome, saldo_centavos
            FROM dim_clientes
            ORDER BY cliente_sk
            """
        ).fetchall()

    return [
        {
            "sk": sk, "codigo": codigo,
            "nome": nome, "saldo_centavos": saldo,
        }
        for sk, codigo, nome, saldo in linhas
    ]


def resumo_fatos(banco):
    with closing(conectar(banco)) as conexao:
        quantidade, unidades, receita = conexao.execute(
            """
            SELECT COUNT(*),
                   COALESCE(SUM(quantidade), 0),
                   COALESCE(SUM(valor_centavos), 0)
            FROM fato_vendas
            """
        ).fetchone()

    return {
        "fatos": quantidade,
        "unidades": unidades,
        "faturamento_centavos": receita,
    }
