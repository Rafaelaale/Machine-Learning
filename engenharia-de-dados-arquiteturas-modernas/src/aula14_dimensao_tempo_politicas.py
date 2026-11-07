"""Aula 14 - Dimensao Tempo e reprocessamento por periodo.

Implementa:
- SK de data AAAAMMDD;
- calendario continuo entre limites dos fatos;
- reprocessamento atomico de periodo completo;
- correcoes, inclusoes e exclusoes;
- extracao somente leitura do OLTP da Minishop.
"""

import calendar
import sqlite3
from contextlib import closing
from datetime import date, datetime, timedelta, timezone
from pathlib import Path


BASE = Path(__file__).resolve().parent.parent
SCHEMA = BASE / "sql" / "aula14_dimensao_tempo_politicas.sql"


def conectar(banco):
    conexao = sqlite3.connect(str(banco), timeout=10)
    conexao.execute("PRAGMA foreign_keys = ON")
    return conexao


def preparar_banco(banco):
    banco = Path(banco)
    banco.parent.mkdir(parents=True, exist_ok=True)

    with closing(conectar(banco)) as conexao:
        conexao.executescript(
            SCHEMA.read_text(encoding="utf-8")
        )


def validar_data(valor):
    if not isinstance(valor, str):
        raise ValueError("Data deve ser texto")

    try:
        data = date.fromisoformat(valor)
    except ValueError as erro:
        raise ValueError("Data invalida") from erro

    if data.isoformat() != valor:
        raise ValueError("Use o formato YYYY-MM-DD")

    return data


def chave_tempo(valor):
    """Converte uma data em chave numerica AAAAMMDD."""
    data = validar_data(valor)
    return int(data.strftime("%Y%m%d"))


def limites_mes(ano, mes):
    if (
        type(ano) is not int
        or type(mes) is not int
        or not (1 <= ano <= 9999)
        or not (1 <= mes <= 12)
    ):
        raise ValueError("Ano ou mes invalido")

    ultimo = calendar.monthrange(ano, mes)[1]

    return (
        date(ano, mes, 1),
        date(ano, mes, ultimo),
    )


def registrar_cliente(banco, codigo, nome):
    """Cadastra ou atualiza dimensao cliente Tipo 1."""
    if not isinstance(codigo, str) or not codigo.strip():
        raise ValueError("Codigo natural invalido")

    if not isinstance(nome, str) or not nome.strip():
        raise ValueError("Nome invalido")

    with closing(conectar(banco)) as conexao:
        with conexao:
            conexao.execute(
                """
                INSERT INTO dim_cliente
                (codigo_natural, nome)
                VALUES (?, ?)
                ON CONFLICT(codigo_natural)
                DO UPDATE SET nome = excluded.nome
                """,
                (codigo, nome.strip()),
            )


def inserir_data(conexao, dia):
    """Insere uma data sem duplicar a chave."""
    sk = int(dia.strftime("%Y%m%d"))

    conexao.execute(
        """
        INSERT OR IGNORE INTO dim_tempo (
            tempo_sk, data, dia, mes, ano,
            trimestre, semestre, dia_semana, fim_semana
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            sk,
            dia.isoformat(),
            dia.day,
            dia.month,
            dia.year,
            (dia.month - 1) // 3 + 1,
            (dia.month - 1) // 6 + 1,
            dia.weekday(),
            int(dia.weekday() >= 5),
        ),
    )


def sincronizar_calendario(conexao, incluir_datas=()):
    """Mantem dias continuos no intervalo de fatos.

    incluir_datas permite adicionar primeiro as datas do
    lote novo, antes da insercao dos fatos, preservando FK.
    """
    datas = [
        date.fromisoformat(r[0])
        for r in conexao.execute(
            """
            SELECT data
            FROM dim_tempo
            WHERE tempo_sk IN (
                SELECT DISTINCT tempo_sk
                FROM fato_movimentos
            )
            """
        ).fetchall()
    ]

    datas.extend(incluir_datas)

    if not datas:
        conexao.execute("DELETE FROM dim_tempo")
        return 0

    inicio = min(datas)
    fim = max(datas)
    atual = inicio

    while atual <= fim:
        inserir_data(conexao, atual)
        atual += timedelta(days=1)

    # Datas fora do intervalo dos fatos nao sao necessarias.
    conexao.execute(
        """
        DELETE FROM dim_tempo
        WHERE data < ? OR data > ?
        """,
        (inicio.isoformat(), fim.isoformat()),
    )

    return (fim - inicio).days + 1


def validar_lote(ano, mes, movimentos):
    """Valida um snapshot completo antes de alterar o DW."""
    inicio, fim = limites_mes(ano, mes)

    if not isinstance(movimentos, (list, tuple)):
        raise ValueError("Lote deve ser lista ou tupla")

    ids = set()
    preparados = []

    for movimento in movimentos:
        if not isinstance(movimento, dict):
            raise ValueError("Movimento invalido")

        identificador = movimento.get("movimento_id")
        codigo = movimento.get("cliente")
        valor = movimento.get("valor_centavos")

        if (
            not isinstance(identificador, str)
            or not identificador.strip()
        ):
            raise ValueError("ID do movimento invalido")

        if not isinstance(codigo, str) or not codigo.strip():
            raise ValueError("Codigo do cliente invalido")

        if type(valor) is not int or valor < 0:
            raise ValueError("Valor do movimento invalido")

        data_evento = validar_data(
            movimento.get("data")
        )

        if not (inicio <= data_evento <= fim):
            raise ValueError("Movimento fora do periodo declarado")

        if identificador in ids:
            raise ValueError("Movimento duplicado no lote")

        ids.add(identificador)

        preparados.append({
            "movimento_id": identificador,
            "cliente": codigo,
            "data": data_evento,
            "valor_centavos": valor,
        })

    return inicio, fim, preparados


def reprocessar_periodo(
    banco, ano, mes, movimentos, lote_completo=False
):
    """Substitui atomicamente TODOS os fatos do mes.

    ATENCAO: movimentos precisa representar a fotografia
    integral do periodo, nao apenas as alteracoes.

    Um lote vazio e valido: exclui todos os fatos do mes.
    """
    if lote_completo is not True:
        raise ValueError(
            "Reprocessamento requer lote_completo=True"
        )

    inicio, fim, preparados = validar_lote(
        ano, mes, movimentos
    )

    with closing(conectar(banco)) as conexao:
        try:
            conexao.execute("BEGIN IMMEDIATE")

            # IDs de outros periodos nao podem ser reaproveitados.
            for item in preparados:
                outra_data = conexao.execute(
                    """
                    SELECT t.data
                    FROM fato_movimentos f
                    JOIN dim_tempo t
                      ON t.tempo_sk = f.tempo_sk
                    WHERE f.movimento_id = ?
                    """,
                    (item["movimento_id"],),
                ).fetchone()

                if outra_data is not None:
                    data_anterior = date.fromisoformat(
                        outra_data[0]
                    )

                    if not (inicio <= data_anterior <= fim):
                        raise ValueError(
                            "ID existente em outro periodo"
                        )

            # O lookup dos clientes acontece ANTES do DELETE.
            chaves_clientes = {}

            for item in preparados:
                codigo = item["cliente"]

                if codigo in chaves_clientes:
                    continue

                resultado = conexao.execute(
                    """
                    SELECT cliente_sk
                    FROM dim_cliente
                    WHERE codigo_natural = ?
                    """,
                    (codigo,),
                ).fetchone()

                if resultado is None:
                    raise ValueError(
                        f"Cliente sem lookup: {codigo}"
                    )

                chaves_clientes[codigo] = resultado[0]

            anteriores, total_anterior = conexao.execute(
                """
                SELECT COUNT(*),
                       COALESCE(SUM(f.valor_centavos), 0)
                FROM fato_movimentos f
                JOIN dim_tempo t ON t.tempo_sk = f.tempo_sk
                WHERE t.data BETWEEN ? AND ?
                """,
                (inicio.isoformat(), fim.isoformat()),
            ).fetchone()

            conexao.execute(
                """
                DELETE FROM fato_movimentos
                WHERE tempo_sk IN (
                    SELECT tempo_sk
                    FROM dim_tempo
                    WHERE data BETWEEN ? AND ?
                )
                """,
                (inicio.isoformat(), fim.isoformat()),
            )

            # Considera datas ainda presentes em outros periodos,
            # mais as novas datas trazidas pelo lote.
            sincronizar_calendario(
                conexao,
                [item["data"] for item in preparados],
            )

            for item in preparados:
                conexao.execute(
                    """
                    INSERT INTO fato_movimentos (
                        movimento_id,
                        cliente_sk,
                        tempo_sk,
                        valor_centavos
                    )
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        item["movimento_id"],
                        chaves_clientes[item["cliente"]],
                        chave_tempo(item["data"].isoformat()),
                        item["valor_centavos"],
                    ),
                )

            total_novo = sum(
                item["valor_centavos"]
                for item in preparados
            )

            conexao.execute(
                """
                INSERT INTO etl_periodos (
                    ano, mes, inicio, fim,
                    linhas_anteriores, linhas_novas,
                    total_anterior_centavos,
                    total_novo_centavos, executado_em
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    ano,
                    mes,
                    inicio.isoformat(),
                    fim.isoformat(),
                    anteriores,
                    len(preparados),
                    total_anterior,
                    total_novo,
                    datetime.now(timezone.utc).isoformat(),
                ),
            )

            # Ajusta extremos apos a carga.
            sincronizar_calendario(conexao)

            conexao.commit()

        except Exception:
            conexao.rollback()
            raise

    return {
        "periodo": f"{ano:04d}-{mes:02d}",
        "linhas_anteriores": anteriores,
        "linhas_novas": len(preparados),
        "total_anterior_centavos": total_anterior,
        "total_novo_centavos": total_novo,
    }


def extrair_periodo_oltp(banco_origem, ano, mes):
    """Extrai fotografia completa de vendas pagas da Minishop.

    Nao cria nem modifica tabelas operacionais.
    """
    inicio, fim = limites_mes(ano, mes)
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

        registros = conexao.execute(
            """
            SELECT
                p.pedido_id,
                i.produto_id,
                p.cliente_id,
                substr(p.data_pedido, 1, 10) AS data,
                i.quantidade * i.preco_unitario_centavos
                    AS valor_centavos
            FROM pedidos p
            JOIN itens_pedido i
              ON i.pedido_id = p.pedido_id
            JOIN pagamentos pg
              ON pg.pedido_id = p.pedido_id
            WHERE p.estado = 'confirmado'
              AND pg.estado = 'aprovado'
              AND substr(p.data_pedido, 1, 10)
                  BETWEEN ? AND ?
            ORDER BY p.pedido_id, i.produto_id
            """,
            (inicio.isoformat(), fim.isoformat()),
        ).fetchall()

        clientes = conexao.execute(
            """
            SELECT cliente_id, nome
            FROM clientes
            """
        ).fetchall()

    nomes = {
        str(r["cliente_id"]): r["nome"]
        for r in clientes
    }

    movimentos = [
        {
            "movimento_id": (
                f"PED-{r['pedido_id']}-PROD-{r['produto_id']}"
            ),
            "cliente": str(r["cliente_id"]),
            "data": r["data"],
            "valor_centavos": r["valor_centavos"],
        }
        for r in registros
    ]

    return {
        "ano": ano,
        "mes": mes,
        "movimentos": movimentos,
        "clientes": nomes,
    }


def importar_periodo_oltp(
    banco_origem, banco_destino, ano, mes
):
    """Extrai OLTP, cadastra clientes e reprocessa o mes."""
    origem = Path(banco_origem).resolve()
    destino = Path(banco_destino).resolve()

    if origem == destino:
        raise ValueError("Origem e destino devem ser distintos")

    dados = extrair_periodo_oltp(origem, ano, mes)
    preparar_banco(destino)

    for codigo, nome in dados["clientes"].items():
        registrar_cliente(destino, codigo, nome)

    return reprocessar_periodo(
        destino,
        ano,
        mes,
        dados["movimentos"],
        lote_completo=True,
    )


def consultar_resumo(banco):
    with closing(conectar(banco)) as conexao:
        fatos, total = conexao.execute(
            """
            SELECT COUNT(*),
                   COALESCE(SUM(valor_centavos), 0)
            FROM fato_movimentos
            """
        ).fetchone()

        dias = conexao.execute(
            "SELECT COUNT(*) FROM dim_tempo"
        ).fetchone()[0]

        extremos = conexao.execute(
            """
            SELECT MIN(data), MAX(data)
            FROM dim_tempo
            """
        ).fetchone()

        cargas = conexao.execute(
            "SELECT COUNT(*) FROM etl_periodos"
        ).fetchone()[0]

    return {
        "fatos": fatos,
        "total_centavos": total,
        "dias_calendario": dias,
        "primeira_data": extremos[0],
        "ultima_data": extremos[1],
        "cargas": cargas,
    }


def valores_por_mes(banco):
    with closing(conectar(banco)) as conexao:
        linhas = conexao.execute(
            """
            SELECT substr(t.data, 1, 7),
                   SUM(f.valor_centavos)
            FROM fato_movimentos f
            JOIN dim_tempo t
              ON t.tempo_sk = f.tempo_sk
            GROUP BY substr(t.data, 1, 7)
            ORDER BY substr(t.data, 1, 7)
            """
        ).fetchall()

    return {periodo: valor for periodo, valor in linhas}


def serie_diaria(banco):
    """Retorna tambem dias sem fatos, com valor zero."""
    with closing(conectar(banco)) as conexao:
        linhas = conexao.execute(
            """
            SELECT
                t.data,
                COALESCE(SUM(f.valor_centavos), 0)
            FROM dim_tempo t
            LEFT JOIN fato_movimentos f
              ON f.tempo_sk = t.tempo_sk
            GROUP BY t.data
            ORDER BY t.data
            """
        ).fetchall()

    return [
        {"data": data, "valor_centavos": valor}
        for data, valor in linhas
    ]
