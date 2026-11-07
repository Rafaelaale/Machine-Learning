"""Aula 28 - Governanca de dados na Minishop.

Tres pilares:
1. Catalogo: inventario de datasets e metricas.
2. Linhagem: caminho documentado das transformacoes.
3. Qualidade: validacoes com evidencia e reconciliacao.

Trabalha sobre a arquitetura da Aula 25 e
as definicoes semanticas da Aula 26.

Nao altera as tabelas de origem.
"""

import json
import sqlite3

from collections import Counter
from contextlib import closing
from pathlib import Path

from src.aula25_lakehouse_minishop import (
    executar as executar_arquitetura,
    validar_gold_analitica,
    consultar_lakehouse,
    indicadores_lakehouse,
    indicadores_dw,
)
from src.aula26_camada_semantica import (
    METRICAS,
    DIMENSOES,
    comparar_fontes,
)
from src.aula17_data_lake import hash_arquivo
from src.aula20_data_lake_minishop import validar_camada


TABELAS_DW = (
    "dim_cliente",
    "dim_produto",
    "dim_tempo",
    "fato_vendas",
)

CAMPOS_OBRIGATORIOS_VENDA = (
    "pedido_id",
    "cliente_id",
    "cliente_nome",
    "produto_id",
    "produto_nome",
    "categoria_nome",
    "data",
    "quantidade",
    "valor_total_centavos",
)


def conexao_leitura(banco):
    """Abre SQLite em modo de somente leitura."""
    caminho = Path(banco).resolve()

    if not caminho.is_file():
        raise FileNotFoundError(caminho)

    return sqlite3.connect(
        caminho.as_uri() + "?mode=ro",
        uri=True,
    )


def catalogar_dw(banco):
    """Extrai metadados reais do schema SQLite."""
    tabelas = {}

    with closing(conexao_leitura(banco)) as con:
        for nome in TABELAS_DW:
            if nome not in {
                linha[0] for linha in con.execute(
                    """
                    SELECT name FROM sqlite_master
                    WHERE type = 'table'
                    """
                )
            }:
                raise ValueError(
                    "Tabela dimensional nao encontrada: " + nome
                )

            colunas = con.execute(
                f"PRAGMA table_info('{nome}')"
            ).fetchall()

            estrangeiras = con.execute(
                f"PRAGMA foreign_key_list('{nome}')"
            ).fetchall()

            total = con.execute(
                f'SELECT COUNT(*) FROM "{nome}"'
            ).fetchone()[0]

            tabelas[nome] = {
                "tipo": "tabela_dimensional"
                    if nome.startswith("dim_")
                    else "tabela_fato",
                "linhas": total,
                "colunas": [
                    {
                        "nome": coluna[1],
                        "tipo": coluna[2],
                        "obrigatorio": bool(coluna[3])
                            or bool(coluna[5]),
                        "chave_primaria": bool(coluna[5]),
                    }
                    for coluna in colunas
                ],
                "chaves_estrangeiras": [
                    {
                        "coluna": fk[3],
                        "tabela_referenciada": fk[2],
                        "coluna_referenciada": fk[4],
                    }
                    for fk in estrangeiras
                ],
            }

    return tabelas


def catalogar_gold(pasta):
    """Relaciona as tabelas Parquet e os metadados da Gold."""
    catalogo = validar_gold_analitica(pasta)

    return {
        "snapshot_id": catalogo["snapshot_id"],
        "formato": "Parquet",
        "tabelas": catalogo["tabelas"],
        "caminho": str(Path(pasta).resolve()),
    }


def criar_catalogo(pasta_gold, banco_dw):
    """Inventario das fontes fisicas e metricas de negocio."""
    return {
        "versao": "1.0",
        "plataforma": "Minishop",
        "responsavel_datasets": "nao_definido",
        "lakehouse": catalogar_gold(pasta_gold),
        "data_warehouse": {
            "tipo": "SQLite",
            "caminho": str(Path(banco_dw).resolve()),
            "tabelas": catalogar_dw(banco_dw),
        },
        "camada_semantica": {
            "metricas": METRICAS,
            "dimensoes": DIMENSOES,
        },
        "documentacao": {
            "responsavel_datasets": (
                "Deve ser atribuido pela organizacao"
            ),
            "faturamento": (
                "Soma dos valores das vendas. "
                "Valores armazenados em centavos."
            ),
            "ticket_medio": (
                "Faturamento dividido por pedidos distintos."
            ),
        },
    }


def criar_linhagem(arquitetura):
    """Documenta transformacoes implementadas nas aulas.

    A linhagem e declarativa: representa o codigo estudado,
    nao e uma descoberta automatica em tempo de execucao.
    """
    nos = {
        "oltp": arquitetura["oltp"],
        "bronze": arquitetura["bronze"],
        "silver": arquitetura["silver"],
        "gold": arquitetura["gold_analitica"],
        "lakehouse": arquitetura["lakehouse_catalogo"],
        "dw": arquitetura["data_warehouse"],
        "semantica": "src.aula26_camada_semantica",
        "consumo": "src.aula27_consumo_semantico",
    }

    etapas = [
        {
            "origem": "oltp",
            "destino": "bronze",
            "operacao": "Extracao e preservacao de snapshot",
        },
        {
            "origem": "bronze",
            "destino": "silver",
            "operacao": "Tratamento e padronizacao",
        },
        {
            "origem": "silver",
            "destino": "gold",
            "operacao": (
                "Enriquecimento de vendas com "
                "cliente, produto e categoria"
            ),
        },
        {
            "origem": "gold",
            "destino": "lakehouse",
            "operacao": (
                "Catalogo e consultas SQL "
                "sobre os mesmos arquivos Parquet"
            ),
        },
        {
            "origem": "silver",
            "destino": "dw",
            "operacao": (
                "ETL para dimensoes e fato de vendas"
            ),
        },
        {
            "origem": "lakehouse",
            "destino": "semantica",
            "operacao": "Metricas oficiais sobre Parquet",
        },
        {
            "origem": "dw",
            "destino": "semantica",
            "operacao": "Metricas oficiais sobre fato e dimensoes",
        },
        {
            "origem": "semantica",
            "destino": "consumo",
            "operacao": "Indicadores padronizados para analistas",
        },
    ]

    return {
        "snapshot_id": arquitetura["snapshot_id"],
        "tipo": "declarativa_documentada",
        "nos": nos,
        "etapas": etapas,
        "metrica_faturamento": {
            "origem_operacional": (
                "Pedidos e itens de pedido "
                "confirmados no OLTP"
            ),
            "lakehouse": (
                "Gold analitica: "
                "vendas_enriquecidas.valor_total_centavos"
            ),
            "dw": (
                "fato_vendas.valor_total_centavos"
            ),
            "regra": "SUM(valor_total_centavos)",
            "unidade": "centavos",
        },
    }


def caminho_linhagem(linhagem, inicio, destino):
    """Encontra percurso dirigido entre dois componentes."""
    if inicio not in linhagem["nos"]:
        raise ValueError("Origem desconhecida")

    if destino not in linhagem["nos"]:
        raise ValueError("Destino desconhecido")

    adjacencias = {}

    for etapa in linhagem["etapas"]:
        adjacencias.setdefault(
            etapa["origem"], []
        ).append(etapa["destino"])

    fila = [[inicio]]
    visitados = set()

    while fila:
        caminho = fila.pop(0)
        atual = caminho[-1]

        if atual == destino:
            return caminho

        if atual in visitados:
            continue

        visitados.add(atual)

        for proximo in adjacencias.get(atual, []):
            if proximo not in visitados:
                fila.append(caminho + [proximo])

    return []


def validar_registros_vendas(registros):
    """Regras de qualidade sobre linhas analiticas.

    Retorna erros em vez de gravar registros invalidos.
    """
    erros = []
    chaves = set()

    for indice, registro in enumerate(registros, 1):
        ausentes = [
            campo
            for campo in CAMPOS_OBRIGATORIOS_VENDA
            if campo not in registro
            or registro[campo] is None
            or (
                isinstance(registro[campo], str)
                and not registro[campo].strip()
            )
        ]

        if ausentes:
            erros.append({
                "linha": indice,
                "regra": "campos_obrigatorios",
                "campos": ausentes,
            })
            continue

        chave = (
            registro["pedido_id"],
            registro["produto_id"],
        )

        if chave in chaves:
            erros.append({
                "linha": indice,
                "regra": "duplicidade",
                "chave": list(chave),
            })

        chaves.add(chave)

        for campo in (
            "pedido_id",
            "cliente_id",
            "produto_id",
            "quantidade",
            "valor_total_centavos",
        ):
            valor = registro[campo]

            if type(valor) is not int or (
                valor <= 0
                if campo != "valor_total_centavos"
                else valor < 0
            ):
                erros.append({
                    "linha": indice,
                    "regra": "medida_invalida",
                    "campo": campo,
                })

        data = registro["data"]

        try:
            from datetime import date
            if date.fromisoformat(data).isoformat() != data:
                raise ValueError()
        except (ValueError, TypeError):
            erros.append({
                "linha": indice,
                "regra": "data_invalida",
            })

    return {
        "linhas": len(registros),
        "aprovado": not erros,
        "erros": erros,
    }


def consultar_vendas_gold(pasta):
    """Le as linhas Gold usando a consulta da Aula 25."""
    return consultar_lakehouse(
        pasta,
        """
        SELECT
            pedido_id,
            cliente_id,
            cliente_nome,
            produto_id,
            produto_nome,
            categoria_nome,
            data,
            quantidade,
            valor_total_centavos
        FROM vendas_enriquecidas
        ORDER BY pedido_id, produto_id
        """,
    )


def verificar_referencias_dw(banco):
    """Verifica integridade referencial real do SQLite."""
    with closing(conexao_leitura(banco)) as con:
        erros_fk = con.execute(
            "PRAGMA foreign_key_check"
        ).fetchall()

        duplicidades = con.execute(
            """
            SELECT pedido_id, sk_produto, COUNT(*)
            FROM fato_vendas
            GROUP BY pedido_id, sk_produto
            HAVING COUNT(*) > 1
            """
        ).fetchall()

        medidas_invalidas = con.execute(
            """
            SELECT COUNT(*)
            FROM fato_vendas
            WHERE quantidade <= 0
               OR valor_total_centavos < 0
            """
        ).fetchone()[0]

    return {
        "referencias_validas": len(erros_fk) == 0,
        "duplicidades": len(duplicidades),
        "medidas_invalidas": medidas_invalidas,
        "aprovado": (
            not erros_fk
            and not duplicidades
            and medidas_invalidas == 0
        ),
    }


def auditar_qualidade(arquitetura):
    """Auditoria de integridade, regras e reconciliacao."""
    pasta = Path(arquitetura["gold_analitica"])
    dw = Path(arquitetura["data_warehouse"])

    validar_camada(arquitetura["silver"], "silver")
    validar_gold_analitica(pasta)

    vendas = consultar_vendas_gold(pasta)
    regras = validar_registros_vendas(vendas)
    referencias = verificar_referencias_dw(dw)

    gold_total = indicadores_lakehouse(pasta)
    dw_total = indicadores_dw(dw)

    metricas_iguais = gold_total == dw_total

    faturamento = comparar_fontes(
        "faturamento", pasta, dw
    )

    ticket = comparar_fontes(
        "ticket_medio", pasta, dw
    )

    aprovado = all((
        regras["aprovado"],
        referencias["aprovado"],
        metricas_iguais,
        faturamento["iguais"],
        ticket["iguais"],
    ))

    return {
        "snapshot_id": arquitetura["snapshot_id"],
        "linhas_verificadas": len(vendas),
        "regras": regras,
        "referencias_dw": referencias,
        "reconciliacao": {
            "lakehouse": gold_total,
            "data_warehouse": dw_total,
            "iguais": metricas_iguais,
        },
        "metricas_semanticas": {
            "faturamento_igual": faturamento["iguais"],
            "ticket_medio_igual": ticket["iguais"],
        },
        "aprovado": aprovado,
    }


def assinaturas_origens(arquitetura):
    """Hashes para conferir preservacao do dado analitico."""
    gold = Path(arquitetura["gold_analitica"])
    dw = Path(arquitetura["data_warehouse"])

    arquivos = sorted(gold.glob("*.parquet")) + [dw]

    return {
        str(arquivo): hash_arquivo(arquivo)
        for arquivo in arquivos
    }


def executar(oltp, lake):
    """Executa auditoria transversal na arquitetura integrada."""
    arquitetura = executar_arquitetura(oltp, lake)

    antes = assinaturas_origens(arquitetura)

    catalogo = criar_catalogo(
        arquitetura["gold_analitica"],
        arquitetura["data_warehouse"],
    )

    linhagem = criar_linhagem(arquitetura)

    qualidade = auditar_qualidade(arquitetura)

    depois = assinaturas_origens(arquitetura)

    preservados = antes == depois

    if not qualidade["aprovado"]:
        raise ValueError(
            "Governanca detectou inconsistencias de qualidade"
        )

    if not preservados:
        raise ValueError(
            "Arquivos analiticos foram modificados"
        )

    return {
        "snapshot_id": arquitetura["snapshot_id"],
        "catalogo": catalogo,
        "linhagem": linhagem,
        "qualidade": qualidade,
        "dados_preservados": preservados,
        "caminho_faturamento": caminho_linhagem(
            linhagem, "oltp", "consumo"
        ),
    }
