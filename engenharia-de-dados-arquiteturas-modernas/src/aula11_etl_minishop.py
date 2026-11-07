"""Aula 11 - ETL da Minishop.

Extract: OLTP somente leitura.
Transform: validacao, normalizacao e lookups.
Load: dimensoes SCD2, fatos incrementais e auditoria.

O banco da Aula 10 nao e alterado.
"""

import sqlite3
from contextlib import closing
from datetime import date, datetime, timezone
from pathlib import Path


BASE = Path(__file__).resolve().parent.parent
SCHEMA = BASE / "sql" / "aula11_etl.sql"


def conectar(banco):
    conexao = sqlite3.connect(str(banco), timeout=10)
    conexao.execute("PRAGMA foreign_keys = ON")
    return conexao


def extrair(banco_oltp):
    """E: extrai vendas confirmadas e pagas."""
    origem = Path(banco_oltp).resolve()

    if not origem.is_file():
        raise FileNotFoundError(origem)

    with closing(
        sqlite3.connect(
            origem.as_uri() + "?mode=ro",
            uri=True,
        )
    ) as conexao:
        conexao.row_factory = sqlite3.Row

        registros = conexao.execute(
            """
            SELECT
                p.pedido_id,
                p.cliente_id,
                c.nome AS cliente_nome,
                i.produto_id,
                pr.nome AS produto_nome,
                ca.nome AS categoria,
                substr(p.data_pedido, 1, 10) AS data,
                i.quantidade,
                i.quantidade * i.preco_unitario_centavos
                    AS valor_centavos
            FROM pedidos p
            JOIN clientes c
              ON c.cliente_id = p.cliente_id
            JOIN itens_pedido i
              ON i.pedido_id = p.pedido_id
            JOIN produtos pr
              ON pr.produto_id = i.produto_id
            JOIN categorias ca
              ON ca.categoria_id = pr.categoria_id
            JOIN pagamentos pg
              ON pg.pedido_id = p.pedido_id
            WHERE p.estado = 'confirmado'
              AND pg.estado = 'aprovado'
            ORDER BY p.pedido_id, i.produto_id
            """
        ).fetchall()

    return [dict(r) for r in registros]


def transformar(registros):
    """T: valida e padroniza antes da carga."""
    resultado = []
    chaves = set()

    for original in registros:
        venda = dict(original)

        for campo in (
            "cliente_nome", "produto_nome", "categoria"
        ):
            valor = venda.get(campo)

            if not isinstance(valor, str) or not valor.strip():
                raise ValueError(
                    f"Campo obrigatorio invalido: {campo}"
                )

            venda[campo] = valor.strip()

        if (
            type(venda["quantidade"]) is not int
            or venda["quantidade"] <= 0
        ):
            raise ValueError("Quantidade invalida")

        if (
            type(venda["valor_centavos"]) is not int
            or venda["valor_centavos"] < 0
        ):
            raise ValueError("Valor invalido")

        if any(
            type(venda[campo]) is not int
            or venda[campo] <= 0
            for campo in (
                "pedido_id", "cliente_id", "produto_id"
            )
        ):
            raise ValueError("Identificador invalido")

        try:
            venda["data"] = date.fromisoformat(
                venda["data"]
            ).isoformat()
        except (ValueError, TypeError) as erro:
            raise ValueError("Data invalida") from erro

        chave = (
            venda["pedido_id"],
            venda["produto_id"],
        )

        if chave in chaves:
            raise ValueError("Venda duplicada na extracao")

        chaves.add(chave)
        resultado.append(venda)

    return resultado


def lookup_scd2(
    conexao,
    tabela,
    coluna_origem,
    identificador,
    atributos,
    instante,
):
    """Localiza a SK ativa ou cria uma versao SCD Tipo 2."""
    if tabela not in {"dim_cliente", "dim_produto"}:
        raise ValueError("Dimensao nao permitida")

    colunas = {
        "dim_cliente": ["nome"],
        "dim_produto": ["nome", "categoria"],
    }[tabela]

    valores = tuple(atributos[c] for c in colunas)

    atual = conexao.execute(
        f"""
        SELECT *
        FROM {tabela}
        WHERE {coluna_origem} = ?
          AND ativo = 1
        """,
        (identificador,),
    ).fetchone()

    if atual is not None:
        existentes = tuple(
            atual[i + 2]
            for i in range(len(colunas))
        )

        if existentes == valores:
            return atual[0], False

        nova_versao = atual[len(colunas) + 2] + 1

        conexao.execute(
            f"""
            UPDATE {tabela}
            SET ativo = 0, valido_ate = ?
            WHERE {coluna_origem} = ?
              AND ativo = 1
            """,
            (instante, identificador),
        )

    else:
        nova_versao = 1

    campos = ", ".join(colunas)
    marcadores = ", ".join("?" for _ in colunas)

    nova_sk = conexao.execute(
        f"""
        INSERT INTO {tabela}
        ({coluna_origem}, {campos},
         versao, valido_desde, valido_ate, ativo)
        VALUES (?, {marcadores}, ?, ?, NULL, 1)
        """,
        (
            identificador,
            *valores,
            nova_versao,
            instante,
        ),
    ).lastrowid

    return nova_sk, True


def lookup_tempo(conexao, valor):
    """Reutiliza a SK da data ou cria uma nova."""
    atual = conexao.execute(
        """
        SELECT tempo_sk
        FROM dim_tempo
        WHERE data = ?
        """,
        (valor,),
    ).fetchone()

    if atual:
        return atual[0]

    d = date.fromisoformat(valor)

    return conexao.execute(
        """
        INSERT INTO dim_tempo
        (data, ano, mes, dia)
        VALUES (?, ?, ?, ?)
        """,
        (valor, d.year, d.month, d.day),
    ).lastrowid


def carregar(banco_dw, vendas):
    """L: executa carga transacional e preserva fatos historicos."""
    destino = Path(banco_dw).resolve()
    destino.parent.mkdir(parents=True, exist_ok=True)

    with closing(conectar(destino)) as conexao:
        conexao.executescript(
            SCHEMA.read_text(encoding="utf-8")
        )

        instante = datetime.now(
            timezone.utc
        ).isoformat(timespec="microseconds")

        try:
            conexao.execute("BEGIN IMMEDIATE")

            anteriores = conexao.execute(
                "SELECT COUNT(*) FROM etl_cargas"
            ).fetchone()[0]

            tipo = (
                "inicial" if anteriores == 0
                else "incremental"
            )

            novos_fatos = 0
            novas_versoes = 0

            # Lookups das dimensoes antes dos fatos.
            # As vendas historicas ja carregadas mantem suas SKs.
            mapa_clientes = {}
            mapa_produtos = {}

            for venda in vendas:
                cliente_id = venda["cliente_id"]
                produto_id = venda["produto_id"]

                atributos_cliente = {
                    "nome": venda["cliente_nome"],
                }

                atributos_produto = {
                    "nome": venda["produto_nome"],
                    "categoria": venda["categoria"],
                }

                if cliente_id in mapa_clientes:
                    sk_cliente = mapa_clientes[cliente_id]
                else:
                    sk_cliente, criada = lookup_scd2(
                        conexao,
                        "dim_cliente",
                        "cliente_id_origem",
                        cliente_id,
                        atributos_cliente,
                        instante,
                    )
                    mapa_clientes[cliente_id] = sk_cliente
                    novas_versoes += int(criada)

                if produto_id in mapa_produtos:
                    sk_produto = mapa_produtos[produto_id]
                else:
                    sk_produto, criada = lookup_scd2(
                        conexao,
                        "dim_produto",
                        "produto_id_origem",
                        produto_id,
                        atributos_produto,
                        instante,
                    )
                    mapa_produtos[produto_id] = sk_produto
                    novas_versoes += int(criada)

            for venda in vendas:
                chave = (
                    venda["pedido_id"],
                    venda["produto_id"],
                )

                existente = conexao.execute(
                    """
                    SELECT
                        quantidade,
                        valor_centavos
                    FROM fato_vendas
                    WHERE pedido_id_origem = ?
                      AND produto_id_origem = ?
                    """,
                    chave,
                ).fetchone()

                if existente is not None:
                    # Correcoes retroativas precisam de
                    # uma politica propria de reprocessamento.
                    if existente != (
                        venda["quantidade"],
                        venda["valor_centavos"],
                    ):
                        raise ValueError(
                            "Fato ja carregado sofreu alteracao; "
                            "reprocessamento necessario"
                        )

                    continue

                tempo_sk = lookup_tempo(
                    conexao,
                    venda["data"],
                )

                conexao.execute(
                    """
                    INSERT INTO fato_vendas (
                        pedido_id_origem,
                        produto_id_origem,
                        cliente_sk,
                        produto_sk,
                        tempo_sk,
                        quantidade,
                        valor_centavos
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        venda["pedido_id"],
                        venda["produto_id"],
                        mapa_clientes[venda["cliente_id"]],
                        mapa_produtos[venda["produto_id"]],
                        tempo_sk,
                        venda["quantidade"],
                        venda["valor_centavos"],
                    ),
                )

                novos_fatos += 1

            conexao.execute(
                """
                INSERT INTO etl_cargas (
                    executado_em, tipo,
                    origem_linhas, novos_fatos, novas_versoes
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    instante,
                    tipo,
                    len(vendas),
                    novos_fatos,
                    novas_versoes,
                ),
            )

            conexao.commit()

        except Exception:
            conexao.rollback()
            raise

    return {
        "tipo": tipo,
        "origem_linhas": len(vendas),
        "novos_fatos": novos_fatos,
        "novas_versoes": novas_versoes,
    }


def executar_etl(banco_oltp, banco_dw):
    """Orquestra Extract, Transform e Load."""
    origem = Path(banco_oltp).resolve()
    destino = Path(banco_dw).resolve()

    if origem == destino:
        raise ValueError("OLTP e DW devem ser diferentes")

    brutos = extrair(origem)
    preparados = transformar(brutos)

    resultado = carregar(destino, preparados)

    return {
        "extract": len(brutos),
        "transform": len(preparados),
        "load": resultado,
    }


def indicadores(banco_dw):
    """Consulta indicadores da tabela de fatos."""
    with closing(conectar(banco_dw)) as conexao:
        fatos, pedidos, unidades, receita = conexao.execute(
            """
            SELECT
                COUNT(*),
                COUNT(DISTINCT pedido_id_origem),
                COALESCE(SUM(quantidade), 0),
                COALESCE(SUM(valor_centavos), 0)
            FROM fato_vendas
            """
        ).fetchone()

        cargas = conexao.execute(
            "SELECT COUNT(*) FROM etl_cargas"
        ).fetchone()[0]

        versoes_clientes = conexao.execute(
            "SELECT COUNT(*) FROM dim_cliente"
        ).fetchone()[0]

        versoes_produtos = conexao.execute(
            "SELECT COUNT(*) FROM dim_produto"
        ).fetchone()[0]

    return {
        "fatos": fatos,
        "pedidos": pedidos,
        "unidades": unidades,
        "faturamento_centavos": receita,
        "cargas": cargas,
        "versoes_clientes": versoes_clientes,
        "versoes_produtos": versoes_produtos,
    }


def historico_cliente(banco_dw, cliente_id):
    """Inspeciona versoes historicas da dimensao cliente."""
    with closing(conectar(banco_dw)) as conexao:
        registros = conexao.execute(
            """
            SELECT cliente_sk, nome, versao, ativo
            FROM dim_cliente
            WHERE cliente_id_origem = ?
            ORDER BY versao
            """,
            (cliente_id,),
        ).fetchall()

    return [
        {
            "cliente_sk": sk,
            "nome": nome,
            "versao": versao,
            "ativo": bool(ativo),
        }
        for sk, nome, versao, ativo in registros
    ]
