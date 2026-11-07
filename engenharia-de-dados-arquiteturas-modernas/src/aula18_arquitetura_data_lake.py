"""Aula 18 - Arquitetura do Data Lake Minishop.

Bronze: snapshots preservados pela Aula 17.
Silver: vendas validadas e padronizadas.
Gold: indicadores analiticos por data e produto.

Cada camada derivada possui manifesto com hashes SHA-256.

O processamento Gold depende apenas da Silver.
O processamento Silver depende apenas da Bronze.
"""

import csv
import json
import os
import shutil
import tempfile
from collections import defaultdict
from datetime import date, datetime, timezone
from pathlib import Path

from src.aula17_data_lake import (
    LAKE,
    ingerir,
    validar_snapshot,
    extrair_vendas_do_snapshot,
    hash_arquivo,
)


COLUNAS_VENDAS = (
    "pedido_id",
    "cliente_id",
    "data",
    "produto_id",
    "produto",
    "quantidade",
    "preco_unitario_centavos",
    "valor_centavos",
)

COLUNAS_DIAS = (
    "data",
    "itens",
    "unidades",
    "faturamento_centavos",
)

COLUNAS_PRODUTOS = (
    "produto_id",
    "produto",
    "itens",
    "unidades",
    "faturamento_centavos",
)


def escrever_json(caminho, dados):
    Path(caminho).write_text(
        json.dumps(
            dados,
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        ) + "\n",
        encoding="utf-8",
    )


def escrever_jsonl(caminho, registros):
    with open(
        caminho, "w", encoding="utf-8", newline=""
    ) as arquivo:
        for registro in registros:
            arquivo.write(
                json.dumps(
                    registro,
                    sort_keys=True,
                    ensure_ascii=False,
                ) + "\n"
            )


def escrever_csv(caminho, registros, colunas):
    with open(
        caminho, "w", encoding="utf-8", newline=""
    ) as arquivo:
        escritor = csv.DictWriter(
            arquivo,
            fieldnames=colunas,
            extrasaction="raise",
        )
        escritor.writeheader()
        escritor.writerows(registros)


def ler_jsonl(caminho):
    registros = []

    with open(
        caminho, "r", encoding="utf-8"
    ) as arquivo:
        for numero, texto in enumerate(arquivo, 1):
            if not texto.strip():
                continue

            try:
                registro = json.loads(texto)
            except json.JSONDecodeError as erro:
                raise ValueError(
                    f"JSONL invalido na linha {numero}"
                ) from erro

            if not isinstance(registro, dict):
                raise ValueError(
                    "Registro JSONL nao e objeto"
                )

            registros.append(registro)

    return registros


def validar_venda(registro):
    """Schema on Read: valida campos ao consumir Bronze."""
    if not isinstance(registro, dict):
        raise ValueError("Venda nao e objeto")

    if not set(COLUNAS_VENDAS).issubset(registro):
        raise ValueError("Campos obrigatorios ausentes")

    for campo in (
        "pedido_id",
        "cliente_id",
        "produto_id",
        "quantidade",
        "preco_unitario_centavos",
        "valor_centavos",
    ):
        if type(registro[campo]) is not int:
            raise ValueError(f"Tipo invalido: {campo}")

    if (
        registro["pedido_id"] <= 0
        or registro["cliente_id"] <= 0
        or registro["produto_id"] <= 0
        or registro["quantidade"] <= 0
        or registro["preco_unitario_centavos"] < 0
    ):
        raise ValueError("Medidas ou IDs invalidos")

    valor_calculado = (
        registro["quantidade"]
        * registro["preco_unitario_centavos"]
    )

    if registro["valor_centavos"] != valor_calculado:
        raise ValueError("Valor da venda inconsistente")

    if (
        not isinstance(registro["produto"], str)
        or not registro["produto"].strip()
    ):
        raise ValueError("Nome do produto invalido")

    data_texto = registro["data"]

    if not isinstance(data_texto, str):
        raise ValueError("Data invalida")

    try:
        data = date.fromisoformat(data_texto)
    except ValueError as erro:
        raise ValueError("Data invalida") from erro

    if data.isoformat() != data_texto:
        raise ValueError("Formato de data invalido")

    return {
        "pedido_id": registro["pedido_id"],
        "cliente_id": registro["cliente_id"],
        "data": data_texto,
        "produto_id": registro["produto_id"],
        "produto": registro["produto"].strip(),
        "quantidade": registro["quantidade"],
        "preco_unitario_centavos": (
            registro["preco_unitario_centavos"]
        ),
        "valor_centavos": registro["valor_centavos"],
    }


def validar_camada(pasta, nome_camada):
    """Verifica integridade dos arquivos produzidos."""
    pasta = Path(pasta)
    arquivo_manifesto = pasta / "manifest.json"

    if not arquivo_manifesto.is_file():
        raise ValueError("Manifesto inexistente")

    manifesto = json.loads(
        arquivo_manifesto.read_text(encoding="utf-8")
    )

    if manifesto.get("camada") != nome_camada:
        raise ValueError("Camada divergente")

    arquivos = manifesto.get("arquivos")

    if not isinstance(arquivos, dict) or not arquivos:
        raise ValueError("Lista de arquivos invalida")

    for nome, hash_esperado in arquivos.items():
        if (
            not isinstance(nome, str)
            or Path(nome).name != nome
        ):
            raise ValueError("Nome de arquivo invalido")

        arquivo = pasta / nome

        if not arquivo.is_file():
            raise ValueError(f"Arquivo ausente: {nome}")

        if hash_arquivo(arquivo) != hash_esperado:
            raise ValueError(
                f"Integridade comprometida: {nome}"
            )

    return manifesto


def gravar_manifesto(
    pasta, camada, snapshot_id, nomes, origem
):
    arquivos = {
        nome: hash_arquivo(Path(pasta) / nome)
        for nome in nomes
    }

    manifesto = {
        "dataset": "minishop",
        "camada": camada,
        "snapshot_id": snapshot_id,
        "origem_logica": origem,
        "gerado_em_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "arquivos": arquivos,
    }

    escrever_json(
        Path(pasta) / "manifest.json",
        manifesto,
    )


def criar_pasta_temporaria(destino):
    destino = Path(destino)
    destino.parent.mkdir(
        parents=True, exist_ok=True
    )

    return Path(
        tempfile.mkdtemp(
            prefix=".aula18_",
            dir=destino.parent,
        )
    )


def publicar_camada(temporaria, destino, nome_camada):
    """Publica uma nova camada sem substituir a anterior."""
    validar_camada(
        temporaria, nome_camada
    )

    if destino.exists():
        validar_camada(destino, nome_camada)
        return False

    os.rename(temporaria, destino)
    return True


def criar_silver(pasta_bronze, lake=LAKE):
    """Transforma Bronze em Silver sem alterar dados brutos."""
    pasta_bronze = Path(pasta_bronze)

    validar_snapshot(pasta_bronze)

    manifesto_raw = json.loads(
        (pasta_bronze / "manifest.json").read_text(
            encoding="utf-8"
        )
    )

    snapshot_id = manifesto_raw["snapshot_id"]

    destino = (
        Path(lake)
        / "staged"
        / "minishop"
        / snapshot_id
    )

    if destino.exists():
        validar_camada(destino, "silver")
        return {
            "pasta": str(destino),
            "snapshot_id": snapshot_id,
            "novo": False,
        }

    # Esta etapa le os dados RAW e aplica um esquema
    # apenas agora, no momento do processamento.
    brutos = extrair_vendas_do_snapshot(
        pasta_bronze
    )

    padronizados = [
        validar_venda(item)
        for item in brutos
    ]

    identificadores = set()

    for item in padronizados:
        chave = (
            item["pedido_id"],
            item["produto_id"],
        )

        if chave in identificadores:
            raise ValueError(
                "Produto duplicado no mesmo pedido"
            )

        identificadores.add(chave)

    temporaria = criar_pasta_temporaria(destino)

    try:
        escrever_jsonl(
            temporaria / "vendas_padronizadas.jsonl",
            padronizados,
        )

        escrever_csv(
            temporaria / "vendas_padronizadas.csv",
            padronizados,
            COLUNAS_VENDAS,
        )

        gravar_manifesto(
            temporaria,
            "silver",
            snapshot_id,
            (
                "vendas_padronizadas.jsonl",
                "vendas_padronizadas.csv",
            ),
            "bronze/minishop/" + snapshot_id,
        )

        novo = publicar_camada(
            temporaria, destino, "silver"
        )

    finally:
        if temporaria.exists():
            shutil.rmtree(temporaria)

    return {
        "pasta": str(destino),
        "snapshot_id": snapshot_id,
        "novo": novo,
    }


def ler_silver(pasta):
    """Le a camada padronizada, conferindo seu esquema."""
    validar_camada(pasta, "silver")

    registros = ler_jsonl(
        Path(pasta) / "vendas_padronizadas.jsonl"
    )

    return [
        validar_venda(item)
        for item in registros
    ]


def indicadores_gold(vendas):
    """Agrupa vendas padronizadas por dia e por produto."""
    por_dia = defaultdict(
        lambda: {
            "itens": 0,
            "unidades": 0,
            "faturamento_centavos": 0,
        }
    )

    por_produto = defaultdict(
        lambda: {
            "produto": "",
            "itens": 0,
            "unidades": 0,
            "faturamento_centavos": 0,
        }
    )

    for venda in vendas:
        dia = por_dia[venda["data"]]
        dia["itens"] += 1
        dia["unidades"] += venda["quantidade"]
        dia["faturamento_centavos"] += (
            venda["valor_centavos"]
        )

        produto = por_produto[
            venda["produto_id"]
        ]

        produto["produto"] = venda["produto"]
        produto["itens"] += 1
        produto["unidades"] += venda["quantidade"]
        produto["faturamento_centavos"] += (
            venda["valor_centavos"]
        )

    diarios = [
        {
            "data": data,
            **valores,
        }
        for data, valores in sorted(
            por_dia.items()
        )
    ]

    produtos = [
        {
            "produto_id": codigo,
            **valores,
        }
        for codigo, valores in sorted(
            por_produto.items()
        )
    ]

    resumo = {
        "linhas_vendas": len(vendas),
        "unidades": sum(
            venda["quantidade"]
            for venda in vendas
        ),
        "faturamento_centavos": sum(
            venda["valor_centavos"]
            for venda in vendas
        ),
        "dias_com_vendas": len(diarios),
        "produtos_distintos": len(produtos),
    }

    return resumo, diarios, produtos


def criar_gold(pasta_silver, lake=LAKE):
    """Gera Gold exclusivamente a partir de Silver."""
    pasta_silver = Path(pasta_silver)

    manifesto_silver = validar_camada(
        pasta_silver, "silver"
    )

    snapshot_id = manifesto_silver["snapshot_id"]

    destino = (
        Path(lake)
        / "gold"
        / "minishop"
        / snapshot_id
    )

    if destino.exists():
        validar_camada(destino, "gold")

        resumo = json.loads(
            (destino / "resumo.json").read_text(
                encoding="utf-8"
            )
        )

        return {
            "pasta": str(destino),
            "snapshot_id": snapshot_id,
            "novo": False,
            "resumo": resumo,
        }

    vendas = ler_silver(pasta_silver)

    resumo, diarios, produtos = indicadores_gold(
        vendas
    )

    temporaria = criar_pasta_temporaria(destino)

    try:
        escrever_json(
            temporaria / "resumo.json",
            resumo,
        )

        escrever_csv(
            temporaria / "faturamento_diario.csv",
            diarios,
            COLUNAS_DIAS,
        )

        escrever_csv(
            temporaria / "faturamento_produtos.csv",
            produtos,
            COLUNAS_PRODUTOS,
        )

        gravar_manifesto(
            temporaria,
            "gold",
            snapshot_id,
            (
                "resumo.json",
                "faturamento_diario.csv",
                "faturamento_produtos.csv",
            ),
            "silver/minishop/" + snapshot_id,
        )

        novo = publicar_camada(
            temporaria, destino, "gold"
        )

    finally:
        if temporaria.exists():
            shutil.rmtree(temporaria)

    return {
        "pasta": str(destino),
        "snapshot_id": snapshot_id,
        "novo": novo,
        "resumo": resumo,
    }


def executar_arquitetura(oltp, lake=LAKE):
    """Executa Bronze -> Silver -> Gold."""
    bronze = ingerir(oltp, lake)

    silver = criar_silver(
        bronze["pasta"], lake
    )

    gold = criar_gold(
        silver["pasta"], lake
    )

    return {
        "bronze": bronze,
        "silver": silver,
        "gold": gold,
    }
