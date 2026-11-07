"""Aula 20 - Criando o Data Lake do Minishop.

Fluxos:
1. OLTP -> snapshot raw preservado (Aula 17).
2. Snapshot -> Bronze por dominio.
3. Bronze -> Silver com joins e particoes mensais.
4. Silver -> Gold com indicadores mensais.
5. Silver -> Data Warehouse dimensional (Aulas 15 e 16).

Parquet e Avro sao gerados quando as bibliotecas
reais pyarrow e fastavro estiverem disponiveis.
"""

import json
import os
import shutil
import tempfile
from collections import defaultdict
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path

from src.aula17_data_lake import (
    LAKE,
    ingerir,
    validar_snapshot,
    conectar_somente_leitura,
    hash_arquivo,
)
from src.aula16_orquestracao_etl import (
    preparar_dw,
    carregar_dimensoes,
    carregar_fatos,
    indicadores,
    validar_periodo,
)
from src.aula15_arquitetura_etl import conectar


BASE = Path(__file__).resolve().parent.parent

DOMINIOS = {
    "cliente": ("clientes",),
    "vendas": (
        "produtos", "categorias",
        "pedidos", "itens_pedido", "pagamentos",
    ),
    "financeiro": ("faturas",),
    "logistica": ("estoque", "movimentos_estoque"),
}


def escrever_jsonl(arquivo, registros):
    arquivo = Path(arquivo)
    arquivo.parent.mkdir(parents=True, exist_ok=True)

    with arquivo.open(
        "w", encoding="utf-8", newline=""
    ) as saida:
        for registro in registros:
            saida.write(
                json.dumps(
                    registro,
                    sort_keys=True,
                    ensure_ascii=False,
                ) + "\n"
            )


def ler_jsonl(arquivo):
    dados = []

    with Path(arquivo).open(
        "r", encoding="utf-8"
    ) as entrada:
        for numero, linha in enumerate(entrada, 1):
            if not linha.strip():
                continue

            try:
                item = json.loads(linha)
            except json.JSONDecodeError as erro:
                raise ValueError(
                    f"JSONL invalido: linha {numero}"
                ) from erro

            if not isinstance(item, dict):
                raise ValueError("Registro nao e um objeto")

            dados.append(item)

    return dados


def publicar_manifesto(pasta, camada, snapshot_id):
    pasta = Path(pasta)

    arquivos = {
        item.relative_to(pasta).as_posix():
            hash_arquivo(item)
        for item in sorted(pasta.rglob("*"))
        if item.is_file()
        and item.name != "manifest.json"
    }

    manifesto = {
        "camada": camada,
        "snapshot_id": snapshot_id,
        "criado_em_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "arquivos": arquivos,
    }

    (pasta / "manifest.json").write_text(
        json.dumps(
            manifesto,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def validar_camada(pasta, camada):
    pasta = Path(pasta)
    arquivo = pasta / "manifest.json"

    if not arquivo.is_file():
        raise ValueError("Manifesto ausente")

    manifesto = json.loads(
        arquivo.read_text(encoding="utf-8")
    )

    if manifesto.get("camada") != camada:
        raise ValueError("Camada incorreta")

    arquivos = manifesto.get("arquivos")

    if not isinstance(arquivos, dict) or not arquivos:
        raise ValueError("Manifesto de arquivos invalido")

    for nome, esperado in arquivos.items():
        relativo = Path(nome)

        if relativo.is_absolute() or ".." in relativo.parts:
            raise ValueError("Caminho invalido no manifesto")

        destino = pasta / relativo

        if (
            not destino.is_file()
            or hash_arquivo(destino) != esperado
        ):
            raise ValueError(
                "Arquivo ausente ou modificado: " + nome
            )

    presentes = {
        p.relative_to(pasta).as_posix()
        for p in pasta.rglob("*")
        if p.is_file() and p.name != "manifest.json"
    }

    if presentes != set(arquivos):
        raise ValueError("Arquivos nao declarados no manifesto")

    return manifesto


def pasta_temporaria(destino):
    destino = Path(destino)
    destino.parent.mkdir(parents=True, exist_ok=True)

    return Path(tempfile.mkdtemp(
        prefix=".aula20_",
        dir=destino.parent,
    ))


def concluir_publicacao(temporaria, destino, camada):
    validar_camada(temporaria, camada)

    if destino.exists():
        validar_camada(destino, camada)
        return False

    os.rename(temporaria, destino)
    return True


def obter_snapshot(oltp, lake=LAKE):
    return ingerir(oltp, lake)


def criar_bronze_dominios(snapshot, lake=LAKE):
    """Exporta tabelas sem transformacao analitica."""
    snapshot = Path(snapshot)
    manifesto_raw = json.loads(
        (snapshot / "manifest.json").read_text(
            encoding="utf-8"
        )
    )

    validar_snapshot(snapshot)
    identificador = manifesto_raw["snapshot_id"]

    destino = (
        Path(lake) / "bronze_dominios"
        / "minishop" / identificador
    )

    if destino.exists():
        validar_camada(destino, "bronze")
        return {
            "pasta": str(destino),
            "novo": False,
            "snapshot_id": identificador,
        }

    temporaria = pasta_temporaria(destino)

    try:
        with closing(conectar_somente_leitura(
            snapshot / "oltp.sqlite"
        )) as con:
            for dominio, tabelas in DOMINIOS.items():
                for tabela in tabelas:
                    registros = [
                        dict(linha)
                        for linha in con.execute(
                            f'SELECT * FROM "{tabela}"'
                        ).fetchall()
                    ]

                    escrever_jsonl(
                        temporaria / dominio
                        / f"{tabela}.jsonl",
                        registros,
                    )

        publicar_manifesto(
            temporaria, "bronze", identificador
        )

        novo = concluir_publicacao(
            temporaria, destino, "bronze"
        )
    finally:
        if temporaria.exists():
            shutil.rmtree(temporaria)

    return {
        "pasta": str(destino),
        "novo": novo,
        "snapshot_id": identificador,
    }


def carregar_bronze(pasta):
    """Interpreta o conteudo preservado somente na leitura."""
    validar_camada(pasta, "bronze")

    dados = {}

    for dominio, tabelas in DOMINIOS.items():
        for tabela in tabelas:
            dados[tabela] = ler_jsonl(
                Path(pasta) / dominio / f"{tabela}.jsonl"
            )

    return dados


def gerar_formatos_binarios(pasta, vendas):
    """Cria formatos REAIS, quando houver dependencias."""
    formatos = {
        "parquet": False,
        "avro": False,
    }

    if not vendas:
        return formatos

    try:
        import pyarrow as pa
        import pyarrow.parquet as pq
    except ImportError:
        pass
    else:
        tabela = pa.Table.from_pylist(vendas)
        pq.write_table(
            tabela,
            Path(pasta) / "vendas.parquet",
            compression="snappy",
        )
        formatos["parquet"] = True

    try:
        from fastavro import writer, parse_schema
    except ImportError:
        pass
    else:
        campos = [
            {"name": nome, "type": tipo}
            for nome, tipo in (
                ("pedido_id", "long"),
                ("cliente_id", "long"),
                ("data", "string"),
                ("produto_id", "long"),
                ("quantidade", "long"),
                ("preco_unitario_centavos", "long"),
                ("valor_total_centavos", "long"),
            )
        ]

        esquema = parse_schema({
            "type": "record",
            "name": "VendaMinishopAula20",
            "fields": campos,
        })

        with (
            Path(pasta) / "vendas.avro"
        ).open("wb") as saida:
            writer(saida, esquema, vendas)

        formatos["avro"] = True

    return formatos


def preparar_silver(pasta_bronze, lake=LAKE):
    """Une dados, preserva informacoes ausentes e particiona."""
    dados = carregar_bronze(pasta_bronze)

    manifesto = validar_camada(
        pasta_bronze, "bronze"
    )
    identificador = manifesto["snapshot_id"]

    destino = (
        Path(lake) / "silver"
        / "minishop" / identificador
    )

    if destino.exists():
        validar_camada(destino, "silver")

        return {
            "pasta": str(destino),
            "novo": False,
            "snapshot_id": identificador,
        }

    categorias = {
        c["categoria_id"]: c
        for c in dados["categorias"]
    }

    produtos = {
        p["produto_id"]: p
        for p in dados["produtos"]
    }

    clientes = dados["clientes"]

    produto_categoria = []

    for produto in dados["produtos"]:
        categoria = categorias[produto["categoria_id"]]

        produto_categoria.append({
            "produto_id": produto["produto_id"],
            "produto_nome": produto["nome"],
            "categoria_id": categoria["categoria_id"],
            "categoria_nome": categoria["nome"],
        })

    pedidos = {
        p["pedido_id"]: p
        for p in dados["pedidos"]
    }

    pagos = {
        p["pedido_id"]
        for p in dados["pagamentos"]
        if p["estado"] == "aprovado"
    }

    vendas = []

    for item in dados["itens_pedido"]:
        pedido = pedidos[item["pedido_id"]]

        if (
            pedido["estado"] != "confirmado"
            or pedido["pedido_id"] not in pagos
        ):
            continue

        produto = produtos[item["produto_id"]]
        data = pedido["data_pedido"][:10]

        validar_periodo(data, data)

        if (
            item["quantidade"] <= 0
            or item["preco_unitario_centavos"] < 0
        ):
            raise ValueError("Item de venda invalido")

        vendas.append({
            "pedido_id": pedido["pedido_id"],
            "cliente_id": pedido["cliente_id"],
            "data": data,
            "produto_id": item["produto_id"],
            "produto_nome": produto["nome"],
            "quantidade": item["quantidade"],
            "preco_unitario_centavos":
                item["preco_unitario_centavos"],
            "valor_total_centavos":
                item["quantidade"]
                * item["preco_unitario_centavos"],
        })

    movimentos = []

    for movimento in dados["movimentos_estoque"]:
        if movimento["tipo"] != "saida":
            continue

        pedido = pedidos.get(movimento["pedido_id"])

        if (
            pedido is None
            or pedido["estado"] != "confirmado"
            or pedido["pedido_id"] not in pagos
        ):
            continue

        movimentos.append({
            "movimento_id": movimento["movimento_id"],
            "produto_id": movimento["produto_id"],
            "data": pedido["data_pedido"][:10],
            "quantidade": movimento["quantidade"],
        })

    temporaria = pasta_temporaria(destino)

    try:
        escrever_jsonl(
            temporaria / "clientes" / "clientes.jsonl",
            clientes,
        )

        escrever_jsonl(
            temporaria / "vendas"
            / "produto_categoria.jsonl",
            produto_categoria,
        )

        escrever_jsonl(
            temporaria / "logistica"
            / "movimentos.jsonl",
            movimentos,
        )

        escrever_jsonl(
            temporaria / "financeiro"
            / "faturas.jsonl",
            dados["faturas"],
        )

        por_mes = defaultdict(list)

        for venda in vendas:
            por_mes[venda["data"][:7]].append(venda)

        for periodo, linhas in por_mes.items():
            ano, mes = periodo.split("-")

            escrever_jsonl(
                temporaria / "vendas"
                / f"ano={ano}" / f"mes={mes}"
                / "vendas.jsonl",
                linhas,
            )

        formatos = gerar_formatos_binarios(
            temporaria, vendas
        )

        (temporaria / "formatos.json").write_text(
            json.dumps(formatos, indent=2),
            encoding="utf-8",
        )

        publicar_manifesto(
            temporaria, "silver", identificador
        )

        novo = concluir_publicacao(
            temporaria, destino, "silver"
        )
    finally:
        if temporaria.exists():
            shutil.rmtree(temporaria)

    return {
        "pasta": str(destino),
        "novo": novo,
        "snapshot_id": identificador,
    }


def ler_silver(pasta):
    """Le apenas arquivos Silver, sem retornar a Bronze."""
    pasta = Path(pasta)
    validar_camada(pasta, "silver")

    vendas = []

    for arquivo in sorted(
        (pasta / "vendas").glob(
            "ano=*/mes=*/vendas.jsonl"
        )
    ):
        vendas.extend(ler_jsonl(arquivo))

    return {
        "clientes": ler_jsonl(
            pasta / "clientes" / "clientes.jsonl"
        ),
        "produtos": ler_jsonl(
            pasta / "vendas" / "produto_categoria.jsonl"
        ),
        "vendas": vendas,
        "movimentos": ler_jsonl(
            pasta / "logistica" / "movimentos.jsonl"
        ),
        "faturas": ler_jsonl(
            pasta / "financeiro" / "faturas.jsonl"
        ),
    }


def criar_gold_mensal(pasta_silver, lake=LAKE):
    dados = ler_silver(pasta_silver)
    manifesto = validar_camada(pasta_silver, "silver")
    identificador = manifesto["snapshot_id"]

    destino = (
        Path(lake) / "gold_mensal"
        / "minishop" / identificador
    )

    if destino.exists():
        validar_camada(destino, "gold")
        return {
            "pasta": str(destino),
            "novo": False,
            "snapshot_id": identificador,
        }

    totais = defaultdict(
        lambda: {
            "pedidos": set(),
            "itens": 0,
            "unidades": 0,
            "faturamento_centavos": 0,
        }
    )

    for venda in dados["vendas"]:
        periodo = venda["data"][:7]
        linha = totais[periodo]

        linha["pedidos"].add(venda["pedido_id"])
        linha["itens"] += 1
        linha["unidades"] += venda["quantidade"]
        linha["faturamento_centavos"] += (
            venda["valor_total_centavos"]
        )

    registros = [
        {
            "periodo": periodo,
            "pedidos": len(valores["pedidos"]),
            "itens": valores["itens"],
            "unidades": valores["unidades"],
            "faturamento_centavos":
                valores["faturamento_centavos"],
        }
        for periodo, valores in sorted(totais.items())
    ]

    temporaria = pasta_temporaria(destino)

    try:
        escrever_jsonl(
            temporaria / "indicadores_mensais.jsonl",
            registros,
        )

        publicar_manifesto(
            temporaria, "gold", identificador
        )

        novo = concluir_publicacao(
            temporaria, destino, "gold"
        )
    finally:
        if temporaria.exists():
            shutil.rmtree(temporaria)

    return {
        "pasta": str(destino),
        "novo": novo,
        "snapshot_id": identificador,
    }


def carregar_dw_da_silver(
    pasta_silver, destino_dw, inicio, fim
):
    """Carrega DW com fonte EXCLUSIVAMENTE Silver."""
    validar_periodo(inicio, fim)

    dados = ler_silver(pasta_silver)

    filtrados = {
        "clientes": dados["clientes"],
        "produtos": dados["produtos"],
        "vendas": [
            {
                campo: venda[campo]
                for campo in (
                    "pedido_id", "cliente_id",
                    "produto_id", "data",
                    "quantidade",
                    "preco_unitario_centavos",
                    "valor_total_centavos",
                )
            }
            for venda in dados["vendas"]
            if inicio <= venda["data"] <= fim
        ],
        "movimentos": [
            movimento
            for movimento in dados["movimentos"]
            if inicio <= movimento["data"] <= fim
        ],
    }

    preparar_dw(destino_dw)

    with closing(conectar(destino_dw)) as con:
        try:
            con.execute("BEGIN IMMEDIATE")

            carregar_dimensoes(
                con, filtrados, inicio, fim
            )

            carga = carregar_fatos(
                con, filtrados, inicio, fim
            )

            con.execute(
                """
                INSERT INTO etl_execucoes
                (inicio, fim, executado_em,
                 vendas_carregadas, movimentos_carregados,
                 faturamento_centavos)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    inicio,
                    fim,
                    datetime.now(timezone.utc).isoformat(),
                    carga["vendas"],
                    carga["inventario"],
                    carga["faturamento_centavos"],
                ),
            )

            con.commit()
        except Exception:
            con.rollback()
            raise

    return {
        "carga": carga,
        "indicadores": indicadores(destino_dw),
    }


def executar(oltp, lake, dw):
    """Executa as etapas, mantendo fontes separadas."""
    snapshot = obter_snapshot(oltp, lake)
    bronze = criar_bronze_dominios(
        snapshot["pasta"], lake
    )
    silver = preparar_silver(bronze["pasta"], lake)
    gold = criar_gold_mensal(silver["pasta"], lake)

    dados = ler_silver(silver["pasta"])

    if not dados["vendas"]:
        raise ValueError(
            "Snapshot sem vendas para demonstrar o DW"
        )

    datas = [
        venda["data"]
        for venda in dados["vendas"]
    ]

    resultado_dw = carregar_dw_da_silver(
        silver["pasta"],
        dw,
        min(datas),
        max(datas),
    )

    return {
        "snapshot": snapshot,
        "bronze": bronze,
        "silver": silver,
        "gold": gold,
        "dw": resultado_dw,
    }
