"""Aula 13 - Slowly Changing Dimensions.

SCD1: sobrescreve cidade, mantendo a SK.
SCD2: versiona cidade, gerando uma nova SK.
Lookup historico: codigo natural + data do evento.

Laboratorio independente, sem modificar o OLTP.
"""

import sqlite3
from contextlib import closing
from datetime import date
from pathlib import Path


BASE = Path(__file__).resolve().parent.parent
SCHEMA = BASE / "sql" / "aula13_slowly_changing_dimensions.sql"

CLIENTE = "23400"
INICIO_HISTORICO = "1900-01-01"
DATA_MUDANCA = "2024-05-01"


def validar_data(valor):
    if not isinstance(valor, str):
        raise ValueError("Data deve ser texto ISO")

    try:
        normalizada = date.fromisoformat(valor).isoformat()
    except ValueError as erro:
        raise ValueError("Data invalida") from erro

    if normalizada != valor:
        raise ValueError("Use data YYYY-MM-DD")

    return valor


def validar_cliente(codigo, cidade):
    if not isinstance(codigo, str) or not codigo.strip():
        raise ValueError("Codigo natural invalido")
    if not isinstance(cidade, str) or not cidade.strip():
        raise ValueError("Cidade invalida")


def conectar(banco):
    conexao = sqlite3.connect(str(banco), timeout=10)
    conexao.execute("PRAGMA foreign_keys = ON")
    return conexao


def preparar_banco(banco):
    """Cria tabelas ausentes sem descartar registros existentes."""
    banco = Path(banco)
    banco.parent.mkdir(parents=True, exist_ok=True)

    with closing(conectar(banco)) as conexao:
        conexao.executescript(
            SCHEMA.read_text(encoding="utf-8")
        )


def atualizar_scd1(banco, codigo, cidade):
    """Sobrescreve cidade, reutilizando a mesma SK."""
    validar_cliente(codigo, cidade)
    cidade = cidade.strip()

    with closing(conectar(banco)) as conexao:
        with conexao:
            existente = conexao.execute(
                """
                SELECT cliente_sk
                FROM cliente_scd1
                WHERE codigo_natural = ?
                """,
                (codigo,),
            ).fetchone()

            if existente is None:
                sk = conexao.execute(
                    """
                    INSERT INTO cliente_scd1
                    (codigo_natural, cidade)
                    VALUES (?, ?)
                    """,
                    (codigo, cidade),
                ).lastrowid
            else:
                sk = existente[0]
                conexao.execute(
                    """
                    UPDATE cliente_scd1
                    SET cidade = ?
                    WHERE cliente_sk = ?
                    """,
                    (cidade, sk),
                )

    return sk


def iniciar_scd2(banco, codigo, cidade, inicio):
    """Registra a primeira versao ou valida sua existencia."""
    validar_cliente(codigo, cidade)
    validar_data(inicio)

    with closing(conectar(banco)) as conexao:
        with conexao:
            primeira = conexao.execute(
                """
                SELECT cliente_sk, cidade, inicio
                FROM cliente_scd2
                WHERE codigo_natural = ?
                ORDER BY inicio
                LIMIT 1
                """,
                (codigo,),
            ).fetchone()

            if primeira is not None:
                if primeira[1:] != (cidade.strip(), inicio):
                    raise ValueError(
                        "Versao inicial diferente da existente"
                    )
                return primeira[0]

            return conexao.execute(
                """
                INSERT INTO cliente_scd2
                (codigo_natural, cidade, inicio, fim, atual)
                VALUES (?, ?, ?, NULL, 1)
                """,
                (codigo, cidade.strip(), inicio),
            ).lastrowid


def mudar_cidade(banco, codigo, nova_cidade, inicio):
    """Fecha a versao anterior e cria a proxima sem sobreposicao."""
    validar_cliente(codigo, nova_cidade)
    validar_data(inicio)
    nova_cidade = nova_cidade.strip()

    with closing(conectar(banco)) as conexao:
        with conexao:
            atual = conexao.execute(
                """
                SELECT cliente_sk, cidade, inicio
                FROM cliente_scd2
                WHERE codigo_natural = ? AND atual = 1
                """,
                (codigo,),
            ).fetchone()

            if atual is None:
                raise ValueError("Cliente sem versao ativa")

            sk_anterior, cidade_anterior, inicio_anterior = atual

            if cidade_anterior == nova_cidade:
                return {"alterou": False, "sk": sk_anterior}

            if inicio <= inicio_anterior:
                raise ValueError(
                    "Mudanca fora de ordem ou na mesma data"
                )

            conexao.execute(
                """
                UPDATE cliente_scd2
                SET fim = ?, atual = 0
                WHERE cliente_sk = ?
                """,
                (inicio, sk_anterior),
            )

            nova_sk = conexao.execute(
                """
                INSERT INTO cliente_scd2
                (codigo_natural, cidade, inicio, fim, atual)
                VALUES (?, ?, ?, NULL, 1)
                """,
                (codigo, nova_cidade, inicio),
            ).lastrowid

    return {"alterou": True, "sk": nova_sk}


def buscar_sk_historica(conexao, codigo, data_evento):
    """Lookup correto por codigo natural e data da venda."""
    validar_data(data_evento)

    registros = conexao.execute(
        """
        SELECT cliente_sk
        FROM cliente_scd2
        WHERE codigo_natural = ?
          AND inicio <= ?
          AND (fim IS NULL OR ? < fim)
        """,
        (codigo, data_evento, data_evento),
    ).fetchall()

    if len(registros) != 1:
        raise ValueError(
            "Lookup historico sem versao unica e valida"
        )

    return registros[0][0]


def buscar_sk_atual(banco, codigo):
    """Consulta a SK ativa; nao serve para cargas retroativas."""
    with closing(conectar(banco)) as conexao:
        linha = conexao.execute(
            """
            SELECT cliente_sk
            FROM cliente_scd2
            WHERE codigo_natural = ? AND atual = 1
            """,
            (codigo,),
        ).fetchone()

    if linha is None:
        raise ValueError("Versao ativa inexistente")

    return linha[0]


def registrar_venda(banco, evento, codigo, data_evento, valor):
    """Registra fato nos dois modelos com integridade transacional."""
    validar_data(data_evento)

    if not isinstance(evento, str) or not evento.strip():
        raise ValueError("Evento invalido")

    if type(valor) is not int or valor < 0:
        raise ValueError("Valor invalido")

    with closing(conectar(banco)) as conexao:
        with conexao:
            sk1_linha = conexao.execute(
                """
                SELECT cliente_sk
                FROM cliente_scd1
                WHERE codigo_natural = ?
                """,
                (codigo,),
            ).fetchone()

            if sk1_linha is None:
                raise ValueError("Cliente SCD1 inexistente")

            sk1 = sk1_linha[0]
            sk2 = buscar_sk_historica(
                conexao, codigo, data_evento
            )

            dados = (
                ("vendas_scd1", sk1),
                ("vendas_scd2", sk2),
            )

            for tabela, sk in dados:
                existente = conexao.execute(
                    f"""
                    SELECT cliente_sk, data_venda, valor_centavos
                    FROM {tabela}
                    WHERE evento_id = ?
                    """,
                    (evento,),
                ).fetchone()

                esperado = (sk, data_evento, valor)

                if existente is not None:
                    if tuple(existente) != esperado:
                        raise ValueError(
                            "Evento existente com dados divergentes"
                        )
                    continue

                conexao.execute(
                    f"""
                    INSERT INTO {tabela}
                    (evento_id, cliente_sk, data_venda, valor_centavos)
                    VALUES (?, ?, ?, ?)
                    """,
                    (evento, sk, data_evento, valor),
                )


def faturamento_por_cidade(banco, modelo):
    """Agrupa valores pela cidade associada a cada SK."""
    tabelas = {
        "scd1": ("vendas_scd1", "cliente_scd1"),
        "scd2": ("vendas_scd2", "cliente_scd2"),
    }

    if modelo not in tabelas:
        raise ValueError("Modelo desconhecido")

    fato, dimensao = tabelas[modelo]

    with closing(conectar(banco)) as conexao:
        linhas = conexao.execute(
            f"""
            SELECT d.cidade, SUM(f.valor_centavos)
            FROM {fato} f
            JOIN {dimensao} d
              ON d.cliente_sk = f.cliente_sk
            GROUP BY d.cidade
            ORDER BY d.cidade
            """
        ).fetchall()

    return {cidade: valor for cidade, valor in linhas}


def versoes_cliente(banco, codigo):
    """Exibe a historia e suas datas de vigencia."""
    with closing(conectar(banco)) as conexao:
        linhas = conexao.execute(
            """
            SELECT cliente_sk, cidade, inicio, fim, atual
            FROM cliente_scd2
            WHERE codigo_natural = ?
            ORDER BY inicio
            """,
            (codigo,),
        ).fetchall()

    return [
        {
            "sk": sk,
            "cidade": cidade,
            "inicio": inicio,
            "fim_exclusivo": fim,
            "atual": bool(atual),
        }
        for sk, cidade, inicio, fim, atual in linhas
    ]


def validar_vigencias(banco, codigo):
    """Verifica sequencia sem sobreposicoes ou lacunas."""
    versoes = versoes_cliente(banco, codigo)

    if not versoes:
        return False

    if sum(v["atual"] for v in versoes) != 1:
        return False

    for anterior, seguinte in zip(versoes, versoes[1:]):
        if anterior["fim_exclusivo"] != seguinte["inicio"]:
            return False

    return versoes[-1]["fim_exclusivo"] is None


def executar_exemplo(banco):
    """Reproduz a historia: Niteroi, Santos e carga retroativa."""
    preparar_banco(banco)

    atualizar_scd1(banco, CLIENTE, "Niteroi")
    iniciar_scd2(
        banco, CLIENTE, "Niteroi", INICIO_HISTORICO
    )

    for numero, mes in enumerate(range(1, 5), start=1):
        registrar_venda(
            banco,
            f"VENDA-{numero}",
            CLIENTE,
            f"2024-{mes:02d}-15",
            1000,
        )

    atualizar_scd1(banco, CLIENTE, "Santos")
    mudar_cidade(banco, CLIENTE, "Santos", DATA_MUDANCA)

    registrar_venda(
        banco, "VENDA-MAIO", CLIENTE, "2024-05-15", 1500
    )

    # Acontece DEPOIS da mudanca, mas o evento e antigo.
    registrar_venda(
        banco, "VENDA-RETRO", CLIENTE, "2023-12-15", 1000
    )

    return {
        "scd1": faturamento_por_cidade(banco, "scd1"),
        "scd2": faturamento_por_cidade(banco, "scd2"),
        "versoes": versoes_cliente(banco, CLIENTE),
        "vigencias_validas": validar_vigencias(banco, CLIENTE),
    }
