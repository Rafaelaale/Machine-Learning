"""Aula 17 - Introducao ao Data Lake da Minishop.

Preserva snapshots SQLite do OLTP em uma camada raw.
Disponibiliza tambem representacoes CSV e JSONL.
Materializa resultados analiticos em uma camada curated.

Nenhuma transformacao altera os snapshots de origem.
"""

import csv
import hashlib
import json
import os
import shutil
import sqlite3
import tempfile
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path


BASE = Path(__file__).resolve().parent.parent
LAKE = BASE / "dados" / "lake"


def conectar_somente_leitura(arquivo):
    caminho = Path(arquivo).resolve()

    if not caminho.is_file():
        raise FileNotFoundError(caminho)

    con = sqlite3.connect(
        caminho.as_uri() + "?mode=ro",
        uri=True,
        timeout=10,
    )
    con.row_factory = sqlite3.Row

    return con


def hash_arquivo(arquivo):
    """Calcula SHA-256 sem carregar o arquivo inteiro na memoria."""
    sha = hashlib.sha256()

    with open(arquivo, "rb") as entrada:
        for bloco in iter(
            lambda: entrada.read(1024 * 1024),
            b"",
        ):
            sha.update(bloco)

    return sha.hexdigest()


def tabelas_usuario(con):
    return [
        r[0]
        for r in con.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
              AND name NOT LIKE 'sqlite_%'
            ORDER BY name
            """
        ).fetchall()
    ]


def assinatura_conteudo(banco):
    """Identifica o estado logico das tabelas do SQLite.

    A assinatura independe da organizacao fisica das
    paginas no arquivo SQLite.
    """
    sha = hashlib.sha256()

    with closing(conectar_somente_leitura(banco)) as con:
        for tabela in tabelas_usuario(con):
            sha.update(
                tabela.encode("utf-8") + b"\n"
            )

            colunas = con.execute(
                f'PRAGMA table_info("{tabela}")'
            ).fetchall()

            nomes = [c["name"] for c in colunas]

            sha.update(
                json.dumps(
                    nomes, ensure_ascii=False
                ).encode("utf-8")
            )

            registros = con.execute(
                f'SELECT * FROM "{tabela}" ORDER BY rowid'
            )

            for registro in registros:
                linha = dict(registro)

                sha.update(
                    json.dumps(
                        linha,
                        sort_keys=True,
                        ensure_ascii=False,
                        separators=(",", ":"),
                    ).encode("utf-8")
                )
                sha.update(b"\n")

    return sha.hexdigest()


def linhas_tabela(con, tabela):
    """Le tabela por inteiro somente para o laboratorio."""
    permitidas = set(tabelas_usuario(con))

    if tabela not in permitidas:
        raise ValueError("Tabela inexistente")

    return [
        dict(r)
        for r in con.execute(
            f'SELECT * FROM "{tabela}" ORDER BY rowid'
        )
    ]


def salvar_jsonl(caminho, linhas):
    with open(caminho, "w", encoding="utf-8", newline="") as saida:
        for linha in linhas:
            saida.write(
                json.dumps(
                    linha,
                    ensure_ascii=False,
                    sort_keys=True,
                ) + "\n"
            )


def salvar_csv(caminho, linhas, colunas):
    with open(caminho, "w", encoding="utf-8", newline="") as saida:
        escritor = csv.DictWriter(
            saida,
            fieldnames=colunas,
        )
        escritor.writeheader()
        escritor.writerows(linhas)


def ler_pedidos_jsonl(caminho):
    """Schema on Read: interpreta JSONL na leitura.

    Valida campos minimos somente no momento do consumo.
    """
    registros = []

    with open(caminho, "r", encoding="utf-8") as entrada:
        for numero, linha in enumerate(entrada, start=1):
            if not linha.strip():
                continue

            try:
                registro = json.loads(linha)
            except json.JSONDecodeError as erro:
                raise ValueError(
                    f"JSON invalido na linha {numero}"
                ) from erro

            if not isinstance(registro, dict):
                raise ValueError("Registro JSON nao e um objeto")

            obrigatorios = {
                "pedido_id",
                "cliente_id",
                "data_pedido",
            }

            if not obrigatorios.issubset(registro):
                raise ValueError(
                    "Esquema de pedido incompleto"
                )

            registros.append(registro)

    return registros


def validar_snapshot(pasta):
    """Verifica hashes, contagens e integridade do SQLite."""
    pasta = Path(pasta)

    manifest = json.loads(
        (pasta / "manifest.json").read_text(
            encoding="utf-8"
        )
    )

    for nome, esperado in manifest["arquivos"].items():
        arquivo = pasta / nome

        if not arquivo.is_file():
            raise ValueError(
                f"Arquivo raw ausente: {nome}"
            )

        if hash_arquivo(arquivo) != esperado:
            raise ValueError(
                f"Arquivo raw alterado: {nome}"
            )

    banco = pasta / "oltp.sqlite"

    with closing(conectar_somente_leitura(banco)) as con:
        integridade = con.execute(
            "PRAGMA quick_check"
        ).fetchone()[0]

        if integridade != "ok":
            raise ValueError(
                "Integridade SQLite comprometida"
            )

        for tabela, esperado in manifest["contagens"].items():
            quantidade = con.execute(
                f'SELECT COUNT(*) FROM "{tabela}"'
            ).fetchone()[0]

            if quantidade != esperado:
                raise ValueError(
                    f"Contagem divergente: {tabela}"
                )

    if assinatura_conteudo(banco) != manifest["snapshot_id"]:
        raise ValueError("Assinatura logica divergente")

    return True


def ingerir(oltp, lake=LAKE):
    """Captura o OLTP e cria snapshot raw imutavel por convencao.

    A captura usa SQLite Backup API, que fornece uma
    fotografia consistente das transacoes confirmadas.

    O manifest permite detectar alteracoes posteriores.
    """
    origem = Path(oltp).resolve()

    if not origem.is_file():
        raise FileNotFoundError(origem)

    raw = Path(lake) / "raw" / "minishop"
    raw.mkdir(parents=True, exist_ok=True)

    temporario = Path(
        tempfile.mkdtemp(
            prefix=".ingestao_",
            dir=raw,
        )
    )

    try:
        banco_raw = temporario / "oltp.sqlite"

        with closing(
            conectar_somente_leitura(origem)
        ) as fonte:
            with closing(
                sqlite3.connect(str(banco_raw))
            ) as copia:
                fonte.backup(copia)

        snapshot_id = assinatura_conteudo(
            banco_raw
        )

        destino = raw / snapshot_id

        if destino.exists():
            validar_snapshot(destino)

            return {
                "snapshot_id": snapshot_id,
                "pasta": str(destino),
                "novo": False,
            }

        with closing(
            conectar_somente_leitura(banco_raw)
        ) as con:
            clientes = linhas_tabela(con, "clientes")
            pedidos = linhas_tabela(con, "pedidos")

            colunas = [
                c["name"]
                for c in con.execute(
                    "PRAGMA table_info(clientes)"
                ).fetchall()
            ]

            contagens = {
                tabela: con.execute(
                    f'SELECT COUNT(*) FROM "{tabela}"'
                ).fetchone()[0]
                for tabela in tabelas_usuario(con)
            }

        salvar_csv(
            temporario / "clientes.csv",
            clientes,
            colunas,
        )

        salvar_jsonl(
            temporario / "pedidos.jsonl",
            pedidos,
        )

        arquivos = {
            nome: hash_arquivo(
                temporario / nome
            )
            for nome in (
                "oltp.sqlite",
                "clientes.csv",
                "pedidos.jsonl",
            )
        }

        manifest = {
            "dataset": "minishop",
            "camada": "raw",
            "snapshot_id": snapshot_id,
            "capturado_em_utc": datetime.now(
                timezone.utc
            ).isoformat(),
            "fonte": "SQLite OLTP local",
            "arquivos": arquivos,
            "contagens": contagens,
            "observacao": (
                "Dados preservados antes das "
                "transformacoes analiticas"
            ),
        }

        (temporario / "manifest.json").write_text(
            json.dumps(
                manifest,
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        validar_snapshot(temporario)

        # Renomeia a pasta preparada, sem substituir
        # um snapshot anterior.
        os.rename(temporario, destino)

        return {
            "snapshot_id": snapshot_id,
            "pasta": str(destino),
            "novo": True,
        }

    finally:
        if temporario.exists():
            shutil.rmtree(temporario)


def extrair_vendas_do_snapshot(pasta):
    """Schema on Read: interpreta o modelo transacional.

    Os joins e regras de negocio sao aplicados agora,
    nao durante a preservacao do dado bruto.
    """
    validar_snapshot(pasta)

    with closing(
        conectar_somente_leitura(
            Path(pasta) / "oltp.sqlite"
        )
    ) as con:
        linhas = con.execute(
            """
            SELECT
                p.pedido_id,
                p.cliente_id,
                substr(p.data_pedido, 1, 10) AS data,
                i.produto_id,
                pr.nome AS produto,
                i.quantidade,
                i.preco_unitario_centavos,
                i.quantidade * i.preco_unitario_centavos
                    AS valor_centavos
            FROM pedidos p
            JOIN itens_pedido i
              ON i.pedido_id = p.pedido_id
            JOIN produtos pr
              ON pr.produto_id = i.produto_id
            JOIN pagamentos pg
              ON pg.pedido_id = p.pedido_id
            WHERE p.estado = 'confirmado'
              AND pg.estado = 'aprovado'
            ORDER BY p.pedido_id, i.produto_id
            """
        ).fetchall()

    return [dict(r) for r in linhas]


def materializar_curado(pasta_raw, lake=LAKE):
    """Cria analise separada, sem escrever na camada raw."""
    pasta_raw = Path(pasta_raw)
    vendas = extrair_vendas_do_snapshot(pasta_raw)

    manifest = json.loads(
        (pasta_raw / "manifest.json").read_text(
            encoding="utf-8"
        )
    )

    identificador = manifest["snapshot_id"]

    destino = (
        Path(lake) / "curated" / "minishop" / identificador
    )
    destino.mkdir(parents=True, exist_ok=True)

    resumo = {
        "snapshot_id": identificador,
        "itens_vendidos": len(vendas),
        "quantidade_vendida": sum(
            v["quantidade"] for v in vendas
        ),
        "faturamento_centavos": sum(
            v["valor_centavos"] for v in vendas
        ),
    }

    (destino / "resumo_vendas.json").write_text(
        json.dumps(
            resumo, indent=2, ensure_ascii=False
        ),
        encoding="utf-8",
    )

    colunas = [
        "pedido_id",
        "cliente_id",
        "data",
        "produto_id",
        "produto",
        "quantidade",
        "preco_unitario_centavos",
        "valor_centavos",
    ]

    salvar_csv(
        destino / "vendas_tratadas.csv",
        vendas,
        colunas,
    )

    return {
        "pasta": str(destino),
        "resumo": resumo,
    }


def listar_snapshots(lake=LAKE):
    """Localiza os snapshots preservados."""
    raw = Path(lake) / "raw" / "minishop"

    if not raw.exists():
        return []

    return [
        str(p)
        for p in sorted(raw.iterdir())
        if p.is_dir()
        and (p / "manifest.json").is_file()
    ]
